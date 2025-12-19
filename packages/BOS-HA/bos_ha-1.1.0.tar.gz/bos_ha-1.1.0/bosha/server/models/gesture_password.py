import numpy as np
from typing import Dict, Any, List, Optional
from .yolov8_hand_detector import YOLOv8HandDetector
from .hand_pose_estimator import HandPoseEstimator

class GesturePasswordAuthenticator:
    """手势密码认证模块"""
    
    def __init__(self, yolov8_model_path: str, pose_model_path: str):
        """
        初始化手势密码认证模块
        
        Args:
            yolov8_model_path: YOLOv8模型路径
            pose_model_path: 人体姿态估计模型路径
        """
        # 初始化手部检测和关键点提取模块
        self.hand_detector = YOLOv8HandDetector(yolov8_model_path)
        self.pose_estimator = HandPoseEstimator(pose_model_path)
        
        # 预设手势密码库
        self.registered_gestures = {
            "user1": [
                # 手势密码序列：食指指向上 → 食指指向右 → 食指指向下 → 食指指向左（正方形）
                "up", "right", "down", "left"
            ],
            "admin": [
                # 手势密码序列：食指向上 → 中指向上 → 无名指向上 → 小指向上（四指上）
                "up", "up", "up", "up"
            ]
        }
        
        # 手势定义
        self.gesture_definitions = {
            "up": {"type": "direction", "threshold": 0.6},
            "down": {"type": "direction", "threshold": 0.6},
            "left": {"type": "direction", "threshold": 0.6},
            "right": {"type": "direction", "threshold": 0.6},
            "open": {"type": "fingers", "threshold": 0.8},
            "close": {"type": "fingers", "threshold": 0.8}
        }
        
        # 认证状态
        self.authentication_buffer = []
        self.max_buffer_length = 5  # 最大手势序列长度
        self.confidence_threshold = 0.7
    
    def detect_gesture_direction(self, keypoints: List[Dict[str, float]]) -> Optional[str]:
        """
        检测手势方向
        
        Args:
            keypoints: 手部关键点列表
            
        Returns:
            str: 手势方向（up, down, left, right）或 None
        """
        if len(keypoints) < 5:
            return None
        
        try:
            # 计算食指方向
            index_finger_tip = np.array([keypoints[8]["x"], keypoints[8]["y"]])
            index_finger_base = np.array([keypoints[7]["x"], keypoints[7]["y"]])
            direction = index_finger_tip - index_finger_base
            
            # 计算方向向量的大小
            direction_magnitude = np.linalg.norm(direction)
            if direction_magnitude < 10:  # 方向变化太小
                return None
            
            # 归一化方向向量
            direction_normalized = direction / direction_magnitude
            
            # 检测主方向
            if abs(direction_normalized[1]) > abs(direction_normalized[0]):
                # 垂直方向
                if direction_normalized[1] < -0.6:
                    return "up"
                elif direction_normalized[1] > 0.6:
                    return "down"
            else:
                # 水平方向
                if direction_normalized[0] > 0.6:
                    return "right"
                elif direction_normalized[0] < -0.6:
                    return "left"
            
            return None
            
        except Exception as e:
            print(f"❌ 检测手势方向失败: {e}")
            return None
    
    def detect_gesture(self, image: np.ndarray) -> Dict[str, Any]:
        """
        检测手势
        
        Args:
            image: 输入图像
            
        Returns:
            dict: 手势检测结果
        """
        try:
            # 手部检测
            hand_result = self.hand_detector.detect_hand(image)
            if not hand_result:
                return {
                    "success": False,
                    "message": "未检测到手部",
                    "gesture": None,
                    "confidence": 0.0
                }
            
            # 关键点提取
            keypoint_result = self.pose_estimator.extract_hand_keypoints(image)
            if not keypoint_result or not keypoint_result["has_hand"]:
                return {
                    "success": False,
                    "message": "未提取到手部关键点",
                    "gesture": None,
                    "confidence": 0.0
                }
            
            # 检测手势方向
            gesture = self.detect_gesture_direction(keypoint_result["hand_keypoints"])
            
            return {
                "success": True,
                "message": "手势检测成功",
                "gesture": gesture,
                "confidence": keypoint_result["confidence"],
                "keypoints": keypoint_result["hand_keypoints"]
            }
            
        except Exception as e:
            print(f"❌ 检测手势失败: {e}")
            return {
                "success": False,
                "message": f"手势检测失败: {str(e)}",
                "gesture": None,
                "confidence": 0.0
            }
    
    def authenticate_gesture_password(self, image: np.ndarray, user_id: str) -> Dict[str, Any]:
        """
        手势密码认证
        
        Args:
            image: 输入图像
            user_id: 用户ID
            
        Returns:
            dict: 认证结果
        """
        try:
            # 检查用户是否已注册
            if user_id not in self.registered_gestures:
                return {
                    "success": False,
                    "message": f"用户 {user_id} 未注册",
                    "is_authenticated": False,
                    "gesture": None,
                    "confidence": 0.0
                }
            
            # 检测手势
            gesture_result = self.detect_gesture(image)
            if not gesture_result["success"] or not gesture_result["gesture"]:
                return {
                    "success": False,
                    "message": gesture_result["message"],
                    "is_authenticated": False,
                    "gesture": None,
                    "confidence": 0.0
                }
            
            # 添加到认证缓冲区
            gesture = gesture_result["gesture"]
            confidence = gesture_result["confidence"]
            
            if confidence >= self.confidence_threshold:
                self.authentication_buffer.append(gesture)
                
                # 保持缓冲区长度
                if len(self.authentication_buffer) > self.max_buffer_length:
                    self.authentication_buffer = self.authentication_buffer[-self.max_buffer_length:]
            
            # 检查是否匹配预设手势密码
            expected_gestures = self.registered_gestures[user_id]
            buffer_len = len(self.authentication_buffer)
            expected_len = len(expected_gestures)
            
            if buffer_len >= expected_len:
                # 检查最近的expected_len个手势是否匹配
                recent_gestures = self.authentication_buffer[-expected_len:]
                is_match = recent_gestures == expected_gestures
                
                if is_match:
                    # 认证成功，清空缓冲区
                    self.authentication_buffer = []
                    return {
                        "success": True,
                        "message": "手势密码认证成功",
                        "is_authenticated": True,
                        "gesture": gesture,
                        "confidence": confidence,
                        "buffer": recent_gestures,
                        "expected": expected_gestures
                    }
            
            # 认证中
            return {
                "success": True,
                "message": "手势密码认证中",
                "is_authenticated": False,
                "gesture": gesture,
                "confidence": confidence,
                "buffer": self.authentication_buffer,
                "expected": expected_gestures
            }
            
        except Exception as e:
            print(f"❌ 手势密码认证失败: {e}")
            return {
                "success": False,
                "message": f"手势密码认证失败: {str(e)}",
                "is_authenticated": False,
                "gesture": None,
                "confidence": 0.0
            }
    
    def register_gesture_password(self, user_id: str, gestures: List[str]) -> Dict[str, Any]:
        """
        注册手势密码
        
        Args:
            user_id: 用户ID
            gestures: 手势序列
            
        Returns:
            dict: 注册结果
        """
        try:
            # 验证手势序列
            if len(gestures) < 3:
                return {
                    "success": False,
                    "message": "手势密码长度必须至少为3个手势"
                }
            
            # 注册手势密码
            self.registered_gestures[user_id] = gestures
            
            return {
                "success": True,
                "message": f"用户 {user_id} 手势密码注册成功",
                "gestures": gestures
            }
            
        except Exception as e:
            print(f"❌ 注册手势密码失败: {e}")
            return {
                "success": False,
                "message": f"注册手势密码失败: {str(e)}"
            }
    
    def reset_authentication(self):
        """
        重置认证状态
        """
        self.authentication_buffer = []
    
    def get_gesture_count(self, user_id: str) -> int:
        """
        获取用户的手势密码长度
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 手势密码长度
        """
        if user_id in self.registered_gestures:
            return len(self.registered_gestures[user_id])
        return 0
    
    def get_authentication_progress(self, user_id: str) -> float:
        """
        获取认证进度
        
        Args:
            user_id: 用户ID
            
        Returns:
            float: 认证进度（0-1）
        """
        if user_id not in self.registered_gestures:
            return 0.0
        
        expected_len = len(self.registered_gestures[user_id])
        current_len = len(self.authentication_buffer)
        return min(current_len / expected_len, 1.0)
    
    def close(self):
        """
        释放资源
        """
        try:
            if hasattr(self, 'hand_detector'):
                self.hand_detector.close()
            
            if hasattr(self, 'pose_estimator'):
                self.pose_estimator.close()
            
            print("✅ 手势密码认证模块资源已释放")
        except Exception as e:
            print(f"❌ 释放手势密码认证模块资源失败: {e}")
    
    def __del__(self):
        """
        析构函数
        """
        self.close()