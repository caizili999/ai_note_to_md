#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
OCR模块
"""

# 导出OCR处理器和异常类
from .ocr_processor import OCRProcessor, OCRProcessingError, OCRAPIError

__all__ = ["OCRProcessor", "OCRProcessingError", "OCRAPIError"] 