import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
import os
from openvino.runtime import Core

class YOLOv8HandDetector:
    """YOLOv8n手部检测器"""
    
    def __init__(self, model_path: str):
        """
        初始化YOLOv8n手部检测器
        
        Args:
            model_path: 模型文件路径（.xml文件）
        """
        self.model_path = model_path
        self.core = Core()
        self.model = None
        self.compiled_model = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        self.class_names = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
            "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
            "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
            "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
            "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
            "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
            "hair drier", "toothbrush"
        ]
        
        # 手部相关类别索引
        self.hand_related_classes = [47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载YOLOv8n模型"""
        try:
            print(f"🚀 加载YOLOv8n模型: {self.model_path}")
            
            # 读取模型
            self.model = self.core.read_model(self.model_path)
            
            # 编译模型
            self.compiled_model = self.core.compile_model(self.model, "AUTO")
            
            # 获取输入输出张量
            self.input_tensor_name = next(iter(self.compiled_model.inputs))
            self.output_tensor_name = next(iter(self.compiled_model.outputs))
            
            print("✅ YOLOv8n模型加载成功!")
            return True
            
        except Exception as e:
            print(f"❌ 加载YOLOv8n模型失败: {e}")
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
        resized = cv2.resize(image, (640, 640))
        
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
    
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5, iou_threshold: float = 0.45) -> List[Dict[str, Any]]:
        """
        检测图像中的手部
        
        Args:
            image: 输入图像
            confidence_threshold: 置信度阈值
            iou_threshold: IoU阈值
            
        Returns:
            List[Dict[str, Any]]: 检测结果列表
        """
        if self.model is None or self.compiled_model is None:
            return []
        
        try:
            # 预处理图像
            input_tensor = self.preprocess(image)
            
            # 推理
            result = self.compiled_model.infer_new_request({self.input_tensor_name: input_tensor})
            
            # 获取输出
            output = result[self.output_tensor_name]
            
            # 后处理
            detections = self.postprocess(output, image.shape, confidence_threshold, iou_threshold)
            
            return detections
            
        except Exception as e:
            print(f"❌ YOLOv8n检测失败: {e}")
            return []
    
    def postprocess(self, output: np.ndarray, image_shape: Tuple[int, int, int], confidence_threshold: float, iou_threshold: float) -> List[Dict[str, Any]]:
        """
        后处理YOLOv8n输出
        
        Args:
            output: 模型输出
            image_shape: 原始图像形状 (高度, 宽度, 通道)
            confidence_threshold: 置信度阈值
            iou_threshold: IoU阈值
            
        Returns:
            List[Dict[str, Any]]: 检测结果列表
        """
        detections = []
        
        # YOLOv8输出格式: (batch_size, num_detections, 85)
        # 其中85 = x, y, w, h, confidence, class1, class2, ..., class80
        
        # 遍历所有检测结果
        for detection in output[0]:
            x_center, y_center, width, height, confidence, *class_scores = detection
            
            # 过滤低置信度检测
            if confidence < confidence_threshold:
                continue
            
            # 获取类别
            class_id = np.argmax(class_scores)
            class_score = class_scores[class_id]
            
            # 过滤非手部相关类别
            if class_id not in self.hand_related_classes:
                continue
            
            # 计算边界框
            x1 = int((x_center - width / 2) * (image_shape[1] / 640))
            y1 = int((y_center - height / 2) * (image_shape[0] / 640))
            x2 = int((x_center + width / 2) * (image_shape[1] / 640))
            y2 = int((y_center + height / 2) * (image_shape[0] / 640))
            
            # 确保边界框在图像范围内
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_shape[1], x2)
            y2 = min(image_shape[0], y2)
            
            # 计算边界框宽度和高度
            w = x2 - x1
            h = y2 - y1
            
            # 添加到检测结果
            detections.append({
                "class_id": int(class_id),
                "class_name": self.class_names[class_id],
                "confidence": float(confidence * class_score),
                "bbox": (x1, y1, w, h),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })
        
        # 按置信度排序
        detections.sort(key=lambda x: x["confidence"], reverse=True)
        
        # 非极大值抑制
        nms_detections = self.nms(detections, iou_threshold)
        
        return nms_detections
    
    def nms(self, detections: List[Dict[str, Any]], iou_threshold: float) -> List[Dict[str, Any]]:
        """
        非极大值抑制
        
        Args:
            detections: 检测结果列表
            iou_threshold: IoU阈值
            
        Returns:
            List[Dict[str, Any]]: NMS后的检测结果列表
        """
        if len(detections) == 0:
            return []
        
        # 提取边界框和置信度
        boxes = np.array([det["bbox"] for det in detections])
        confidences = np.array([det["confidence"] for det in detections])
        
        # 转换边界框格式 (x1, y1, w, h) -> (x1, y1, x2, y2)
        boxes[:, 2] = boxes[:, 0] + boxes[:, 2]
        boxes[:, 3] = boxes[:, 1] + boxes[:, 3]
        
        # 使用OpenCV的NMS
        indices = cv2.dnn.NMSBoxes(boxes.tolist(), confidences.tolist(), 0.0, iou_threshold)
        
        # 获取NMS后的检测结果
        nms_detections = [detections[i] for i in indices.flatten()] if len(indices) > 0 else []
        
        return nms_detections
    
    def detect_hand(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        检测手部并返回手部区域
        
        Args:
            image: 输入图像
            
        Returns:
            Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]: (手部区域图像, 边界框) 或 None
        """
        # 检测所有物体
        detections = self.detect(image, confidence_threshold=0.3, iou_threshold=0.45)
        
        if not detections:
            return None
        
        # 寻找最大的手部相关检测
        max_area = 0
        best_hand = None
        
        for det in detections:
            x, y, w, h = det["bbox"]
            area = w * h
            
            if area > max_area:
                max_area = area
                best_hand = det
        
        if best_hand is None:
            return None
        
        # 提取手部区域
        x, y, w, h = best_hand["bbox"]
        
        # 扩展边界框，确保包含完整手部
        margin = 20
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(image.shape[1], x + w + margin)
        y2 = min(image.shape[0], y + h + margin)
        
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
            print("✅ YOLOv8n模型资源已释放")
        except Exception as e:
            print(f"❌ 释放YOLOv8n模型资源失败: {e}")
    
    def __del__(self):
        """析构函数"""
        self.close()