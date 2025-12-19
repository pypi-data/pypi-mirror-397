from typing import Dict, Any, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import numpy as np

class Qwen3VLSemanticValidator:
    """Qwen3-VL语义校验模块"""
    
    def __init__(self, model_name: str = "Qwen/Qwen2-VL-7B-Instruct"):
        """
        初始化Qwen3-VL语义校验模块
        
        Args:
            model_name: 模型名称或路径
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载Qwen3-VL模型"""
        try:
            print(f"🚀 加载Qwen3-VL模型: {self.model_name}")
            print(f"📱 使用设备: {self.device}")
            
            # 加载模型和分词器
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            
            print("✅ Qwen3-VL模型加载成功!")
            return True
            
        except Exception as e:
            print(f"❌ 加载Qwen3-VL模型失败: {e}")
            return False
    
    def validate_sign_sentence(self, sentence: str, image: np.ndarray = None) -> Dict[str, Any]:
        """
        语义校验手语句子
        
        Args:
            sentence: 生成的手语句子
            image: 可选的输入图像
            
        Returns:
            dict: 语义校验结果
        """
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "message": "Qwen3-VL模型未加载",
                    "is_valid": False,
                    "confidence": 0.0,
                    "suggestion": ""
                }
            
            # 构建提示词
            prompt = f"请检查以下手语识别结果的语义是否通顺、合理:\n\n{sentence}\n\n请回答：\n1. 是否语义通顺？（是/否）\n2. 置信度评分（0-100）\n3. 如果有问题，请给出修正建议"
            
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 模型推理
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
            
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 解析响应
            result = self._parse_response(response)
            
            return {
                "success": True,
                "message": "语义校验成功",
                "is_valid": result["is_valid"],
                "confidence": result["confidence"],
                "suggestion": result["suggestion"],
                "raw_response": response
            }
            
        except Exception as e:
            print(f"❌ 语义校验失败: {e}")
            return {
                "success": False,
                "message": f"语义校验失败: {str(e)}",
                "is_valid": False,
                "confidence": 0.0,
                "suggestion": ""
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析模型响应
        
        Args:
            response: 模型响应文本
            
        Returns:
            dict: 解析结果
        """
        # 默认结果
        result = {
            "is_valid": False,
            "confidence": 50,
            "suggestion": ""
        }
        
        try:
            # 解析是否语义通顺
            if "是" in response.split("\n")[0]:
                result["is_valid"] = True
            
            # 解析置信度评分
            for line in response.split("\n"):
                if "置信度" in line or "评分" in line:
                    # 提取数字
                    confidence = int(''.join(filter(str.isdigit, line)))
                    result["confidence"] = min(max(confidence, 0), 100) / 100.0
                    break
            
            # 解析修正建议
            if "建议" in response:
                suggestion_start = response.find("建议")
                if suggestion_start != -1:
                    result["suggestion"] = response[suggestion_start:].strip()
            
        except Exception as e:
            print(f"❌ 解析响应失败: {e}")
        
        return result
    
    def validate_with_image(self, sentence: str, image: np.ndarray) -> Dict[str, Any]:
        """
        结合图像进行语义校验
        
        Args:
            sentence: 生成的手语句子
            image: 输入图像
            
        Returns:
            dict: 语义校验结果
        """
        try:
            if not self.model or not self.tokenizer:
                return {
                    "success": False,
                    "message": "Qwen3-VL模型未加载",
                    "is_valid": False,
                    "confidence": 0.0,
                    "suggestion": ""
                }
            
            # 将numpy数组转换为PIL图像
            pil_image = Image.fromarray(image)
            
            # 构建提示词
            prompt = f"请观察以下图像，并检查图像内容与手语识别结果是否匹配：\n\n手语识别结果：{sentence}\n\n请回答：\n1. 图像内容与识别结果是否匹配？（是/否）\n2. 匹配度评分（0-100）\n3. 如果有问题，请给出修正建议"
            
            # 模型推理
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": pil_image
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
            
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 解析响应
            result = self._parse_response(response)
            
            return {
                "success": True,
                "message": "图像语义校验成功",
                "is_valid": result["is_valid"],
                "confidence": result["confidence"],
                "suggestion": result["suggestion"],
                "raw_response": response
            }
            
        except Exception as e:
            print(f"❌ 图像语义校验失败: {e}")
            return {
                "success": False,
                "message": f"图像语义校验失败: {str(e)}",
                "is_valid": False,
                "confidence": 0.0,
                "suggestion": ""
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "model_name": self.model_name,
            "model_type": "qwen3-vl",
            "device": self.device,
            "model_loaded": self.model is not None
        }
    
    def close(self):
        """
        释放模型资源
        """
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            print("✅ Qwen3-VL模型资源已释放")
        except Exception as e:
            print(f"❌ 释放Qwen3-VL模型资源失败: {e}")
    
    def __del__(self):
        """
        析构函数
        """
        self.close()