#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口界面
AI笔记整理工具的主界面
"""

import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QComboBox, 
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, 
    QFormLayout, QLineEdit, QCheckBox, QSpinBox, QDialog
)
from PySide6.QtCore import Qt, QSize

from utils.file_handler import FileHandler
from models.ai_processor import get_processor
from utils.ocr_processor import OCRProcessor


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.setWindowTitle("AI笔记整理工具")
        self.setMinimumSize(QSize(900, 600))
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # 单文件处理选项卡
        single_file_tab = QWidget()
        tabs.addTab(single_file_tab, "单文件处理")
        
        # 批量处理选项卡
        batch_file_tab = QWidget()
        tabs.addTab(batch_file_tab, "批量处理")
        
        # 设置选项卡
        settings_tab = QWidget()
        tabs.addTab(settings_tab, "设置")
        
        # 设置单文件处理界面
        self.setup_single_file_ui(single_file_tab)
        
        # 设置批量处理界面
        self.setup_batch_file_ui(batch_file_tab)
        
        # 设置设置界面
        self.setup_settings_ui(settings_tab)
    
    def setup_single_file_ui(self, tab):
        """设置单文件处理界面"""
        layout = QVBoxLayout(tab)
        
        # 文件选择区域
        file_group = QGroupBox("导入笔记")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择按钮和显示
        file_select_layout = QHBoxLayout()
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        self.file_path_label.setPlaceholderText("选择文件或粘贴笔记内容")
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_file)
        
        file_select_layout.addWidget(self.file_path_label)
        file_select_layout.addWidget(browse_button)
        file_layout.addLayout(file_select_layout)
        
        # 笔记内容文本区域
        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在此粘贴笔记内容...")
        input_layout.addWidget(self.input_text)
        file_layout.addLayout(input_layout)
        
        layout.addWidget(file_group)
        
        # 设置区域
        options_group = QGroupBox("格式设置")
        options_layout = QFormLayout(options_group)
        
        # AI模型选择
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["Custom"])
        options_layout.addRow("AI模型:", self.ai_model_combo)
        
        # 标题级别
        self.header_level_spin = QSpinBox()
        self.header_level_spin.setRange(1, 6)
        self.header_level_spin.setValue(1)
        options_layout.addRow("标题级别:", self.header_level_spin)
        
        # 列表样式
        self.list_style_combo = QComboBox()
        self.list_style_combo.addItems(["无序列表 (-)", "有序列表 (1.)"])
        options_layout.addRow("列表样式:", self.list_style_combo)
        
        # 代码块语言
        self.code_language_edit = QLineEdit()
        self.code_language_edit.setText("text")
        options_layout.addRow("代码块默认语言:", self.code_language_edit)
        
        layout.addWidget(options_group)
        
        # 处理按钮
        process_button = QPushButton("整理笔记")
        process_button.clicked.connect(self.process_note)
        layout.addWidget(process_button)
        
        # 结果区域
        result_group = QGroupBox("Markdown结果")
        result_layout = QVBoxLayout(result_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        result_layout.addWidget(self.output_text)
        
        # 导出按钮
        export_button = QPushButton("导出Markdown")
        export_button.clicked.connect(self.export_markdown)
        result_layout.addWidget(export_button)
        
        layout.addWidget(result_group)
    
    def setup_batch_file_ui(self, tab):
        """设置批量处理界面"""
        layout = QVBoxLayout(tab)
        
        # 文件夹选择区域
        folder_group = QGroupBox("选择文件夹")
        folder_layout = QHBoxLayout(folder_group)
        
        self.folder_path_label = QLineEdit()
        self.folder_path_label.setReadOnly(True)
        self.folder_path_label.setPlaceholderText("选择包含笔记的文件夹")
        
        browse_folder_button = QPushButton("浏览...")
        browse_folder_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_path_label)
        folder_layout.addWidget(browse_folder_button)
        
        layout.addWidget(folder_group)
        
        # 文件列表
        files_group = QGroupBox("文件列表")
        files_layout = QVBoxLayout(files_group)
        
        self.files_list = QTextEdit()
        self.files_list.setReadOnly(True)
        files_layout.addWidget(self.files_list)
        
        layout.addWidget(files_group)
        
        # 批量处理按钮
        batch_process_button = QPushButton("批量处理")
        batch_process_button.clicked.connect(self.batch_process)
        layout.addWidget(batch_process_button)
        
        # 处理状态
        status_group = QGroupBox("处理状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
    
    def setup_settings_ui(self, tab):
        """设置设置界面"""
        layout = QVBoxLayout(tab)
        
        # API设置
        api_group = QGroupBox("API设置")
        api_layout = QFormLayout(api_group)
        
        # 自定义模型设置
        self.custom_model_name = QLineEdit()
        self.custom_model_name.setPlaceholderText("输入自定义模型名称")
        self.custom_base_url = QLineEdit()
        self.custom_base_url.setPlaceholderText("输入模型API地址")
        self.custom_api_key = QLineEdit()
        self.custom_api_key.setPlaceholderText("输入API密钥")
        self.custom_api_key.setEchoMode(QLineEdit.Password)
        
        api_layout.addRow("自定义模型:", self.custom_model_name)
        api_layout.addRow("模型API地址:", self.custom_base_url)
        api_layout.addRow("API密钥:", self.custom_api_key)
        
        layout.addWidget(api_group)
        
        # OCR设置
        ocr_group = QGroupBox("OCR设置")
        ocr_layout = QFormLayout(ocr_group)
        
        # OCR API类型选择
        self.ocr_api_type = QComboBox()
        self.ocr_api_type.addItems(["自定义", "百度", "腾讯"])
        self.ocr_api_type.currentIndexChanged.connect(self.on_ocr_api_type_changed)
        ocr_layout.addRow("OCR API类型:", self.ocr_api_type)
        
        # 百度OCR设置
        self.baidu_ocr_token = QLineEdit()
        self.baidu_ocr_token.setPlaceholderText("输入百度OCR Token")
        self.baidu_ocr_token.setEchoMode(QLineEdit.Password)
        ocr_layout.addRow("百度OCR Token:", self.baidu_ocr_token)
        
        # 腾讯OCR设置
        self.tencent_secret_id = QLineEdit()
        self.tencent_secret_id.setPlaceholderText("输入腾讯云SecretId")
        self.tencent_secret_id.setEchoMode(QLineEdit.Password)
        ocr_layout.addRow("腾讯云SecretId:", self.tencent_secret_id)
        
        self.tencent_secret_key = QLineEdit()
        self.tencent_secret_key.setPlaceholderText("输入腾讯云SecretKey")
        self.tencent_secret_key.setEchoMode(QLineEdit.Password)
        ocr_layout.addRow("腾讯云SecretKey:", self.tencent_secret_key)
        
        # 自定义OCR设置
        self.custom_ocr_endpoint = QLineEdit()
        self.custom_ocr_endpoint.setPlaceholderText("输入自定义OCR API地址")
        ocr_layout.addRow("自定义OCR地址:", self.custom_ocr_endpoint)
        
        self.custom_ocr_token = QLineEdit()
        self.custom_ocr_token.setPlaceholderText("输入自定义OCR Token")
        self.custom_ocr_token.setEchoMode(QLineEdit.Password)
        ocr_layout.addRow("自定义OCR Token:", self.custom_ocr_token)
        
        layout.addWidget(ocr_group)
        
        # 操作按钮布局
        button_layout = QHBoxLayout()
        # 测试按钮
        test_conn_button = QPushButton("测试连接")
        test_conn_button.clicked.connect(self.test_connection)
        button_layout.addWidget(test_conn_button)
        
        # 测试OCR按钮
        test_ocr_button = QPushButton("测试OCR")
        test_ocr_button.clicked.connect(self.test_ocr_connection)
        button_layout.addWidget(test_ocr_button)
        
        # 保存设置按钮
        save_settings_button = QPushButton("保存设置")
        save_settings_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_settings_button)
        
        layout.addLayout(button_layout)
        
        # 添加一些空白
        layout.addStretch()
        
        # 初始化显示/隐藏相关控件
        self.on_ocr_api_type_changed(0)
        
        # 加载已保存的设置
        self.load_settings()
    
    def browse_file(self):
        """浏览文件"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择笔记文件",
            "",
            "文本文件 (*.txt);;Word文档 (*.docx);;Word文档 (*.doc);;PDF文件 (*.pdf);;Markdown文件 (*.md);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            
            # 读取文件内容
            file_content = FileHandler.read_file(file_path)
            if file_content:
                self.input_text.setText(file_content)
            else:
                QMessageBox.warning(self, "读取错误", "无法读取所选文件内容")
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(
            self,
            "选择笔记文件夹",
            ""
        )
        
        if folder_path:
            self.folder_path_label.setText(folder_path)
            
            # 列出文件夹中的文件
            self.list_files_in_folder(folder_path)
    
    def list_files_in_folder(self, folder_path):
        """列出文件夹中的文件"""
        supported_extensions = ['.txt', '.doc','.docx', '.pdf', '.md']
        files = []
        
        try:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in supported_extensions:
                        files.append(file)
            
            self.files_list.setText("\n".join(files))
        except Exception as e:
            QMessageBox.warning(self, "读取文件夹错误", f"无法读取文件夹内容: {e}")
    
    def process_note(self):
        """处理笔记"""
        note_content = self.input_text.toPlainText()
        
        if not note_content:
            QMessageBox.warning(self, "输入错误", "请输入或导入笔记内容")
            return
        
        try:
            # 获取格式选项
            format_options = {
                'header_level': self.header_level_spin.value(),
                'list_style': "unordered" if self.list_style_combo.currentIndex() == 0 else "ordered",
                'code_language': self.code_language_edit.text()
            }
            
            # 获取自定义模型配置
            api_key = self.custom_api_key.text()
            base_url = self.custom_base_url.text()
            
            # 获取处理器
            processor = get_processor(api_key, base_url)
            
            # 处理笔记
            result = processor.process_note(note_content, format_options)
            
            if result:
                self.output_text.setText(result)
            else:
                QMessageBox.warning(self, "处理错误", "笔记处理失败")
        
        except Exception as e:
            QMessageBox.critical(self, "处理错误", f"处理笔记时出错: {e}")
    
    def export_markdown(self):
        """导出Markdown"""
        markdown_content = self.output_text.toPlainText()
        
        if not markdown_content:
            QMessageBox.warning(self, "导出错误", "没有可导出的内容")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "导出Markdown",
            "",
            "Markdown文件 (*.md)"
        )
        
        if file_path:
            if not file_path.endswith('.md'):
                file_path += '.md'
            
            if FileHandler.save_markdown_file(markdown_content, file_path):
                QMessageBox.information(self, "导出成功", f"Markdown已成功导出到: {file_path}")
            else:
                QMessageBox.warning(self, "导出错误", "导出Markdown时出错")
    
    def batch_process(self):
        """批量处理文件"""
        folder_path = self.folder_path_label.text()
        
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "输入错误", "请选择有效的文件夹")
            return
        
        # 确认是否进行批量处理
        reply = QMessageBox.question(
            self,
            "确认",
            "确认批量处理所选文件夹中的所有支持文件?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            # 获取格式选项
            format_options = {
                'header_level': self.header_level_spin.value(),
                'list_style': "unordered" if self.list_style_combo.currentIndex() == 0 else "ordered",
                'code_language': self.code_language_edit.text()
            }
            
            # 获取自定义模型配置
            api_key = self.custom_api_key.text()
            base_url = self.custom_base_url.text()
            
            # 获取处理器
            processor = get_processor(api_key, base_url)
            
            # 处理文件夹中的文件
            self.status_text.clear()
            self.status_text.append("开始批量处理...")
            
            supported_extensions = ['.txt', '.doc','.docx', '.pdf', '.md']
            output_folder = os.path.join(folder_path, "markdown_output")
            
            # 创建输出文件夹
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # 处理每个文件
            files_processed = 0
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in supported_extensions:
                        self.status_text.append(f"处理: {file}")
                        
                        # 读取文件内容
                        file_content = FileHandler.read_file(file_path)
                        if not file_content:
                            self.status_text.append(f"  - 错误: 无法读取文件内容")
                            continue
                        
                        # 处理笔记
                        result = processor.process_note(file_content, format_options)
                        if not result:
                            self.status_text.append(f"  - 错误: 处理失败")
                            continue
                        
                        # 保存结果
                        output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.md")
                        if FileHandler.save_markdown_file(result, output_file):
                            self.status_text.append(f"  - 成功: 已保存到 {output_file}")
                            files_processed += 1
                        else:
                            self.status_text.append(f"  - 错误: 保存失败")
            
            self.status_text.append(f"批量处理完成。成功处理了 {files_processed} 个文件。")
            self.status_text.append(f"输出文件夹: {output_folder}")
            
            # 显示完成消息
            QMessageBox.information(
                self, 
                "批量处理完成", 
                f"成功处理了 {files_processed} 个文件。\n输出文件夹: {output_folder}"
            )
        
        except Exception as e:
            self.status_text.append(f"错误: {e}")
            QMessageBox.critical(self, "处理错误", f"批量处理时出错: {e}")
    
    def test_connection(self):
        """测试API连接"""
        try:
            # 自定义模型参数检查
            model_name = self.custom_model_name.text()
            base_url = self.custom_base_url.text()
            if not model_name or not base_url:
                QMessageBox.warning(self, "测试失败", "请输入自定义模型名称和API地址")
                return
            
            # 获取自定义模型配置
            api_key = self.custom_api_key.text()
            base_url = self.custom_base_url.text()
            
            # 创建处理器实例
            processor = get_processor(api_key, base_url)
            
            # 执行连接测试并获取原始响应
            answer = processor.test_connection()
            
            # 显示原始响应结果
            result_msg = f"响应结果:\n{answer}"
            
            if result_msg:
                QMessageBox.information(self, "连接成功", result_msg)
            else:
                QMessageBox.critical(self, "连接失败", result_msg)
        
        except Exception as e:
            QMessageBox.critical(self, "测试错误", f"连接测试时发生错误: {str(e)}")

    def save_settings(self):
        """保存设置"""
        # 保存自定义模型设置
        if self.custom_model_name.text():
            os.environ["CUSTOM_MODEL_NAME"] = self.custom_model_name.text()
            os.environ["CUSTOM_BASE_URL"] = self.custom_base_url.text()
        
        # 保存OCR设置
        # 保存OCR API类型
        ocr_api_type_map = ["CUSTOM", "BAIDU", "TENCENT"]
        os.environ["OCR_API_TYPE"] = ocr_api_type_map[self.ocr_api_type.currentIndex()]
        
        # 保存百度OCR设置
        if self.baidu_ocr_token.text():
            os.environ["BAIDU_OCR_TOKEN"] = self.baidu_ocr_token.text()
            
        # 保存腾讯OCR设置
        if self.tencent_secret_id.text() and self.tencent_secret_key.text():
            os.environ["TENCENT_SECRET_ID"] = self.tencent_secret_id.text()
            os.environ["TENCENT_SECRET_KEY"] = self.tencent_secret_key.text()
            
        # 保存自定义OCR设置
        if self.custom_ocr_endpoint.text():
            os.environ["CUSTOM_OCR_ENDPOINT"] = self.custom_ocr_endpoint.text()
        if self.custom_ocr_token.text():
            os.environ["CUSTOM_OCR_TOKEN"] = self.custom_ocr_token.text()
        
        # 将设置保存到配置文件
        self._save_settings_to_file()
        
        QMessageBox.information(self, "设置保存", "设置已成功保存")

    def on_ocr_api_type_changed(self, index):
        """处理OCR API类型变化"""
        # 根据选择的OCR API类型，显示或隐藏相应的设置控件
        if index == 0:  # 自定义
            self.baidu_ocr_token.setVisible(False)
            self.tencent_secret_id.setVisible(False)
            self.tencent_secret_key.setVisible(False)
            self.custom_ocr_endpoint.setVisible(True)
            self.custom_ocr_token.setVisible(True)
        elif index == 1:  # 百度
            self.baidu_ocr_token.setVisible(True)
            self.tencent_secret_id.setVisible(False)
            self.tencent_secret_key.setVisible(False)
            self.custom_ocr_endpoint.setVisible(False)
            self.custom_ocr_token.setVisible(False)
        elif index == 2:  # 腾讯
            self.baidu_ocr_token.setVisible(False)
            self.tencent_secret_id.setVisible(True)
            self.tencent_secret_key.setVisible(True)
            self.custom_ocr_endpoint.setVisible(False)
            self.custom_ocr_token.setVisible(False)

    def test_ocr_connection(self):
        """测试OCR连接"""
        try:
            from pathlib import Path
            from utils.ocr_processor import OCRProcessor
            
            # 获取OCR类型和配置
            ocr_api_type_map = ["CUSTOM", "BAIDU", "TENCENT"]
            ocr_api_type = ocr_api_type_map[self.ocr_api_type.currentIndex()]
            
            # 构建配置字典
            config = {
                "OCR_API_TYPE": ocr_api_type
            }
            
            # 根据OCR类型添加不同的配置项
            if ocr_api_type == "BAIDU":
                if not self.baidu_ocr_token.text():
                    QMessageBox.warning(self, "测试失败", "请输入百度OCR Token")
                    return
                config["BAIDU_OCR_TOKEN"] = self.baidu_ocr_token.text()
            
            elif ocr_api_type == "TENCENT":
                if not self.tencent_secret_id.text() or not self.tencent_secret_key.text():
                    QMessageBox.warning(self, "测试失败", "请输入腾讯云SecretId和SecretKey")
                    return
                config["TENCENT_SECRET_ID"] = self.tencent_secret_id.text()
                config["TENCENT_SECRET_KEY"] = self.tencent_secret_key.text()
            
            else:  # CUSTOM
                if not self.custom_ocr_endpoint.text() or not self.custom_ocr_token.text():
                    QMessageBox.warning(self, "测试失败", "请输入自定义OCR API地址和Token")
                    return
                config["CUSTOM_OCR_ENDPOINT"] = self.custom_ocr_endpoint.text()
                config["CUSTOM_OCR_TOKEN"] = self.custom_ocr_token.text()
            
            # 创建OCR处理器
            ocr_processor = OCRProcessor(config)
            
            # 弹出文件选择对话框，让用户选择一个图片进行测试
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "选择测试图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if not file_path:
                return
            
            # 显示等待提示
            QMessageBox.information(self, "测试中", "正在测试OCR功能，请稍候...")
            
            # 进行OCR处理
            result = ocr_processor.process_image(Path(file_path))
            
            if result:
                # 显示结果对话框
                result_dialog = QDialog(self)
                result_dialog.setWindowTitle("OCR测试结果")
                result_dialog.setMinimumSize(500, 400)
                
                layout = QVBoxLayout(result_dialog)
                
                result_text = QTextEdit()
                result_text.setReadOnly(True)
                result_text.setText(result)
                layout.addWidget(result_text)
                
                close_button = QPushButton("关闭")
                close_button.clicked.connect(result_dialog.accept)
                layout.addWidget(close_button)
                
                result_dialog.exec()
            else:
                QMessageBox.warning(self, "测试失败", "OCR处理失败，未返回结果")
                
        except Exception as e:
            QMessageBox.critical(self, "测试错误", f"OCR测试时发生错误: {str(e)}")

    def load_settings(self):
        """加载已保存的设置"""
        # 加载自定义模型设置
        self.custom_model_name.setText(os.environ.get("CUSTOM_MODEL_NAME", ""))
        self.custom_base_url.setText(os.environ.get("CUSTOM_BASE_URL", ""))
        self.custom_api_key.setText(os.environ.get("CUSTOM_API_KEY", ""))
        
        # 加载OCR API类型
        ocr_api_type = os.environ.get("OCR_API_TYPE", "CUSTOM")
        if ocr_api_type == "BAIDU":
            self.ocr_api_type.setCurrentIndex(1)
        elif ocr_api_type == "TENCENT":
            self.ocr_api_type.setCurrentIndex(2)
        else:
            self.ocr_api_type.setCurrentIndex(0)
        
        # 加载百度OCR设置
        self.baidu_ocr_token.setText(os.environ.get("BAIDU_OCR_TOKEN", ""))
        
        # 加载腾讯OCR设置
        self.tencent_secret_id.setText(os.environ.get("TENCENT_SECRET_ID", ""))
        self.tencent_secret_key.setText(os.environ.get("TENCENT_SECRET_KEY", ""))
        
        # 加载自定义OCR设置
        self.custom_ocr_endpoint.setText(os.environ.get("CUSTOM_OCR_ENDPOINT", ""))
        self.custom_ocr_token.setText(os.environ.get("CUSTOM_OCR_TOKEN", ""))
        
        # 尝试从配置文件加载设置
        self._load_settings_from_file()
    
    def _save_settings_to_file(self):
        """将设置保存到配置文件"""
        try:
            import json
            from pathlib import Path
            
            # 创建设置目录
            config_dir = Path.home() / ".ai_note_to_md"
            config_dir.mkdir(exist_ok=True)
            
            # 保存设置到文件
            config_file = config_dir / "settings.json"
            
            # 收集设置
            settings = {
                # 模型设置
                "CUSTOM_MODEL_NAME": self.custom_model_name.text(),
                "CUSTOM_BASE_URL": self.custom_base_url.text(),
                
                # OCR设置
                "OCR_API_TYPE": ["CUSTOM", "BAIDU", "TENCENT"][self.ocr_api_type.currentIndex()],
                "BAIDU_OCR_TOKEN": self.baidu_ocr_token.text(),
                "TENCENT_SECRET_ID": self.tencent_secret_id.text(),
                "TENCENT_SECRET_KEY": self.tencent_secret_key.text(),
                "CUSTOM_OCR_ENDPOINT": self.custom_ocr_endpoint.text(),
                "CUSTOM_OCR_TOKEN": self.custom_ocr_token.text()
            }
            
            # 写入文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存设置到文件时出错: {e}")
    
    def _load_settings_from_file(self):
        """从配置文件加载设置"""
        try:
            import json
            from pathlib import Path
            
            # 设置文件路径
            config_file = Path.home() / ".ai_note_to_md" / "settings.json"
            
            # 检查文件是否存在
            if not config_file.exists():
                return
            
            # 读取设置
            with open(config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 应用模型设置
            if "CUSTOM_MODEL_NAME" in settings:
                self.custom_model_name.setText(settings["CUSTOM_MODEL_NAME"])
                os.environ["CUSTOM_MODEL_NAME"] = settings["CUSTOM_MODEL_NAME"]
            
            if "CUSTOM_BASE_URL" in settings:
                self.custom_base_url.setText(settings["CUSTOM_BASE_URL"])
                os.environ["CUSTOM_BASE_URL"] = settings["CUSTOM_BASE_URL"]
            
            # 应用OCR设置
            if "OCR_API_TYPE" in settings:
                ocr_type = settings["OCR_API_TYPE"]
                if ocr_type == "BAIDU":
                    self.ocr_api_type.setCurrentIndex(1)
                elif ocr_type == "TENCENT":
                    self.ocr_api_type.setCurrentIndex(2)
                else:
                    self.ocr_api_type.setCurrentIndex(0)
                os.environ["OCR_API_TYPE"] = ocr_type
            
            # 百度OCR设置
            if "BAIDU_OCR_TOKEN" in settings:
                self.baidu_ocr_token.setText(settings["BAIDU_OCR_TOKEN"])
                os.environ["BAIDU_OCR_TOKEN"] = settings["BAIDU_OCR_TOKEN"]
            
            # 腾讯OCR设置
            if "TENCENT_SECRET_ID" in settings:
                self.tencent_secret_id.setText(settings["TENCENT_SECRET_ID"])
                os.environ["TENCENT_SECRET_ID"] = settings["TENCENT_SECRET_ID"]
            
            if "TENCENT_SECRET_KEY" in settings:
                self.tencent_secret_key.setText(settings["TENCENT_SECRET_KEY"])
                os.environ["TENCENT_SECRET_KEY"] = settings["TENCENT_SECRET_KEY"]
            
            # 自定义OCR设置
            if "CUSTOM_OCR_ENDPOINT" in settings:
                self.custom_ocr_endpoint.setText(settings["CUSTOM_OCR_ENDPOINT"])
                os.environ["CUSTOM_OCR_ENDPOINT"] = settings["CUSTOM_OCR_ENDPOINT"]
            
            if "CUSTOM_OCR_TOKEN" in settings:
                self.custom_ocr_token.setText(settings["CUSTOM_OCR_TOKEN"])
                os.environ["CUSTOM_OCR_TOKEN"] = settings["CUSTOM_OCR_TOKEN"]
                
        except Exception as e:
            print(f"从文件加载设置时出错: {e}")
