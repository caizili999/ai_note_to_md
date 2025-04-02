import os
import io
import base64
import requests
from pathlib import Path
from PIL import Image, ImageEnhance
from typing import Optional, Dict, Any

class OCRProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        """初始化OCR处理器
        
        Args:
            config: OCR配置字典，如果为None则从环境变量读取配置
        """
        # 如果未提供配置，则从环境变量读取
        if config is None:
            config = self._load_config_from_env()
            
        self.config = config
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp']
        self.max_image_size = 4096  # 最大允许的图片尺寸
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """从环境变量加载OCR配置"""
        config = {
            "OCR_API_TYPE": os.environ.get("OCR_API_TYPE", "CUSTOM")
        }
        
        # 根据API类型加载对应的配置
        if config["OCR_API_TYPE"] == "BAIDU":
            config["BAIDU_OCR_TOKEN"] = os.environ.get("BAIDU_OCR_TOKEN", "")
        elif config["OCR_API_TYPE"] == "TENCENT":
            config["TENCENT_SECRET_ID"] = os.environ.get("TENCENT_SECRET_ID", "")
            config["TENCENT_SECRET_KEY"] = os.environ.get("TENCENT_SECRET_KEY", "")
        else:  # CUSTOM
            config["CUSTOM_OCR_ENDPOINT"] = os.environ.get("CUSTOM_OCR_ENDPOINT", "")
            config["CUSTOM_OCR_TOKEN"] = os.environ.get("CUSTOM_OCR_TOKEN", "")
            config["OCR_LANGUAGE"] = os.environ.get("OCR_LANGUAGE", "zh")
            config["OCR_TIMEOUT"] = int(os.environ.get("OCR_TIMEOUT", "30"))
            
        return config

    def preprocess_image(self, image_path: Path) -> bytes:
        """预处理图片以提高OCR识别精度"""
        with Image.open(image_path) as img:
            # 调整图片尺寸
            img.thumbnail((self.max_image_size, self.max_image_size))
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存处理后的图片到字节流
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            return img_buffer.getvalue()

    def call_ocr_api(self, image_data: bytes) -> str:
        """调用配置的OCR API"""
        api_type = self.config.get('OCR_API_TYPE', 'CUSTOM')
        base64_image = base64.b64encode(image_data).decode('utf-8')

        if api_type == "BAIDU":
            return self._call_baidu_ocr(base64_image)
        elif api_type == "TENCENT":
            return self._call_tencent_ocr(base64_image)
        else:
            return self._call_custom_ocr(base64_image)

    def _call_baidu_ocr(self, base64_image: str) -> str:
        """调用百度OCR API"""
        token = self.config.get("BAIDU_OCR_TOKEN")
        if not token:
            raise OCRAPIError("未配置百度OCR Token")
            
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        params = {
            'access_token': token
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'image': base64_image,
            'language_type': 'CHN_ENG',
            'detect_direction': 'true'
        }
        response = requests.post(url, params=params, headers=headers, data=data)
        return self._parse_baidu_response(response.json())

    def _call_tencent_ocr(self, base64_image: str) -> str:
        """调用腾讯OCR API"""
        secret_id = self.config.get("TENCENT_SECRET_ID")
        secret_key = self.config.get("TENCENT_SECRET_KEY")
        
        if not secret_id or not secret_key:
            raise OCRAPIError("未配置腾讯云SecretId或SecretKey")
            
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.ocr.v20181119 import ocr_client, models
            
            cred = credential.Credential(secret_id, secret_key)
            client = ocr_client.OcrClient(cred, "ap-guangzhou")
            
            req = models.GeneralBasicOCRRequest()
            req.ImageBase64 = base64_image
            resp = client.GeneralBasicOCR(req)
            return '\n'.join([item.DetectedText for item in resp.TextDetections])
        except ImportError:
            raise OCRAPIError("未安装腾讯云OCR SDK，请安装tencentcloud-sdk-python")
        except Exception as e:
            raise OCRAPIError(f"腾讯OCR调用失败: {str(e)}")

    def _call_custom_ocr(self, base64_image: str) -> str:
        """调用自定义OCR API"""
        endpoint = self.config.get("CUSTOM_OCR_ENDPOINT")
        token = self.config.get("CUSTOM_OCR_TOKEN")
        
        if not endpoint or not token:
            raise OCRAPIError("未配置自定义OCR API地址或Token")
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'image': base64_image,
            'config': {
                'language': self.config.get('OCR_LANGUAGE', 'zh'),
                'detect_orientation': True
            }
        }
        
        try:
            timeout = self.config.get('OCR_TIMEOUT', 30)
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            
            if 'result' in result:
                return result['result']
            elif 'error' in result:
                raise OCRAPIError(f"自定义OCR API错误: {result['error']}")
            else:
                return str(result)  # 尝试返回整个结果
        except requests.exceptions.RequestException as e:
            raise OCRAPIError(f"自定义OCR API请求失败: {str(e)}")

    def process_image(self, image_path: Path) -> str:
        """处理图片并返回识别文本"""
        if image_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"不支持的图片格式: {image_path.suffix}")

        try:
            processed_image = self.preprocess_image(image_path)
            return self.call_ocr_api(processed_image)
        except Exception as e:
            raise OCRProcessingError(f"图片处理失败: {str(e)}") from e

    @staticmethod
    def _parse_baidu_response(response: dict) -> str:
        """解析百度OCR响应"""
        if 'error_code' in response:
            raise OCRAPIError(f"百度OCR错误: {response['error_msg']}")
        return '\n'.join([item['words'] for item in response['words_result']])

class OCRProcessingError(Exception):
    pass

class OCRAPIError(Exception):
    pass
