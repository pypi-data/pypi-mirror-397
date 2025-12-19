#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR处理器，集成DeepSeek OCR Q8量化版本
用于识别图片内容并提取关键信息
"""

import os
import sys
import json
from datetime import datetime
import numpy as np
from PIL import Image
import requests

class OCRProcessor:
    """
    OCR处理器，用于识别图片内容
    """
    
    def __init__(self, api_key=None, model="deepseek-ocr-q8"):
        """
        初始化OCR处理器
        
        Args:
            api_key: API密钥
            model: OCR模型名称
        """
        self.api_key = api_key
        self.model = model
        self.supported_formats = ["png", "jpg", "jpeg", "bmp", "pdf"]
        self.api_url = "https://api.deepseek.com/v1/ocr"
    
    def _preprocess_image(self, image_path):
        """
        预处理图片，提高OCR识别效果
        
        Args:
            image_path: 图片路径
            
        Returns:
            PIL.Image: 预处理后的图片
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # 调整图片大小，确保不超过OCR模型的最大限制
                max_size = 2048
                width, height = img.size
                if width > max_size or height > max_size:
                    ratio = min(max_size / width, max_size / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                return img
        except Exception as e:
            print(f"图片预处理失败: {str(e)}")
            return None
    
    def _encode_image(self, image_path):
        """
        将图片编码为base64格式
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: base64编码的图片
        """
        import base64
        
        try:
            img = self._preprocess_image(image_path)
            if img:
                # 保存为临时文件
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    temp_path = f.name
                img.save(temp_path, format="PNG")
                
                # 读取并编码
                with open(temp_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode("utf-8")
                
                # 删除临时文件
                os.remove(temp_path)
                
                return encoded_string
            return None
        except Exception as e:
            print(f"图片编码失败: {str(e)}")
            return None
    
    def recognize_image(self, image_path):
        """
        识别单张图片内容
        
        Args:
            image_path: 图片路径
            
        Returns:
            dict: 识别结果，包含文本内容和位置信息
        """
        try:
            # 验证图片格式
            ext = os.path.splitext(image_path)[1].lower()[1:]
            if ext not in self.supported_formats:
                return {
                    "success": False,
                    "message": f"不支持的图片格式: {ext}。支持的格式: {', '.join(self.supported_formats)}"
                }
            
            # 编码图片
            encoded_image = self._encode_image(image_path)
            if not encoded_image:
                return {
                    "success": False,
                    "message": "图片编码失败"
                }
            
            # 构造请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "image": {
                    "base64": encoded_image
                },
                "parameters": {
                    "return_text": True,
                    "return_boxes": True,
                    "language": "auto"
                }
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result,
                    "message": "图片识别成功"
                }
            else:
                return {
                    "success": False,
                    "message": f"OCR API请求失败: {response.status_code} - {response.text}"
                }
        except Exception as e:
            print(f"图片识别异常: {str(e)}")
            return {
                "success": False,
                "message": f"图片识别异常: {str(e)}"
            }
    
    def recognize_images_batch(self, image_paths):
        """
        批量识别图片内容
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            list: 识别结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.recognize_image(image_path)
            results.append({
                "image_path": image_path,
                "result": result
            })
        
        return {
            "success": True,
            "results": results,
            "total_images": len(image_paths),
            "successful_images": sum(1 for r in results if r["result"]["success"]),
            "message": f"批量识别完成，共处理 {len(image_paths)} 张图片"
        }
    
    def extract_template_variables(self, image_path, template_placeholders):
        """
        从图片中提取内容并匹配模板变量
        
        Args:
            image_path: 图片路径
            template_placeholders: 模板占位符列表
            
        Returns:
            dict: 匹配的变量和值
        """
        try:
            # 识别图片内容
            result = self.recognize_image(image_path)
            if not result["success"]:
                return {
                    "success": False,
                    "message": "图片识别失败"
                }
            
            # 提取文本内容
            text_content = ""
            if "content" in result and "text" in result["content"]:
                text_content = result["content"]["text"]
            elif "content" in result and "predictions" in result["content"]:
                # 处理其他OCR API返回格式
                for pred in result["content"]["predictions"]:
                    if "text" in pred:
                        text_content += pred["text"] + "\n"
            
            # 匹配模板变量
            matched_variables = {}
            for placeholder in template_placeholders:
                # 简单匹配：寻找包含占位符关键字的文本
                # 这里可以根据需要扩展为更复杂的匹配逻辑
                placeholder_key = placeholder.replace("{", "").replace("}", "")
                if placeholder_key in text_content:
                    # 提取占位符对应的值
                    # 这里实现一个简单的提取逻辑，实际应用中需要根据具体需求调整
                    # 例如：使用正则表达式提取关键字后面的值
                    import re
                    pattern = f"{placeholder_key}[：|:]\s*(.+?)\s*\n"
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        matched_variables[placeholder] = matches[0]
            
            return {
                "success": True,
                "matched_variables": matched_variables,
                "raw_content": text_content,
                "message": "变量提取成功"
            }
        except Exception as e:
            print(f"变量提取失败: {str(e)}")
            return {
                "success": False,
                "message": f"变量提取失败: {str(e)}"
            }
    
    def get_supported_formats(self):
        """
        获取支持的图片格式
        
        Returns:
            list: 支持的图片格式列表
        """
        return self.supported_formats
    
    def set_api_key(self, api_key):
        """
        设置API密钥
        
        Args:
            api_key: API密钥
        """
        self.api_key = api_key
    
    def set_model(self, model):
        """
        设置OCR模型
        
        Args:
            model: 模型名称
        """
        self.model = model
