#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理工具类
负责处理文件的导入和导出
"""

import os
import docx
import win32com.client as wc
import PyPDF2
from pathlib import Path


class FileHandler:
    """文件处理类，用于处理不同格式的文件导入和导出"""
    
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
            # 读取Word文档,如果结尾是.docx
            if file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                return '\n'.join(full_text)
            
            # 读取Word文档,如果结尾是.doc
            elif file_path.endswith('.doc'):
                #doc文件另存为docx
                word = wc.Dispatch("Word.Application")
                doc = word.Documents.Open(file_path)
                # 12代表转换后为docx文件
                doc.SaveAs(file_path.replace('.doc', '.docx'), 12)
                doc.Close
                word.Quit
                doc = docx.Document(file_path.replace('.doc', '.docx'))
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
    def save_markdown_file(content, file_path):
        """保存Markdown文件"""
        try:
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
        
        if file_extension == '.txt':
            return FileHandler.read_text_file(file_path)
        elif file_extension == '.docx' or file_extension == '.doc':
            return FileHandler.read_docx_file(file_path)
        elif file_extension == '.pdf':
            return FileHandler.read_pdf_file(file_path)
        elif file_extension == '.md':
            return FileHandler.read_markdown_file(file_path)
        else:
            print(f"不支持的文件类型: {file_extension}")
            return None 