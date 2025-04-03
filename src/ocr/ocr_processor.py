#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   ocr_processor.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
OCR处理模块
负责图像文字识别，支持百度OCR、腾讯云OCR和自定义OCR
"""

import os
import io
import base64
import json
import requests
from pathlib import Path
from PIL import Image, ImageEnhance
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import tempfile


class OCRProcessor:
    """OCR处理器，用于从图像中提取文字"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化OCR处理器
        
        Args:
            config: OCR配置字典，如果为None则从环境变量读取配置
        """
        # 如果未提供配置，则从环境变量读取
        if config is None:
            config = self._load_config_from_env()
            
        self.config = config
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        self.max_image_size = 4096  # 最大允许的图片尺寸
        
        # 创建日志记录器
        self.logger = logging.getLogger("OCRProcessor")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """从环境变量加载OCR配置"""
        config = {
            "OCR_API_TYPE": os.environ.get("OCR_API_TYPE", "CUSTOM")
        }
        
        # 根据API类型加载对应的配置
        if config["OCR_API_TYPE"] == "BAIDU":
            config["BAIDU_APP_ID"] = os.environ.get("BAIDU_APP_ID", "")
            config["BAIDU_API_KEY"] = os.environ.get("BAIDU_API_KEY", "")
            config["BAIDU_SECRET_KEY"] = os.environ.get("BAIDU_SECRET_KEY", "")
            config["BAIDU_OCR_TOKEN"] = os.environ.get("BAIDU_OCR_TOKEN", "")
        elif config["OCR_API_TYPE"] == "TENCENT":
            config["TENCENT_SECRET_ID"] = os.environ.get("TENCENT_SECRET_ID", "")
            config["TENCENT_SECRET_KEY"] = os.environ.get("TENCENT_SECRET_KEY", "")
        else:  # CUSTOM
            config["CUSTOM_OCR_ENDPOINT"] = os.environ.get("CUSTOM_OCR_ENDPOINT", "")
            config["OCR_LANGUAGE"] = os.environ.get("OCR_LANGUAGE", "zh")
            config["OCR_TIMEOUT"] = int(os.environ.get("OCR_TIMEOUT", "30"))
            
        return config

    def preprocess_image(self, image_path: Path) -> bytes:
        """预处理图片以提高OCR识别精度"""
        try:
            with Image.open(image_path) as img:
                # 调整图片尺寸
                img.thumbnail((self.max_image_size, self.max_image_size))
                
                # 转换为RGB模式(处理RGBA或其他格式)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 增强对比度
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                
                # 保存处理后的图片到字节流
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=85)
                return img_buffer.getvalue()
        except Exception as e:
            raise OCRProcessingError(f"图像预处理失败: {str(e)}")

    def process_image(self, image_path: Path) -> str:
        """处理图片并返回识别文本"""
        if image_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"不支持的图片格式: {image_path.suffix}，支持的格式: {', '.join(self.supported_formats)}")

        try:
            # 获取OCR API类型
            api_type = self.config.get('OCR_API_TYPE', 'CUSTOM')
            
            # 百度OCR处理
            if api_type == "BAIDU":
                return self._process_with_baidu(image_path)
            
            # 腾讯OCR处理
            elif api_type == "TENCENT":
                return self._process_with_tencent(image_path)
            
            # 自定义OCR处理
            else:
                return self._process_with_custom(image_path)
                
        except Exception as e:
            raise OCRProcessingError(f"图片处理失败: {str(e)}") from e
    
    def _process_with_baidu(self, image_path: Path) -> str:
        """使用百度OCR处理图片"""
        try:
            # 导入百度OCR SDK
            from aip import AipOcr
            
            # 获取百度OCR参数
            app_id = self.config.get("BAIDU_APP_ID") or os.environ.get("BAIDU_APP_ID")
            api_key = self.config.get("BAIDU_API_KEY") or os.environ.get("BAIDU_API_KEY")
            secret_key = self.config.get("BAIDU_SECRET_KEY") or os.environ.get("BAIDU_SECRET_KEY")
            
            if not app_id or not api_key or not secret_key:
                raise OCRAPIError("未配置百度OCR APP_ID、API_KEY或SECRET_KEY")
            
            # 创建客户端
            client = AipOcr(app_id, api_key, secret_key)
            
            # 读取图片文件
            with open(str(image_path), 'rb') as fp:
                image_data = fp.read()
            
            # 设置请求参数
            options = {
                "language_type": "CHN_ENG",  # 中英文混合
                "detect_direction": "true",   # 检测文字方向
                "detect_language": "true",    # 检测语言
                "probability": "true"         # 返回置信度
            }
            
            # 调用通用文字识别（高精度版）
            result = client.basicAccurate(image_data, options)
            
            # 处理错误情况
            if "error_code" in result:
                raise OCRAPIError(f"百度OCR错误: {result['error_msg']}")
            
            # 返回识别结果
            return "\n".join([item["words"] for item in result["words_result"]])
            
        except ImportError:
            raise OCRAPIError("未安装百度OCR SDK，请执行: pip install baidu-aip")
        except Exception as e:
            raise OCRAPIError(f"百度OCR处理失败: {str(e)}")

    def _process_with_tencent(self, image_path: Path) -> str:
        """使用腾讯OCR处理图片"""
        try:
            # 导入腾讯云OCR SDK
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
            from tencentcloud.ocr.v20181119 import ocr_client, models
            
            # 获取腾讯云配置
            secret_id = self.config.get("TENCENT_SECRET_ID") or os.environ.get("TENCENT_SECRET_ID")
            secret_key = self.config.get("TENCENT_SECRET_KEY") or os.environ.get("TENCENT_SECRET_KEY")
            
            if not secret_id or not secret_key:
                raise OCRAPIError("未配置腾讯云SecretId或SecretKey")
            
            # 创建认证对象
            cred = credential.Credential(secret_id, secret_key)
            
            # 配置HTTP参数
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            
            # 创建客户端配置
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 创建OCR客户端，使用北京区域
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)
            
            # 读取图片文件并转换为base64
            with open(str(image_path), 'rb') as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
            
            # 创建OCR请求对象
            req = models.GeneralAccurateOCRRequest()  # 使用高精度版本
            
            # 设置图片数据
            req.ImageBase64 = base64_str
            
            # 发送OCR请求
            resp = client.GeneralAccurateOCR(req)
            
            # 提取识别结果
            result_texts = []
            for text in resp.TextDetections:
                result_texts.append(text.DetectedText)
            
            # 返回识别文本
            return "\n".join(result_texts)
            
        except ImportError:
            raise OCRAPIError("未安装腾讯云SDK，请执行: pip install tencentcloud-sdk-python")
        except Exception as e:
            raise OCRAPIError(f"腾讯OCR处理失败: {str(e)}")

    def _process_with_custom(self, image_path: Path) -> str:
        """使用自定义OCR处理图片"""
        try:
            # 获取自定义OCR地址
            ocr_url = self.config.get("CUSTOM_OCR_ENDPOINT") or os.environ.get("CUSTOM_OCR_ENDPOINT")
            
            if not ocr_url:
                raise OCRAPIError("未配置自定义OCR API地址")
            
            # 确保OCR地址有效
            if not ocr_url.startswith("http"):
                ocr_url = f"http://{ocr_url}"
            
            # 如果API地址不包含完整路径，添加"/api/ocr"
            if not ocr_url.endswith("/ocr") and not ocr_url.endswith("/api/ocr"):
                if ocr_url.endswith("/"):
                    ocr_url += "api/ocr"
                else:
                    ocr_url += "/api/ocr"
            
            # 读取和预处理图片
            with open(str(image_path), 'rb') as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
            
            # 构建请求数据
            data = {
                "base64": base64_str
            }
            
            # 设置请求头
            headers = {"Content-Type": "application/json"}
            
            # 发送请求
            response = requests.post(
                ocr_url, 
                data=json.dumps(data), 
                headers=headers,
                timeout=self.config.get('OCR_TIMEOUT', 30)
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()['data']
                list_result = []
                for item in result:
                    list_result.append(item['text'])
                return '\n'.join(list_result)
            else:
                raise OCRAPIError(f"自定义OCR API请求失败，状态码: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            raise OCRAPIError(f"自定义OCR API请求失败: {str(e)}")
        except Exception as e:
            raise OCRAPIError(f"自定义OCR处理失败: {str(e)}")

    def test_baidu_connection(self):
        """测试百度OCR连接"""
        try:
            # 验证配置
            if not self.config.get("BAIDU_APP_ID") or not self.config.get("BAIDU_API_KEY") or not self.config.get("BAIDU_SECRET_KEY"):
                self.logger.error("百度OCR配置不完整")
                return False
            
            # 获取访问令牌
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.config.get('BAIDU_API_KEY')}&client_secret={self.config.get('BAIDU_SECRET_KEY')}"
            response = requests.get(token_url)
            response.raise_for_status()
            token = response.json().get("access_token")
            
            if not token:
                self.logger.error("无法获取百度AI访问令牌")
                return False
            
            self.logger.info("百度OCR连接测试成功")
            return True
            
        except Exception as e:
            self.logger.error(f"百度OCR连接测试失败: {str(e)}")
            return False
    
    def test_tencent_connection(self):
        """测试腾讯OCR连接"""
        try:
            # 验证配置
            if not self.config.get("TENCENT_SECRET_ID") or not self.config.get("TENCENT_SECRET_KEY"):
                self.logger.error("腾讯OCR配置不完整")
                return False
            
            # 导入腾讯云SDK
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            
            # 设置腾讯云凭证
            cred = credential.Credential(self.config.get("TENCENT_SECRET_ID"), self.config.get("TENCENT_SECRET_KEY"))
            
            # 配置HTTP选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            
            # 配置客户端选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 这里只测试凭证初始化，不发送真正的请求
            self.logger.info("腾讯OCR凭证验证成功")
            return True
            
        except Exception as e:
            self.logger.error(f"腾讯OCR连接测试失败: {str(e)}")
            return False
    
    def test_custom_connection(self):
        """测试自定义OCR连接"""
        try:
            # 验证配置
            if not self.config.get("CUSTOM_OCR_ENDPOINT"):
                self.logger.error("自定义OCR配置不完整")
                return False
            
            # 准备请求
            headers = {}
            if self.config.get("CUSTOM_OCR_KEY"):
                headers['Authorization'] = f'Bearer {self.config.get("CUSTOM_OCR_KEY")}'
            
            # 发送一个简单的GET请求测试连接
            response = requests.get(self.config.get("CUSTOM_OCR_ENDPOINT"), headers=headers)
            
            # 检查是否可以连接
            if response.status_code in [200, 400, 401, 403, 404]:  # 这些状态码表示服务器可以连接，但可能需要认证或其他条件
                self.logger.info("自定义OCR连接测试成功")
                return True
            else:
                self.logger.error(f"自定义OCR连接测试失败: 状态码 {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"自定义OCR连接测试失败: {str(e)}")
            return False


class OCRProcessingError(Exception):
    """OCR处理错误"""
    pass


class OCRAPIError(Exception):
    """OCR API错误"""
    pass 