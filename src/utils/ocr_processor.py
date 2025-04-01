import os
import io
import base64
import requests
from pathlib import Path
from PIL import Image, ImageEnhance
from typing import Optional, Dict, Any

class OCRProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp']
        self.max_image_size = 4096  # 最大允许的图片尺寸

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

        if api_type == 'BAIDU':
            return self._call_baidu_ocr(base64_image)
        elif api_type == 'TENCENT':
            return self._call_tencent_ocr(base64_image)
        else:
            return self._call_custom_ocr(base64_image)

    def _call_baidu_ocr(self, base64_image: str) -> str:
        """调用百度OCR API"""
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        params = {
            'access_token': self.config['BAIDU_OCR_TOKEN']
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
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.ocr.v20181119 import ocr_client, models
        
        cred = credential.Credential(
            self.config['TENCENT_SECRET_ID'],
            self.config['TENCENT_SECRET_KEY']
        )
        client = ocr_client.OcrClient(cred, "ap-guangzhou")
        
        req = models.GeneralBasicOCRRequest()
        req.ImageBase64 = base64_image
        resp = client.GeneralBasicOCR(req)
        return '\n'.join([item.DetectedText for item in resp.TextDetections])

    def _call_custom_ocr(self, base64_image: str) -> str:
        """调用自定义OCR API"""
        headers = {
            'Authorization': f'Bearer {self.config["CUSTOM_OCR_TOKEN"]}',
            'Content-Type': 'application/json'
        }
        payload = {
            'image': base64_image,
            'config': {
                'language': self.config.get('OCR_LANGUAGE', 'zh'),
                'detect_orientation': True
            }
        }
        response = requests.post(
            self.config['CUSTOM_OCR_ENDPOINT'],
            json=payload,
            headers=headers,
            timeout=self.config.get('OCR_TIMEOUT', 30)
        )
        return response.json()['result']

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
