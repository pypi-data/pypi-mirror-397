import numpy as np
import time
from typing import Dict, Any, List, Optional
from .yolov8_hand_detector import YOLOv8HandDetector
from .hand_pose_estimator import HandPoseEstimator
from .transformer_sign_recognizer import TransformerSignRecognizer
from .sentence_generator import SentenceGenerator

class EndToEndSignRecognition:
    """端到端手语识别系统"""
    
    def __init__(self, 
                 yolov8_model_path: str,
                 pose_model_path: str,
                 transformer_model_path: str,
                 confidence_threshold: float = 0.7):
        """
        初始化端到端手语识别系统
        
        Args:
            yolov8_model_path: YOLOv8模型路径
            pose_model_path: 人体姿态估计模型路径
            transformer_model_path: Transformer手语识别模型路径
            confidence_threshold: 置信度阈值
        """
        self.confidence_threshold = confidence_threshold
        
        # 初始化各个模块
        self.hand_detector = YOLOv8HandDetector(yolov8_model_path)
        self.pose_estimator = HandPoseEstimator(pose_model_path)
        self.sign_recognizer = TransformerSignRecognizer(transformer_model_path, confidence_threshold)
        self.sentence_generator = SentenceGenerator()
        
        # 序列缓冲区
        self.sequence_buffer = []
        self.max_sequence_length = 30  # 最大序列长度（约5秒）
    
    def recognize_sign(self, image: np.ndarray) -> Dict[str, Any]:
        """
        端到端手语识别
        
        Args:
            image: 输入图像，格式为 (高度, 宽度, 通道)
            
        Returns:
            dict: 识别结果，包含手语类别、置信度、句子等信息
        """
        try:
            # 1. 手部检测
            hand_result = self.hand_detector.detect_hand(image)
            if not hand_result:
                return {
                    "success": False,
                    "message": "未检测到手部",
                    "hand_detected": False,
                    "keypoints_extracted": False,
                    "recognized": False,
                    "predicted_class": "",
                    "confidence": 0.0,
                    "sentence": ""
                }
            
            hand_region, hand_bbox = hand_result
            
            # 2. 手部关键点提取
            keypoint_result = self.pose_estimator.extract_hand_keypoints(image)
            if not keypoint_result or not keypoint_result["has_hand"]:
                return {
                    "success": False,
                    "message": "未提取到手部关键点",
                    "hand_detected": True,
                    "keypoints_extracted": False,
                    "recognized": False,
                    "predicted_class": "",
                    "confidence": 0.0,
                    "sentence": ""
                }
            
            hand_keypoints = keypoint_result["hand_keypoints"]
            
            # 3. 手语识别
            recognition_result = self.sign_recognizer.predict(hand_keypoints)
            
            if not recognition_result["success"]:
                return {
                    "success": False,
                    "message": recognition_result["message"],
                    "hand_detected": True,
                    "keypoints_extracted": True,
                    "recognized": False,
                    "predicted_class": "",
                    "confidence": 0.0,
                    "sentence": ""
                }
            
            predicted_class = recognition_result["predicted_class"]
            confidence = recognition_result["confidence"]
            
            # 4. 序列处理
            self.sequence_buffer.append({
                "predicted_class": predicted_class,
                "confidence": confidence,
                "timestamp": time.time()
            })
            
            # 保持序列长度
            if len(self.sequence_buffer) > self.max_sequence_length:
                self.sequence_buffer = self.sequence_buffer[-self.max_sequence_length:]
            
            # 5. 句子生成
            sentence = self.generate_sentence()
            
            return {
                "success": True,
                "message": "识别成功",
                "hand_detected": True,
                "keypoints_extracted": True,
                "recognized": True,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "sentence": sentence,
                "hand_bbox": hand_bbox,
                "sequence_length": len(self.sequence_buffer),
                "sequence": self.sequence_buffer
            }
            
        except Exception as e:
            print(f"❌ 端到端手语识别失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"识别失败: {str(e)}",
                "hand_detected": False,
                "keypoints_extracted": False,
                "recognized": False,
                "predicted_class": "",
                "confidence": 0.0,
                "sentence": ""
            }
    
    def generate_sentence(self) -> str:
        """
        生成完整句子
        
        Returns:
            str: 生成的句子
        """
        if not self.sequence_buffer:
            return ""
        
        # 提取有效识别结果
        valid_recognitions = [rec for rec in self.sequence_buffer if rec["predicted_class"] and rec["confidence"] >= self.confidence_threshold]
        
        if not valid_recognitions:
            return ""
        
        # 提取识别类别
        recognition_classes = [rec["predicted_class"] for rec in valid_recognitions]
        
        # 使用句子生成器生成句子
        sentence = self.sentence_generator.generate_sentence(recognition_classes)
        
        return sentence
    
    def recognize_sequence(self, images: List[np.ndarray]) -> Dict[str, Any]:
        """
        对连续图像序列进行识别
        
        Args:
            images: 图像序列
            
        Returns:
            dict: 序列识别结果
        """
        try:
            # 保存原始序列缓冲区
            original_buffer = self.sequence_buffer.copy()
            self.sequence_buffer = []
            
            # 逐帧识别
            frame_results = []
            for image in images:
                result = self.recognize_sign(image)
                frame_results.append(result)
            
            # 生成最终句子
            final_sentence = self.generate_sentence()
            
            # 计算统计信息
            valid_frames = sum(1 for res in frame_results if res["recognized"])
            avg_confidence = np.mean([res["confidence"] for res in frame_results if res["recognized"]]) if valid_frames > 0 else 0.0
            
            return {
                "success": True,
                "message": "序列识别成功",
                "frame_results": frame_results,
                "valid_frames": valid_frames,
                "total_frames": len(images),
                "avg_confidence": float(avg_confidence),
                "final_sentence": final_sentence,
                "sequence_length": len(self.sequence_buffer),
                "sequence": self.sequence_buffer
            }
            
        except Exception as e:
            print(f"❌ 序列识别失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"序列识别失败: {str(e)}",
                "frame_results": [],
                "valid_frames": 0,
                "total_frames": len(images),
                "avg_confidence": 0.0,
                "final_sentence": "",
                "sequence_length": 0,
                "sequence": []
            }
        finally:
            # 恢复原始序列缓冲区
            self.sequence_buffer = original_buffer
    
    def reset_sequence(self):
        """重置序列缓冲区"""
        self.sequence_buffer = []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "system_type": "end_to_end_sign_recognition",
            "confidence_threshold": self.confidence_threshold,
            "max_sequence_length": self.max_sequence_length,
            "hand_detector": {
                "model_path": self.hand_detector.model_path,
                "model_loaded": self.hand_detector.model is not None
            },
            "pose_estimator": {
                "model_path": self.pose_estimator.model_path,
                "model_loaded": self.pose_estimator.model is not None
            },
            "sign_recognizer": {
                "model_path": self.sign_recognizer.model_path,
                "model_loaded": self.sign_recognizer.model is not None,
                "class_count": len(self.sign_recognizer.class_names)
            },
            "sentence_generator": {
                "enabled": True
            }
        }
    
    def update_confidence_threshold(self, threshold: float):
        """
        更新置信度阈值
        
        Args:
            threshold: 新的置信度阈值
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            self.sign_recognizer.update_confidence_threshold(threshold)
            print(f"置信度阈值已更新为: {threshold}")
        else:
            print("置信度阈值必须在 [0.0, 1.0] 范围内")
    
    def close(self):
        """
        释放所有模型资源
        """
        try:
            print("🚀 释放所有模型资源...")
            
            if hasattr(self, 'hand_detector'):
                self.hand_detector.close()
            
            if hasattr(self, 'pose_estimator'):
                self.pose_estimator.close()
            
            if hasattr(self, 'sign_recognizer'):
                self.sign_recognizer.close()
            
            print("✅ 所有模型资源已释放")
            
        except Exception as e:
            print(f"❌ 释放模型资源失败: {e}")
    
    def __del__(self):
        """
        析构函数，确保资源被释放
        """
        self.close()