#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   file_handler.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
文件处理工具类
负责处理文件的导入和导出
"""

import os
import docx
import PyPDF2
from pathlib import Path

# 导入OCR处理器
from ocr.ocr_processor import OCRProcessor, OCRProcessingError


class FileHandler:
    """文件处理类，用于处理不同格式的文件导入和导出"""
    
    # 支持的图像格式
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
    
    @staticmethod
    def read_text_file(file_path):
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # 尝试使用其他编码
            with open(file_path, 'r', encoding='gbk') as file:
                return file.read()
        except Exception as e:
            print(f"读取文本文件时出错: {e}")
            return None
    
    @staticmethod
    def read_docx_file(file_path):
        """读取Word文档"""
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"读取Word文档时出错: {e}")
            return None
    
    @staticmethod
    def read_pdf_file(file_path):
        """读取PDF文件"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"读取PDF文件时出错: {e}")
            return None
    
    @staticmethod
    def read_markdown_file(file_path):
        """读取Markdown文件"""
        return FileHandler.read_text_file(file_path)
    
    @staticmethod
    def read_image_file(file_path):
        """读取图片文件并使用OCR提取文本"""
        try:
            # 创建OCR处理器
            ocr_processor = OCRProcessor()
            
            # 处理图片并获取文本
            text = ocr_processor.process_image(Path(file_path))
            
            if text:
                return text
            else:
                print(f"图片OCR识别未返回文本")
                return None
        except OCRProcessingError as e:
            print(f"图片OCR处理失败: {e}")
            return None
        except Exception as e:
            print(f"读取图片文件时出错: {e}")
            return None
    
    @staticmethod
    def save_markdown_file(content, file_path):
        """保存Markdown文件"""
        try:
            # 确保目标文件夹存在
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"保存Markdown文件时出错: {e}")
            return False
    
    @staticmethod
    def read_file(file_path):
        """根据文件类型读取文件内容"""
        file_extension = Path(file_path).suffix.lower()
        
        # 文本文件
        if file_extension == '.txt':
            return FileHandler.read_text_file(file_path)
        # Word文档
        elif file_extension == '.docx':
            return FileHandler.read_docx_file(file_path)
        # PDF文件
        elif file_extension == '.pdf':
            return FileHandler.read_pdf_file(file_path)
        # Markdown文件
        elif file_extension == '.md':
            return FileHandler.read_markdown_file(file_path)
        # 图像文件
        elif file_extension in FileHandler.SUPPORTED_IMAGE_FORMATS:
            return FileHandler.read_image_file(file_path)
        else:
            print(f"不支持的文件类型: {file_extension}")
            return None 