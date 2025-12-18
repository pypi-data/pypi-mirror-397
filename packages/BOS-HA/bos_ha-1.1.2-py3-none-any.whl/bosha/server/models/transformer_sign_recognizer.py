import numpy as np
from typing import Dict, Any, List
from openvino.runtime import Core
import os

class TransformerSignRecognizer:
    """基于Transformer的手语识别模型封装类"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        """
        初始化Transformer手语识别模型
        
        Args:
            model_path: 模型文件路径（.xml文件）
            confidence_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.core = Core()
        self.model = None
        self.compiled_model = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        
        # 扩展手语类别，与原有模型保持一致
        self.class_names = [
            # 问候类
            "你好", "谢谢", "再见", "早上好", "晚上好", "欢迎", "请问", "没关系", "不客气", "久仰", 
            # 情感类
            "我爱你", "喜欢", "生气", "悲伤", "开心", "惊讶", "感动", "害怕", "骄傲", "失望", 
            # 回答类
            "是", "否", "不知道", "可能", "当然", "抱歉", "是的", "不是", "也许", "一定", 
            # 请求类
            "请", "帮助", "需要", "想要", "给我", "借我", "请问", "麻烦", "拜托", "让一下", 
            # 身份类
            "我", "你", "他", "她", "我们", "你们", "他们", "老师", "医生", "学生", 
            # 生活类
            "家", "学校", "工作", "医院", "商店", "公园", "餐厅", "银行", "超市", "邮局", 
            # 物品类
            "食物", "水", "饮料", "衣服", "鞋子", "帽子", "手机", "电脑", "书包", "书本", 
            "笔", "纸", "杯子", "筷子", "勺子", "碗", "盘子", "桌子", "椅子", "床", 
            # 动作类
            "走", "跑", "坐", "站", "吃", "喝", "看", "听", "说", "写", 
            "读", "画", "唱", "跳", "睡", "醒", "来", "去", "上", "下", 
            # 数量类
            "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", 
            "百", "千", "万", "零", "半", "两", "多", "少", "第一", "第二", 
            # 其他
            "时间", "今天", "明天", "昨天", "星期", "月份", "年", "钱", "价格", "颜色", 
            "红色", "蓝色", "绿色", "黄色", "黑色", "白色", "紫色", "橙色", "粉色", "灰色", 
            "大", "小", "长", "短", "高", "矮", "胖", "瘦", "热", "冷", 
            "早", "晚", "快", "慢", "好", "坏", "对", "错", "新", "旧",
            # 扩展类别
            "朋友", "家人", "父母", "兄弟", "姐妹", "孩子", "老人", "年轻人", "男人", "女人",
            "水果", "蔬菜", "肉类", "米饭", "面条", "面包", "牛奶", "果汁", "咖啡", "茶",
            "汽车", "火车", "飞机", "地铁", "公交", "自行车", "步行", "驾驶", "乘坐", "到达",
            "开始", "结束", "继续", "停止", "等待", "出发", "返回", "离开", "到达", "停留"
        ]
        
        # 序列识别支持
        self.sequence_buffer = []
        self.sequence_length = 10
        self.sequence_weights = np.linspace(0.1, 1.0, self.sequence_length)
        self.sequence_weights /= np.sum(self.sequence_weights)
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载Transformer手语识别模型"""
        try:
            print(f"🚀 加载Transformer手语识别模型: {self.model_path}")
            
            # 读取模型
            self.model = self.core.read_model(self.model_path)
            
            # 编译模型
            self.compiled_model = self.core.compile_model(self.model, "AUTO")
            
            # 获取输入输出张量
            self.input_tensor_name = next(iter(self.compiled_model.inputs))
            self.output_tensor_name = next(iter(self.compiled_model.outputs))
            
            print("✅ Transformer手语识别模型加载成功!")
            return True
            
        except Exception as e:
            print(f"❌ 加载Transformer手语识别模型失败: {e}")
            return False
    
    def preprocess(self, keypoints: List[Dict[str, float]]) -> np.ndarray:
        """
        预处理关键点数据
        
        Args:
            keypoints: 关键点列表，每个关键点包含x, y, confidence
            
        Returns:
            np.ndarray: 预处理后的关键点数据，格式为 (1, 序列长度, 关键点数量 * 2)
        """
        # 提取x, y坐标
        coords = []
        for kp in keypoints:
            coords.append([kp["x"], kp["y"]])
        
        # 转换为numpy数组
        coords = np.array(coords)
        
        # 归一化到 [-1, 1] 范围
        if coords.shape[0] > 0:
            min_vals = coords.min(axis=0)
            max_vals = coords.max(axis=0)
            range_vals = max_vals - min_vals
            range_vals[range_vals == 0] = 1.0
            coords = 2.0 * (coords - min_vals) / range_vals - 1.0
        
        # 调整形状为 (1, 序列长度, 关键点数量 * 2)
        input_tensor = np.expand_dims(coords.flatten(), axis=0)
        input_tensor = np.expand_dims(input_tensor, axis=0)
        
        return input_tensor.astype(np.float32)
    
    def predict(self, keypoints: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        对手语进行预测
        
        Args:
            keypoints: 关键点列表，每个关键点包含x, y, confidence
            
        Returns:
            dict: 预测结果，包含类别、置信度等信息
        """
        try:
            if not self.model or not self.compiled_model:
                return {
                    "success": False,
                    "message": "Transformer模型未加载，请先下载并选择有效的模型",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 预处理关键点数据
            input_tensor = self.preprocess(keypoints)
            
            # 推理
            result = self.compiled_model.infer_new_request({self.input_tensor_name: input_tensor})
            output = result[self.output_tensor_name]
            
            # 后处理
            probabilities = self.softmax(output[0])
            confidence = np.max(probabilities)
            predicted_idx = np.argmax(probabilities)
            predicted_class = self.class_names[predicted_idx % len(self.class_names)] if confidence >= self.confidence_threshold else ""
            
            return {
                "success": True,
                "message": "识别成功",
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "probabilities": probabilities.tolist(),
                "class_index": int(predicted_idx)
            }
            
        except Exception as e:
            print(f"❌ Transformer模型推理失败: {e}")
            return {
                "success": False,
                "message": f"推理失败: {str(e)}",
                "predicted_class": "",
                "confidence": 0.0
            }
    
    def predict_sequence(self, sequence_keypoints: List[List[Dict[str, float]]]) -> Dict[str, Any]:
        """
        对连续关键点序列进行预测
        
        Args:
            sequence_keypoints: 关键点序列列表，每个元素是一帧的关键点
            
        Returns:
            dict: 序列预测结果
        """
        try:
            if not self.model or not self.compiled_model:
                return {
                    "success": False,
                    "message": "Transformer模型未加载",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 批量预处理
            batch_input = []
            valid_frames = []
            
            for kps in sequence_keypoints:
                if kps:
                    input_tensor = self.preprocess(kps)
                    batch_input.append(input_tensor)
                    valid_frames.append(True)
                else:
                    valid_frames.append(False)
            
            if not batch_input:
                return {
                    "success": False,
                    "message": "无效的关键点序列",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 合并为批量输入
            batch_input = np.concatenate(batch_input, axis=0)
            
            # 批量推理
            result = self.compiled_model.infer_new_request({self.input_tensor_name: batch_input})
            outputs = result[self.output_tensor_name]
            
            # 后处理
            frame_predictions = []
            for i, output in enumerate(outputs):
                probabilities = self.softmax(output)
                confidence = np.max(probabilities)
                predicted_idx = np.argmax(probabilities)
                predicted_class = self.class_names[predicted_idx % len(self.class_names)] if confidence >= self.confidence_threshold else ""
                
                frame_predictions.append({
                    "predicted_class": predicted_class,
                    "confidence": float(confidence),
                    "probabilities": probabilities
                })
            
            # 序列融合
            final_probabilities = self.fuse_sequence_predictions(frame_predictions)
            final_confidence = np.max(final_probabilities)
            final_predicted_idx = np.argmax(final_probabilities)
            final_predicted_class = self.class_names[final_predicted_idx % len(self.class_names)] if final_confidence >= self.confidence_threshold else ""
            
            return {
                "success": True,
                "message": "序列识别成功",
                "predicted_class": final_predicted_class,
                "confidence": float(final_confidence),
                "frame_predictions": frame_predictions,
                "sequence_length": len(valid_frames),
                "valid_frames": sum(valid_frames)
            }
            
        except Exception as e:
            print(f"❌ 序列预测失败: {e}")
            return {
                "success": False,
                "message": f"序列预测失败: {str(e)}",
                "predicted_class": "",
                "confidence": 0.0
            }
    
    def fuse_sequence_predictions(self, predictions: List[Dict[str, Any]]) -> np.ndarray:
        """
        融合序列预测结果
        
        Args:
            predictions: 帧预测结果列表
            
        Returns:
            np.ndarray: 融合后的概率分布
        """
        if not predictions:
            return np.zeros(len(self.class_names))
        
        # 调整权重长度
        current_length = len(predictions)
        weights = self.sequence_weights[-current_length:] if current_length < self.sequence_length else self.sequence_weights
        weights = weights[:current_length] / np.sum(weights[:current_length])
        
        # 初始化融合概率
        fused_probabilities = np.zeros(len(self.class_names))
        
        # 加权融合
        for i, pred in enumerate(predictions):
            fused_probabilities += weights[i] * pred["probabilities"]
        
        return fused_probabilities
    
    def softmax(self, x: np.ndarray) -> np.ndarray:
        """
        计算softmax值
        
        Args:
            x: 输入数组
            
        Returns:
            np.ndarray: softmax结果
        """
        try:
            # 避免数值溢出，减去最大值
            max_val = np.max(x)
            e_x = np.exp(x - max_val)
            
            # 计算总和，添加极小值避免除以零
            sum_e_x = np.sum(e_x) + 1e-10
            
            return e_x / sum_e_x
            
        except Exception as e:
            print(f"❌ softmax计算失败: {e}")
            # 返回均匀分布作为 fallback
            return np.ones_like(x) / len(x) if len(x) > 0 else np.array([1.0])
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "model_path": self.model_path,
            "model_type": "transformer",
            "confidence_threshold": self.confidence_threshold,
            "class_count": len(self.class_names),
            "class_names": self.class_names,
            "model_loaded": self.model is not None,
            "sequence_length": self.sequence_length
        }
    
    def update_confidence_threshold(self, threshold: float):
        """
        更新置信度阈值
        
        Args:
            threshold: 新的置信度阈值
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            print(f"置信度阈值已更新为: {threshold}")
        else:
            print("置信度阈值必须在 [0.0, 1.0] 范围内")
    
    def close(self):
        """释放模型资源"""
        try:
            if self.model is not None:
                self.model = None
            if self.compiled_model is not None:
                self.compiled_model = None
            print("✅ Transformer模型资源已释放")
        except Exception as e:
            print(f"❌ 释放Transformer模型资源失败: {e}")
    
    def __del__(self):
        """析构函数"""
        self.close()