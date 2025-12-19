import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from openvino.runtime import Core

class HandPoseEstimator:
    """基于OpenVINO的手部关键点提取器"""
    
    def __init__(self, model_path: str):
        """
        初始化手部关键点提取器
        
        Args:
            model_path: 模型文件路径（.xml文件）
        """
        self.model_path = model_path
        self.core = Core()
        self.model = None
        self.compiled_model = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        
        # 手部关键点索引
        self.hand_keypoint_indices = [5, 6, 7, 8, 9,  # 左手
                                     10, 11, 12, 13, 14]  # 右手
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载手部关键点模型"""
        try:
            print(f"🚀 加载手部关键点模型: {self.model_path}")
            
            # 读取模型
            self.model = self.core.read_model(self.model_path)
            
            # 编译模型
            self.compiled_model = self.core.compile_model(self.model, "AUTO")
            
            # 获取输入输出张量
            self.input_tensor_name = next(iter(self.compiled_model.inputs))
            self.output_tensor_name = next(iter(self.compiled_model.outputs))
            
            print("✅ 手部关键点模型加载成功!")
            return True
            
        except Exception as e:
            print(f"❌ 加载手部关键点模型失败: {e}")
            return False
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像
        
        Args:
            image: 输入图像，格式为 (高度, 宽度, 通道)
            
        Returns:
            np.ndarray: 预处理后的图像，格式为 (1, 通道, 高度, 宽度)
        """
        # 调整图像大小
        resized = cv2.resize(image, (640, 480))
        
        # 转换为RGB
        if resized.shape[-1] == 4:
            resized = resized[..., :3]
        
        # 转换为(通道, 高度, 宽度)格式
        input_tensor = resized.transpose(2, 0, 1)
        
        # 添加batch维度
        input_tensor = np.expand_dims(input_tensor, axis=0)
        
        # 归一化
        input_tensor = input_tensor.astype(np.float32) / 255.0
        
        return input_tensor
    
    def estimate_pose(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        估计人体姿势
        
        Args:
            image: 输入图像
            
        Returns:
            Optional[Dict[str, Any]]: 姿势估计结果，包含关键点坐标等信息
        """
        if self.model is None or self.compiled_model is None:
            return None
        
        try:
            # 预处理图像
            input_tensor = self.preprocess(image)
            
            # 推理
            result = self.compiled_model.infer_new_request({self.input_tensor_name: input_tensor})
            
            # 获取输出
            output = result[self.output_tensor_name]
            
            # 后处理
            pose_result = self.postprocess(output, image.shape)
            
            return pose_result
            
        except Exception as e:
            print(f"❌ 姿势估计失败: {e}")
            return None
    
    def postprocess(self, output: np.ndarray, image_shape: Tuple[int, int, int]) -> Dict[str, Any]:
        """
        后处理姿势估计输出
        
        Args:
            output: 模型输出
            image_shape: 原始图像形状 (高度, 宽度, 通道)
            
        Returns:
            Dict[str, Any]: 后处理后的姿势估计结果
        """
        # human-pose-estimation-0001 输出格式:
        # (batch_size, num_joints, height, width) 或 (batch_size, num_joints * 3, height, width)
        
        # 解析关键点
        batch_size, num_channels, height, width = output.shape
        num_joints = num_channels // 3
        
        # 提取置信度图
        conf_maps = output[0, num_joints:, :, :]
        
        # 提取偏移量
        offsets = output[0, :num_joints*2, :, :]
        
        # 提取关键点坐标
        keypoints = []
        for i in range(num_joints):
            # 找到置信度最高点
            conf_map = conf_maps[i, :, :]
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(conf_map)
            
            # 计算实际坐标
            x = (max_loc[0] / width) * image_shape[1]
            y = (max_loc[1] / height) * image_shape[0]
            confidence = max_val
            
            # 应用偏移量
            offset_x = offsets[i, max_loc[1], max_loc[0]]
            offset_y = offsets[i + num_joints, max_loc[1], max_loc[0]]
            
            x += offset_x
            y += offset_y
            
            keypoints.append({
                "x": float(x),
                "y": float(y),
                "confidence": float(confidence)
            })
        
        return {
            "keypoints": keypoints,
            "num_joints": num_joints,
            "confidence": float(np.mean([kp["confidence"] for kp in keypoints]))
        }
    
    def extract_hand_keypoints(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        提取手部关键点
        
        Args:
            image: 输入图像
            
        Returns:
            Optional[Dict[str, Any]]: 手部关键点结果
        """
        # 估计姿势
        pose_result = self.estimate_pose(image)
        
        if pose_result is None:
            return None
        
        # 提取手部关键点
        keypoints = pose_result["keypoints"]
        hand_keypoints = [kp for i, kp in enumerate(keypoints) if i in self.hand_keypoint_indices]
        
        # 计算手部关键点置信度
        hand_confidence = np.mean([kp["confidence"] for kp in hand_keypoints])
        
        # 检测是否有手
        has_hand = hand_confidence > 0.2
        
        return {
            "hand_keypoints": hand_keypoints,
            "has_hand": has_hand,
            "confidence": float(hand_confidence),
            "full_keypoints": keypoints
        }
    
    def detect_hand_from_keypoints(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        从关键点检测手部区域
        
        Args:
            image: 输入图像
            
        Returns:
            Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]: (手部区域图像, 边界框) 或 None
        """
        # 提取手部关键点
        hand_result = self.extract_hand_keypoints(image)
        
        if hand_result is None or not hand_result["has_hand"]:
            return None
        
        # 获取手部关键点
        hand_keypoints = hand_result["hand_keypoints"]
        
        # 计算手部边界框
        x_coords = [kp["x"] for kp in hand_keypoints]
        y_coords = [kp["y"] for kp in hand_keypoints]
        
        if not x_coords or not y_coords:
            return None
        
        # 计算边界框
        x1 = max(0, int(min(x_coords) - 20))
        y1 = max(0, int(min(y_coords) - 20))
        x2 = min(image.shape[1], int(max(x_coords) + 20))
        y2 = min(image.shape[0], int(max(y_coords) + 20))
        
        # 确保边界框有效
        if x1 >= x2 or y1 >= y2:
            return None
        
        # 提取手部区域
        hand_region = image[y1:y2, x1:x2]
        
        return hand_region, (x1, y1, x2 - x1, y2 - y1)
    
    def close(self):
        """释放模型资源"""
        try:
            if self.model is not None:
                self.model = None
            if self.compiled_model is not None:
                self.compiled_model = None
            print("✅ 手部关键点模型资源已释放")
        except Exception as e:
            print(f"❌ 释放手部关键点模型资源失败: {e}")
    
    def __del__(self):
        """析构函数"""
        self.close()