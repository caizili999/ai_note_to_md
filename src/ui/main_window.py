#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   main_window.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
主窗口界面
AI笔记整理工具的主界面
"""

import os
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QComboBox, 
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, 
    QFormLayout, QLineEdit, QCheckBox, QSpinBox, QDialog,
    QApplication, QProgressDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices

from utils.file_handler import FileHandler
from models.ai_processor import get_processor
from ocr.ocr_processor import OCRProcessor


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.setWindowTitle("AI笔记整理工具")
        self.setMinimumSize(QSize(900, 600))
        
        # 初始化状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("准备就绪", 5000)
        
        # 初始化模型信息字典
        self.models_info = {}
        
        # 初始化UI组件
        self.init_ui()
        
        # 使用QTimer延迟加载设置，确保UI组件已完全创建
        QTimer.singleShot(100, self.delayed_load_settings)
    
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
        self.ai_model_combo.setToolTip("选择要使用的AI模型")
        options_layout.addRow("AI模型:", self.ai_model_combo)
        
        # 提示词模板
        self.prompt_template_edit = QTextEdit()
        self.prompt_template_edit.setPlaceholderText("输入提示词模板...")
        self.prompt_template_edit.setText("请将以下笔记内容转换为Markdown格式:\n\n")
        self.prompt_template_edit.setMaximumHeight(80)
        options_layout.addRow("提示词模板:", self.prompt_template_edit)
        
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
        api_layout = QVBoxLayout(api_group)  # 改为垂直布局
        
        # 模型列表区域
        models_group = QGroupBox("模型列表")
        models_layout = QVBoxLayout(models_group)
        
        # 添加模型列表
        self.models_list = QListWidget()
        self.models_list.setSelectionMode(QListWidget.SingleSelection)
        self.models_list.itemSelectionChanged.connect(self.on_model_selected)
        models_layout.addWidget(self.models_list)
        
        # 模型操作按钮
        models_buttons_layout = QHBoxLayout()
        self.add_model_button = QPushButton("添加模型")
        self.add_model_button.clicked.connect(self.add_new_model)
        self.remove_model_button = QPushButton("删除模型")
        self.remove_model_button.clicked.connect(self.remove_selected_model)
        models_buttons_layout.addWidget(self.add_model_button)
        models_buttons_layout.addWidget(self.remove_model_button)
        models_layout.addLayout(models_buttons_layout)
        
        models_group.setLayout(models_layout)
        api_layout.addWidget(models_group)
        
        # 自定义模型详细设置
        model_details_group = QGroupBox("模型详细设置")
        model_details_layout = QFormLayout(model_details_group)
        
        self.custom_model_name = QLineEdit()
        self.custom_model_name.setPlaceholderText("输入自定义模型名称")
        self.custom_model_display_name = QLineEdit()
        self.custom_model_display_name.setPlaceholderText("输入显示名称")
        self.custom_base_url = QLineEdit()
        self.custom_base_url.setPlaceholderText("输入模型API地址")
        self.custom_api_key = QLineEdit()
        self.custom_api_key.setPlaceholderText("输入API密钥")
        self.custom_api_key.setEchoMode(QLineEdit.Password)
        
        model_details_layout.addRow("模型名称:", self.custom_model_name)
        model_details_layout.addRow("显示名称:", self.custom_model_display_name)
        model_details_layout.addRow("API地址:", self.custom_base_url)
        model_details_layout.addRow("API密钥:", self.custom_api_key)
        
        # 保存模型按钮
        self.save_model_button = QPushButton("保存模型设置")
        self.save_model_button.clicked.connect(self.save_model_details)
        model_details_layout.addRow("", self.save_model_button)
        
        # 测试连接按钮
        test_button = QPushButton("测试AI连接")
        test_button.clicked.connect(self.test_connection)
        model_details_layout.addRow("", test_button)
        
        model_details_group.setLayout(model_details_layout)
        api_layout.addWidget(model_details_group)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # OCR设置
        ocr_group = QGroupBox("OCR设置")
        ocr_layout = QVBoxLayout(ocr_group)  # 使用垂直布局
        
        # OCR API类型选择 - 放在顶部
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("OCR API类型:"))
        self.ocr_api_type = QComboBox()
        self.ocr_api_type.addItems(["自定义", "百度", "腾讯"])
        self.ocr_api_type.currentIndexChanged.connect(self.on_ocr_api_type_changed)
        type_layout.addWidget(self.ocr_api_type)
        type_layout.addStretch()  # 添加弹簧，使控件左对齐
        ocr_layout.addLayout(type_layout)
        
        # 创建百度OCR设置控件
        self.baidu_app_id = QLineEdit()
        self.baidu_app_id.setPlaceholderText("APP_ID")
        self.baidu_api_key = QLineEdit()
        self.baidu_api_key.setPlaceholderText("API_KEY")
        self.baidu_secret_key = QLineEdit()
        self.baidu_secret_key.setPlaceholderText("SECRET_KEY")
        self.baidu_secret_key.setEchoMode(QLineEdit.Password)
        
        # 创建腾讯OCR设置控件
        self.tencent_secret_id = QLineEdit()
        self.tencent_secret_id.setPlaceholderText("SecretId")
        self.tencent_secret_key = QLineEdit()
        self.tencent_secret_key.setPlaceholderText("SecretKey")
        self.tencent_secret_key.setEchoMode(QLineEdit.Password)
        self.tencent_region = QLineEdit()
        self.tencent_region.setPlaceholderText("OCR区域")
        self.tencent_region.setText("ap-beijing")
        
        # 创建自定义OCR设置控件
        self.custom_ocr_url = QLineEdit()
        self.custom_ocr_url.setPlaceholderText("OCRAPI地址")
        self.custom_ocr_key = QLineEdit()
        self.custom_ocr_key.setPlaceholderText("OCRAPI密钥")
        self.custom_ocr_key.setEchoMode(QLineEdit.Password)
        
        # 初始显示自定义OCR设置
        self.baidu_ocr_settings = [self.baidu_app_id, self.baidu_api_key, self.baidu_secret_key]
        self.tencent_ocr_settings = [self.tencent_secret_id, self.tencent_secret_key, self.tencent_region]
        self.custom_ocr_settings = [self.custom_ocr_url, self.custom_ocr_key]
        
        # 创建每种OCR设置的QGroupBox，使布局更清晰
        # 百度OCR设置
        self.baidu_group = QGroupBox("百度OCR配置")
        self.baidu_ocr_form = QFormLayout(self.baidu_group)
        self.baidu_ocr_form.addRow("APP_ID:", self.baidu_app_id)
        self.baidu_ocr_form.addRow("API_KEY:", self.baidu_api_key)
        self.baidu_ocr_form.addRow("SECRET_KEY:", self.baidu_secret_key)
        
        # 腾讯OCR设置
        self.tencent_group = QGroupBox("腾讯OCR配置")
        self.tencent_ocr_form = QFormLayout(self.tencent_group)
        self.tencent_ocr_form.addRow("SecretId:", self.tencent_secret_id)
        self.tencent_ocr_form.addRow("SecretKey:", self.tencent_secret_key)
        self.tencent_ocr_form.addRow("区域:", self.tencent_region)
        
        # 自定义OCR设置
        self.custom_group = QGroupBox("自定义OCR配置")
        self.custom_ocr_form = QFormLayout(self.custom_group)
        self.custom_ocr_form.addRow("API地址:", self.custom_ocr_url)
        self.custom_ocr_form.addRow("API密钥:", self.custom_ocr_key)
        
        # 添加OCR配置框架
        self.ocr_settings_widget = QWidget()
        self.ocr_settings_layout = QVBoxLayout(self.ocr_settings_widget)
        ocr_layout.addWidget(self.ocr_settings_widget)
        
        # 隐藏所有OCR配置组
        self.baidu_group.hide()
        self.tencent_group.hide()
        self.custom_group.hide()
        
        # 显示选中的OCR设置表单
        self.on_ocr_api_type_changed(0)  # 默认显示自定义OCR
        
        # 添加测试OCR连接按钮
        self.test_ocr_button = QPushButton("测试OCR连接")
        self.test_ocr_button.clicked.connect(self.test_ocr_connection)
        ocr_layout.addWidget(self.test_ocr_button)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # 保存和加载设置按钮
        buttons_layout = QHBoxLayout()
        save_settings_button = QPushButton("保存设置")
        save_settings_button.clicked.connect(self.save_settings)
        load_settings_button = QPushButton("加载设置")
        load_settings_button.clicked.connect(self.load_settings)
        
        buttons_layout.addWidget(save_settings_button)
        buttons_layout.addWidget(load_settings_button)
        layout.addLayout(buttons_layout)
        
        # 添加"关注我，请我喝咖啡"按钮
        support_button = QPushButton("点击关注我，多多star，感谢支持")
        support_button.setStyleSheet("QPushButton {background-color: #24292e; color: white; font-weight: bold; padding: 8px;}")
        support_button.setCursor(Qt.PointingHandCursor)
        support_button.clicked.connect(self.open_github_page)
        layout.addWidget(support_button)
        
        # 添加拉伸空间
        layout.addStretch()
    
    def browse_file(self):
        """浏览文件"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择笔记文件",
            "",
            "文本文件 (*.txt);;Word文档 (*.docx);;PDF文件 (*.pdf);;Markdown文件 (*.md);;图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            
            # 判断是否为图像文件
            file_extension = Path(file_path).suffix.lower()
            is_image = file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
            
            # 创建进度对话框
            progress_title = "OCR识别中" if is_image else "读取文件中"
            progress = QProgressDialog(f"{progress_title}...", "取消", 0, 100, self)
            progress.setWindowTitle("文件处理进度")
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(0)
            progress.show()
            
            # 更新进度的计时器
            timer = QTimer(self)
            progress_value = 0
            
            def update_progress():
                nonlocal progress_value
                if progress_value < 90:
                    progress_value += (5 if is_image else 10)  # OCR处理较慢，进度更新慢一些
                    progress.setValue(progress_value)
            
            # 定时更新进度
            timer.timeout.connect(update_progress)
            timer.start(200)  # 每200毫秒更新一次
            
            try:
                if is_image:
                    self.status_bar.showMessage(f"正在进行OCR识别，可能需要一些时间...")
                    self.update()  # 刷新UI
                    
                    # 显示图像预览
                    self.show_image_preview(file_path)
                
                # 读取文件内容
                file_content = FileHandler.read_file(file_path)
                
                # 停止计时器，完成进度
                timer.stop()
                progress.setValue(100)
                
                if file_content:
                    self.input_text.setText(file_content)
                    
                    # 如果是图像文件，显示提示
                    if is_image:
                        self.status_bar.showMessage(f"OCR识别完成", 5000)
                else:
                    QMessageBox.warning(self, "读取错误", "无法读取所选文件内容")
            except Exception as e:
                # 停止计时器
                timer.stop()
                progress.close()
                
                QMessageBox.warning(self, "读取错误", f"文件处理异常: {str(e)}")
                self.status_bar.showMessage(f"文件处理异常: {str(e)}", 5000)

    def show_image_preview(self, image_path):
        """显示图像预览"""
        try:
            # 创建图像预览对话框
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("图像预览")
            preview_dialog.setMinimumSize(600, 400)
            
            # 创建布局
            layout = QVBoxLayout(preview_dialog)
            
            # 添加图像标签
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            
            # 等比缩放图像
            scaled_pixmap = pixmap.scaled(
                580, 350, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 添加关闭按钮
            close_button = QPushButton("关闭")
            close_button.clicked.connect(preview_dialog.close)
            
            # 将组件添加到布局
            layout.addWidget(QLabel(f"文件: {Path(image_path).name}"))
            layout.addWidget(image_label)
            layout.addWidget(close_button)
            
            # 非模态显示对话框
            preview_dialog.setModal(False)
            preview_dialog.show()
        except Exception as e:
            self.status_bar.showMessage(f"无法显示图像预览: {str(e)}", 5000)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "选择包含笔记的文件夹")
        
        if folder_path:
            self.folder_path_label.setText(folder_path)
            self.files_list.clear()
            
            # 查找文件夹中所有支持的文件
            supported_files = []
            
            # 获取支持的文件扩展名
            text_extensions = [".txt", ".docx", ".pdf", ".md"]
            image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"]
            all_extensions = text_extensions + image_extensions
            
            # 查找所有支持的文件
            for ext in all_extensions:
                files = list(Path(folder_path).glob(f"*{ext}"))
                supported_files.extend(files)
            
            # 在文件列表中显示找到的文件
            if supported_files:
                self.files_list.append(f"找到 {len(supported_files)} 个文件:")
                for i, file in enumerate(supported_files, 1):
                    file_type = "文本文件" if file.suffix.lower() in text_extensions else "图像文件"
                    self.files_list.append(f"{i}. {file.name} ({file_type})")
            else:
                self.files_list.append("未找到支持的文件。")
                
            # 保存文件列表供批处理使用
            self.supported_files = supported_files
    
    def batch_process(self):
        """批量处理文件"""
        folder_path = self.folder_path_label.text()
        
        if not folder_path:
            QMessageBox.warning(self, "错误", "请先选择一个文件夹。")
            return
        
        if not hasattr(self, "supported_files") or not self.supported_files:
            QMessageBox.warning(self, "错误", "所选文件夹中没有找到支持的文件。")
            return
        
        # 检查是否选择了模型
        selected_model_index = self.ai_model_combo.currentIndex()
        if selected_model_index < 0:
            QMessageBox.warning(self, "模型选择错误", "请先在设置中添加并选择一个AI模型")
            return
        
        # 获取选中的模型信息
        selected_model_id = self.ai_model_combo.currentData()
        if not selected_model_id or selected_model_id not in self.models_info:
            QMessageBox.warning(self, "模型错误", "所选模型无效，请重新选择")
            return
        
        model_info = self.models_info[selected_model_id]
        api_key = model_info.get("api_key", "")
        base_url = model_info.get("base_url", "")
        model_name = model_info.get("name", "")
        
        # 清空状态文本区域
        self.status_text.clear()
        self.status_text.append("开始批量处理...")
        self.status_text.append(f"使用模型: {model_info.get('display_name', '未命名模型')}")
        self.status_bar.showMessage("批量处理中...", 0)  # 0表示不会自动消失
        
        # 记录处理计数
        success_count = 0
        failed_count = 0
        image_count = 0
        
        # 获取输出文件夹（默认为源文件夹中的"markdown_output"子文件夹）
        output_folder = Path(folder_path) / "markdown_output"
        output_folder.mkdir(exist_ok=True)
        
        # 创建总体进度对话框
        total_files = len(self.supported_files)
        progress = QProgressDialog(f"批量处理 0/{total_files} 文件...", "取消", 0, total_files, self)
        progress.setWindowTitle("批量处理进度")
        progress.setWindowModality(Qt.WindowModal)
        progress.setValue(0)
        progress.show()
        
        # 批量处理所有文件
        for file_index, file in enumerate(self.supported_files):
            try:
                # 更新总体进度
                progress.setValue(file_index)
                progress.setLabelText(f"批量处理 {file_index}/{total_files} 文件...\n当前: {file.name}")
                QApplication.processEvents()  # 确保UI更新
                
                if progress.wasCanceled():
                    self.status_text.append("用户取消了处理")
                    break
                
                self.status_text.append(f"处理文件: {file.name}...")
                
                # 区分图片和文本文件
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
                    self.status_text.append(f"  进行OCR识别...")
                    image_count += 1
                
                # 创建文件读取进度对话框
                file_progress = QProgressDialog(f"读取文件: {file.name}", "取消", 0, 100, self)
                file_progress.setWindowTitle("文件读取进度")
                file_progress.setWindowModality(Qt.WindowModal)
                file_progress.setValue(0)
                file_progress.show()
                
                # 更新文件读取进度的计时器
                file_timer = QTimer(self)
                file_progress_value = 0
                
                def update_file_progress():
                    nonlocal file_progress_value
                    if file_progress_value < 90:
                        file_progress_value += 10
                        file_progress.setValue(file_progress_value)
                
                # 定时更新进度
                file_timer.timeout.connect(update_file_progress)
                file_timer.start(200)  # 每200毫秒更新一次
                
                # 读取文件内容
                content = FileHandler.read_file(str(file))
                
                # 停止计时器，完成文件读取进度
                file_timer.stop()
                file_progress.setValue(100)
                
                if not content:
                    self.status_text.append(f"  错误: 无法读取文件内容")
                    failed_count += 1
                    continue
                
                # 使用AI处理内容
                processor = get_processor(api_key, base_url)
                processor.model_name = model_name  # 设置模型名称
                result = processor.process_note(
                    content,
                    {
                        'header_level': self.header_level_spin.value(),
                        'list_style': "unordered" if self.list_style_combo.currentIndex() == 0 else "ordered",
                        'code_language': self.code_language_edit.text(),
                        'prompt_template': self.prompt_template_edit.toPlainText()
                    }
                )
                
                # 生成输出文件路径
                output_file = output_folder / f"{file.stem}.md"
                
                # 保存结果
                FileHandler.save_markdown_file(result, str(output_file))
                
                self.status_text.append(f"  成功: 已保存到 {output_file.name}")
                success_count += 1
                
            except Exception as e:
                self.status_text.append(f"  错误: {str(e)}")
                failed_count += 1
        
        # 完成总体进度
        progress.setValue(total_files)
        
        # 显示处理结果
        self.status_text.append("\n处理完成:")
        self.status_text.append(f"共处理 {len(self.supported_files)} 个文件")
        self.status_text.append(f"其中图像文件: {image_count} 个")
        self.status_text.append(f"成功: {success_count} 个")
        self.status_text.append(f"失败: {failed_count} 个")
        self.status_text.append(f"输出目录: {output_folder}")
        
        self.status_bar.showMessage(f"批量处理完成: 成功{success_count}个, 失败{failed_count}个", 10000)
    
    def process_note(self):
        """处理笔记"""
        note_content = self.input_text.toPlainText()
        
        if not note_content:
            QMessageBox.warning(self, "输入错误", "请输入或导入笔记内容")
            return
        
        # 检查是否选择了模型
        selected_model_index = self.ai_model_combo.currentIndex()
        if selected_model_index < 0:
            QMessageBox.warning(self, "模型选择错误", "请先在设置中添加并选择一个AI模型")
            return
        
        try:
            # 获取选中的模型信息
            selected_model_id = self.ai_model_combo.currentData()
            if not selected_model_id or selected_model_id not in self.models_info:
                QMessageBox.warning(self, "模型错误", "所选模型无效，请重新选择")
                return
            
            model_info = self.models_info[selected_model_id]
            api_key = model_info.get("api_key", "")
            base_url = model_info.get("base_url", "")
            model_name = model_info.get("name", "")
            
            # 获取格式选项
            format_options = {
                'header_level': self.header_level_spin.value(),
                'list_style': "unordered" if self.list_style_combo.currentIndex() == 0 else "ordered",
                'code_language': self.code_language_edit.text(),
                'prompt_template': self.prompt_template_edit.toPlainText()
            }
            
            # 获取处理器
            processor = get_processor(api_key, base_url)
            processor.model_name = model_name  # 设置模型名称
            
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
        """保存设置到环境变量和配置文件"""
        try:
            # 保存OCR配置
            ocr_api_type = ["CUSTOM", "BAIDU", "TENCENT"][self.ocr_api_type.currentIndex()]
            os.environ["OCR_API_TYPE"] = ocr_api_type
            
            # 根据选择的OCR类型保存对应的配置
            if ocr_api_type == "BAIDU":
                if self.baidu_app_id.text():
                    os.environ["BAIDU_APP_ID"] = self.baidu_app_id.text()
                if self.baidu_api_key.text():
                    os.environ["BAIDU_API_KEY"] = self.baidu_api_key.text()
                if self.baidu_secret_key.text():
                    os.environ["BAIDU_SECRET_KEY"] = self.baidu_secret_key.text()
            
            elif ocr_api_type == "TENCENT":
                if self.tencent_secret_id.text():
                    os.environ["TENCENT_SECRET_ID"] = self.tencent_secret_id.text()
                if self.tencent_secret_key.text():
                    os.environ["TENCENT_SECRET_KEY"] = self.tencent_secret_key.text()
                if self.tencent_region.text():
                    os.environ["TENCENT_REGION"] = self.tencent_region.text()
            
            else:  # CUSTOM
                if self.custom_ocr_url.text():
                    os.environ["CUSTOM_OCR_ENDPOINT"] = self.custom_ocr_url.text()
                if self.custom_ocr_key.text():
                    os.environ["CUSTOM_OCR_KEY"] = self.custom_ocr_key.text()
            
            # 保存提示词模板设置
            os.environ["PROMPT_TEMPLATE"] = self.prompt_template_edit.toPlainText()
            
            # 如果有选中的模型，确保其设置已保存并更新环境变量
            selected_index = self.ai_model_combo.currentIndex()
            if selected_index >= 0:
                selected_model_id = self.ai_model_combo.currentData()
                if selected_model_id in self.models_info:
                    model_info = self.models_info[selected_model_id]
                    # 更新环境变量
                    os.environ["CUSTOM_MODEL"] = model_info.get("name", "")
                    os.environ["CUSTOM_BASE_URL"] = model_info.get("base_url", "")
                    os.environ["CUSTOM_API_KEY"] = model_info.get("api_key", "")
                    
                    # 同步更新到UI显示
                    self.status_bar.showMessage(f"当前选中模型: {model_info.get('display_name', '未命名')}", 3000)
            
            # 保存设置到文件
            self._save_settings_to_file()
            
            # 显示成功消息
            QMessageBox.information(self, "保存成功", "所有设置已保存")
            self.status_bar.showMessage("所有设置已保存", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存设置时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_ocr_api_type_changed(self, index):
        """OCR API类型变更时的处理"""
        # 隐藏所有OCR设置组
        self.baidu_group.hide()
        self.tencent_group.hide()
        self.custom_group.hide()
        
        # 清除现有布局中的所有小部件
        if hasattr(self, 'ocr_settings_layout'):
            # 移除之前的所有组件
            while self.ocr_settings_layout.count():
                item = self.ocr_settings_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
        
        # 根据选择的类型显示不同的OCR设置组
        if index == 0:  # 自定义
            # 显示自定义OCR表单
            self.custom_group.show()
            self.ocr_settings_layout.addWidget(self.custom_group)
            self.status_bar.showMessage("已切换到自定义OCR设置", 3000)
        elif index == 1:  # 百度
            # 显示百度OCR表单
            self.baidu_group.show()
            self.ocr_settings_layout.addWidget(self.baidu_group)
            self.status_bar.showMessage("已切换到百度OCR设置", 3000)
        elif index == 2:  # 腾讯
            # 显示腾讯OCR表单
            self.tencent_group.show()
            self.ocr_settings_layout.addWidget(self.tencent_group)
            self.status_bar.showMessage("已切换到腾讯OCR设置", 3000)

    def test_ocr_connection(self):
        """测试OCR连接"""
        try:
            # 获取选择的OCR类型
            ocr_type = self.ocr_api_type.currentText()
            config = {}
            
            # 根据选择的OCR类型准备配置
            if ocr_type == "百度":
                app_id = self.baidu_app_id.text().strip()
                api_key = self.baidu_api_key.text().strip()
                secret_key = self.baidu_secret_key.text().strip()
                
                if not all([app_id, api_key, secret_key]):
                    QMessageBox.warning(self, "输入错误", "请填写所有百度OCR参数")
                    return
                
                config = {
                    "OCR_API_TYPE": "BAIDU",
                    "BAIDU_APP_ID": app_id,
                    "BAIDU_API_KEY": api_key,
                    "BAIDU_SECRET_KEY": secret_key
                }
                
            elif ocr_type == "腾讯":
                secret_id = self.tencent_secret_id.text().strip()
                secret_key = self.tencent_secret_key.text().strip()
                region = self.tencent_region.text().strip()
                
                if not all([secret_id, secret_key]):
                    QMessageBox.warning(self, "输入错误", "请填写腾讯OCR SecretId和SecretKey参数")
                    return
                
                config = {
                    "OCR_API_TYPE": "TENCENT",
                    "TENCENT_SECRET_ID": secret_id,
                    "TENCENT_SECRET_KEY": secret_key,
                    "TENCENT_REGION": region
                }
                
            else:  # 自定义
                api_url = self.custom_ocr_url.text().strip()
                
                if not api_url:
                    QMessageBox.warning(self, "输入错误", "请填写自定义OCR API地址")
                    return
                
                config = {
                    "OCR_API_TYPE": "CUSTOM",
                    "CUSTOM_OCR_ENDPOINT": api_url
                }
                # 如果有API密钥，也添加
                api_key = self.custom_ocr_key.text().strip()
                if api_key:
                    config["CUSTOM_OCR_KEY"] = api_key
            
            # 询问用户是选择测试连接还是测试图片识别
            test_options = QMessageBox()
            test_options.setWindowTitle("测试选项")
            test_options.setText("请选择测试方式:")
            test_options.setIcon(QMessageBox.Question)
            
            connection_button = test_options.addButton("仅测试连接", QMessageBox.ActionRole)
            image_button = test_options.addButton("选择图片进行测试", QMessageBox.ActionRole)
            cancel_button = test_options.addButton("取消", QMessageBox.RejectRole)
            
            test_options.exec()
            
            # 根据用户选择执行不同的测试
            clicked_button = test_options.clickedButton()
            
            if clicked_button == connection_button:
                # 仅测试连接
                self.status_bar.showMessage("正在测试OCR连接...", 0)
                
                from ocr.ocr_processor import OCRProcessor
                processor = OCRProcessor(config)
                
                # 测试连接
                test_result = False
                if ocr_type == "百度":
                    test_result = processor.test_baidu_connection()
                elif ocr_type == "腾讯":
                    test_result = processor.test_tencent_connection()
                else:
                    test_result = processor.test_custom_connection()
                
                if test_result:
                    QMessageBox.information(self, "连接成功", f"{ocr_type}OCR连接测试成功!")
                    self.status_bar.showMessage(f"{ocr_type}OCR连接测试成功", 5000)
                else:
                    QMessageBox.warning(self, "连接失败", f"{ocr_type}OCR连接测试失败，请检查参数")
                    self.status_bar.showMessage(f"{ocr_type}OCR连接测试失败", 5000)
                    
            elif clicked_button == image_button:
                # 选择图片进行测试识别
                file_dialog = QFileDialog()
                image_path, _ = file_dialog.getOpenFileName(
                    self,
                    "选择测试图片",
                    "",
                    "图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;所有文件 (*.*)"
                )
                
                if not image_path:
                    return
                
                # 显示等待提示
                self.status_bar.showMessage(f"正在使用{ocr_type}OCR识别图片...", 0)
                wait_msg = QMessageBox()
                wait_msg.setWindowTitle("处理中")
                wait_msg.setText(f"正在使用{ocr_type}OCR识别图片，请稍候...")
                wait_msg.setStandardButtons(QMessageBox.NoButton)
                wait_msg.show()
                QApplication.processEvents()  # 确保消息框显示
                
                try:
                    # 创建OCR处理器并识别图片
                    from ocr.ocr_processor import OCRProcessor
                    from pathlib import Path
                    
                    processor = OCRProcessor(config)
                    
                    # 根据OCR类型调用不同的图片识别方法
                    result = processor.process_image(Path(image_path))
                    # 关闭等待提示
                    wait_msg.close()
                    
                    if result:
                        # 显示图片预览和识别结果
                        preview_dialog = QDialog(self)
                        preview_dialog.setWindowTitle("OCR识别结果")
                        preview_dialog.setMinimumSize(800, 600)
                        
                        # 创建布局
                        layout = QVBoxLayout(preview_dialog)
                        
                        # 图像和结果的水平布局
                        image_result_layout = QHBoxLayout()
                        
                        # 左侧图像预览区域
                        image_group = QGroupBox("图像预览")
                        image_layout = QVBoxLayout(image_group)
                        
                        # 添加图像标签
                        image_label = QLabel()
                        pixmap = QPixmap(image_path)
                        
                        # 等比缩放图像
                        scaled_pixmap = pixmap.scaled(
                            350, 500, 
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        image_layout.addWidget(image_label)
                        image_result_layout.addWidget(image_group)
                        
                        # 右侧识别结果区域
                        result_group = QGroupBox("识别结果")
                        result_layout = QVBoxLayout(result_group)
                        
                        result_text = QTextEdit()
                        result_text.setReadOnly(True)
                        result_text.setText(result)
                        result_layout.addWidget(result_text)
                        
                        image_result_layout.addWidget(result_group)
                        layout.addLayout(image_result_layout)
                        
                        # 添加关闭按钮
                        close_button = QPushButton("关闭")
                        close_button.clicked.connect(preview_dialog.close)
                        layout.addWidget(close_button)
                        
                        preview_dialog.exec()
                        self.status_bar.showMessage(f"{ocr_type}OCR识别完成", 5000)
                    else:
                        QMessageBox.warning(self, "识别失败", f"{ocr_type}OCR识别失败，未返回结果")
                        self.status_bar.showMessage(f"{ocr_type}OCR识别失败", 5000)
                    
                except Exception as e:
                    wait_msg.close()
                    QMessageBox.critical(self, "识别错误", f"OCR图片识别出错: {str(e)}")
                    self.status_bar.showMessage(f"OCR图片识别出错: {str(e)}", 5000)
                
        except Exception as e:
            QMessageBox.critical(self, "测试失败", f"OCR测试出错: {str(e)}")
            self.status_bar.showMessage(f"OCR测试出错: {str(e)}", 5000)

    def load_settings(self):
        """从环境变量和配置文件加载设置"""
        try:
            # 先从文件加载设置
            self._load_settings_from_file()
            
            # 加载提示词模板设置
            self.prompt_template_edit.setText(os.environ.get("PROMPT_TEMPLATE", "请将以下笔记内容转换为Markdown格式:\n\n"))
            
            # 加载OCR类型设置
            ocr_api_type = os.environ.get("OCR_API_TYPE", "CUSTOM")
            index_map = {"CUSTOM": 0, "BAIDU": 1, "TENCENT": 2}
            self.ocr_api_type.setCurrentIndex(index_map.get(ocr_api_type, 0))
            
            # 加载百度OCR设置
            self.baidu_app_id.setText(os.environ.get("BAIDU_APP_ID", ""))
            self.baidu_api_key.setText(os.environ.get("BAIDU_API_KEY", ""))
            self.baidu_secret_key.setText(os.environ.get("BAIDU_SECRET_KEY", ""))
            
            # 加载腾讯OCR设置
            self.tencent_secret_id.setText(os.environ.get("TENCENT_SECRET_ID", ""))
            self.tencent_secret_key.setText(os.environ.get("TENCENT_SECRET_KEY", ""))
            self.tencent_region.setText(os.environ.get("TENCENT_REGION", "ap-beijing"))
            
            # 加载自定义OCR设置
            self.custom_ocr_url.setText(os.environ.get("CUSTOM_OCR_ENDPOINT", ""))
            self.custom_ocr_key.setText(os.environ.get("CUSTOM_OCR_KEY", ""))
            
            # 更新模型下拉列表
            self.update_models_dropdown()
            
            self.status_bar.showMessage("设置已加载", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"加载设置时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _save_settings_to_file(self):
        """保存设置到文件"""
        try:
            # 获取项目根目录
            project_dir = self._get_project_root()
            settings_file = project_dir / "settings.json"
            
            # 检查原始设置文件是否存在
            original_settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        original_settings = json.load(f)
                except:
                    pass
            
            # 获取当前设置
            settings = {
                # 保留原来的单个模型设置以兼容旧版本
                "CUSTOM_MODEL": os.environ.get("CUSTOM_MODEL", ""),
                "CUSTOM_BASE_URL": os.environ.get("CUSTOM_BASE_URL", ""),
                "CUSTOM_API_KEY": os.environ.get("CUSTOM_API_KEY", ""),
                
                # 模型配置
                "MODELS": self.models_info,
                
                # 提示词模板设置
                "PROMPT_TEMPLATE": self.prompt_template_edit.toPlainText(),
                
                # OCR设置
                "OCR_API_TYPE": ["CUSTOM", "BAIDU", "TENCENT"][self.ocr_api_type.currentIndex()],
                
                # 百度OCR设置
                "BAIDU_APP_ID": self.baidu_app_id.text(),
                "BAIDU_API_KEY": self.baidu_api_key.text(),
                "BAIDU_SECRET_KEY": self.baidu_secret_key.text(),
                
                # 腾讯OCR设置
                "TENCENT_SECRET_ID": self.tencent_secret_id.text(),
                "TENCENT_SECRET_KEY": self.tencent_secret_key.text(),
                "TENCENT_REGION": self.tencent_region.text(),
                
                # 自定义OCR设置
                "CUSTOM_OCR_ENDPOINT": self.custom_ocr_url.text(),
                "CUSTOM_OCR_KEY": self.custom_ocr_key.text()
            }
            
            # 如果有选中的当前模型，将其设为默认模型
            selected_index = self.ai_model_combo.currentIndex()
            if selected_index >= 0:
                selected_model_id = self.ai_model_combo.currentData()
                if selected_model_id in self.models_info:
                    model_info = self.models_info[selected_model_id]
                    # 更新单独的模型字段
                    settings["CUSTOM_MODEL"] = model_info.get("name", "")
                    settings["CUSTOM_BASE_URL"] = model_info.get("base_url", "")
                    settings["CUSTOM_API_KEY"] = model_info.get("api_key", "")
            
            # 保存设置到JSON文件
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            # 打印确认消息
            print(f"设置已保存到: {settings_file}")
            
        except Exception as e:
            raise Exception(f"保存设置到文件时出错: {str(e)}")
    
    def _load_settings_from_file(self):
        """从文件加载设置"""
        try:
            # 获取项目根目录
            project_dir = self._get_project_root()
            settings_file = project_dir / "settings.json"
            
            # 检查文件是否存在
            if not settings_file.exists():
                return
            
            # 读取设置
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 加载多模型设置
            if "MODELS" in settings and isinstance(settings["MODELS"], dict):
                self.models_info = settings["MODELS"]
                
                # 清空模型列表
                self.models_list.clear()
                
                # 重新填充模型列表
                for model_id, model_info in self.models_info.items():
                    item = QListWidgetItem(model_info.get("name", "未命名模型"))
                    item.setData(Qt.UserRole, model_id)
                    self.models_list.addItem(item)
                
                # 设置环境变量用于默认模型
                if self.models_info:
                    # 使用第一个模型作为默认
                    default_model_id = next(iter(self.models_info))
                    default_model = self.models_info[default_model_id]
                    
                    os.environ["CUSTOM_MODEL"] = default_model.get("name", "")
                    os.environ["CUSTOM_BASE_URL"] = default_model.get("base_url", "")
                    os.environ["CUSTOM_API_KEY"] = default_model.get("api_key", "")
            # 向后兼容原来的单模型配置
            elif "CUSTOM_MODEL" in settings or "CUSTOM_BASE_URL" in settings or "CUSTOM_API_KEY" in settings:
                # 创建一个默认模型
                model_id = "default_model"
                model_info = {
                    "id": model_id,
                    "name": settings.get("CUSTOM_MODEL", "默认模型"),
                    "display_name": "默认模型",
                    "base_url": settings.get("CUSTOM_BASE_URL", ""),
                    "api_key": settings.get("CUSTOM_API_KEY", "")
                }
                
                self.models_info[model_id] = model_info
                
                # 添加到列表显示
                item = QListWidgetItem(model_info["name"])
                item.setData(Qt.UserRole, model_id)
                self.models_list.addItem(item)
                
                # 选择新添加的模型
                self.models_list.setCurrentRow(0)
            
            # 加载提示词模板设置
            if "PROMPT_TEMPLATE" in settings:
                os.environ["PROMPT_TEMPLATE"] = settings["PROMPT_TEMPLATE"]
            
            # 加载OCR类型设置
            if "OCR_API_TYPE" in settings:
                os.environ["OCR_API_TYPE"] = settings["OCR_API_TYPE"]
            
            # 加载百度OCR设置
            if "BAIDU_APP_ID" in settings:
                os.environ["BAIDU_APP_ID"] = settings["BAIDU_APP_ID"]
            
            if "BAIDU_API_KEY" in settings:
                os.environ["BAIDU_API_KEY"] = settings["BAIDU_API_KEY"]
            
            if "BAIDU_SECRET_KEY" in settings:
                os.environ["BAIDU_SECRET_KEY"] = settings["BAIDU_SECRET_KEY"]
            
            # 加载腾讯OCR设置
            if "TENCENT_SECRET_ID" in settings:
                os.environ["TENCENT_SECRET_ID"] = settings["TENCENT_SECRET_ID"]
            
            if "TENCENT_SECRET_KEY" in settings:
                os.environ["TENCENT_SECRET_KEY"] = settings["TENCENT_SECRET_KEY"]
            
            if "TENCENT_REGION" in settings:
                os.environ["TENCENT_REGION"] = settings["TENCENT_REGION"]
            
            # 加载自定义OCR设置
            if "CUSTOM_OCR_ENDPOINT" in settings:
                os.environ["CUSTOM_OCR_ENDPOINT"] = settings["CUSTOM_OCR_ENDPOINT"]
            
            if "CUSTOM_OCR_KEY" in settings:
                os.environ["CUSTOM_OCR_KEY"] = settings["CUSTOM_OCR_KEY"]
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"从文件加载设置时出错: {str(e)}")
    
    def _get_project_root(self):
        """获取项目根目录"""
        try:
            # 获取当前文件所在目录
            current_dir = Path(__file__).resolve().parent
            
            # 向上查找，找到项目根目录（有main.py的父目录）
            while current_dir.name != "src" and current_dir.parent != current_dir:
                current_dir = current_dir.parent
            
            # 返回项目根目录
            return current_dir.parent
            
        except Exception as e:
            raise Exception(f"获取项目根目录时出错: {str(e)}")

    def import_note(self):
        """导入笔记"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "导入文件",
            "",
            "文本文件 (*.txt);;Word文档 (*.docx);;PDF文件 (*.pdf);;Markdown (*.md);;图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.gif)"
        )
        
        if file_path:
            try:
                # 显示进度对话框
                progress = QProgressDialog("读取文件中...", "取消", 0, 100, self)
                progress.setWindowTitle("文件读取进度")
                progress.setWindowModality(Qt.WindowModal)
                progress.setValue(0)
                progress.show()
                
                # 更新进度的计时器
                timer = QTimer(self)
                progress_value = 0
                
                def update_progress():
                    nonlocal progress_value
                    if progress_value < 90:
                        progress_value += 10
                        progress.setValue(progress_value)
                
                # 定时更新进度
                timer.timeout.connect(update_progress)
                timer.start(100)  # 每100毫秒更新一次
                
                # 读取文件内容
                content = FileHandler.read_file(file_path)
                
                # 停止计时器，完成进度
                timer.stop()
                progress.setValue(100)
                
                if content:
                    self.input_text.setText(content)
                    self.status_bar.showMessage(f"已导入文件: {os.path.basename(file_path)}", 5000)
                else:
                    QMessageBox.warning(self, "导入错误", "无法读取文件内容")
            except Exception as e:
                QMessageBox.warning(self, "导入错误", f"导入文件时出错: {e}")

    def open_github_page(self):
        """打开GitHub项目页面"""
        try:
            # GitHub项目URL
            github_url = "https://github.com/caizili999/ai_note_to_md"
            QDesktopServices.openUrl(QUrl(github_url))
        except Exception as e:
            QMessageBox.warning(self, "打开GitHub页面失败", f"无法打开GitHub页面: {str(e)}")

    def add_new_model(self):
        """添加新模型"""
        # 创建一个新的模型ID (使用时间戳确保唯一性)
        import time
        model_id = f"model_{int(time.time())}"
        
        # 创建默认模型信息
        model_info = {
            "id": model_id,
            "name": f"自定义模型 {self.models_list.count() + 1}",
            "display_name": f"模型 {self.models_list.count() + 1}",
            "base_url": "",
            "api_key": ""
        }
        
        # 添加到模型字典
        self.models_info[model_id] = model_info
        
        # 添加到列表显示
        self.models_list.addItem(model_info["name"])
        new_item = self.models_list.item(self.models_list.count() - 1)
        new_item.setData(Qt.UserRole, model_id)
        
        # 选择新添加的模型
        self.models_list.setCurrentRow(self.models_list.count() - 1)
        
        # 清空详细设置区域，准备输入新模型信息
        self.custom_model_name.setText(model_info["name"])
        self.custom_model_display_name.setText(model_info["display_name"])
        self.custom_base_url.setText("")
        self.custom_api_key.setText("")
    
    def remove_selected_model(self):
        """删除选中的模型"""
        # 获取当前选中的项
        current_item = self.models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "删除失败", "请先选择要删除的模型")
            return
        
        # 确认是否删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模型 '{current_item.text()}' 吗？", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 获取模型ID
            model_id = current_item.data(Qt.UserRole)
            
            # 从字典中删除
            if model_id in self.models_info:
                del self.models_info[model_id]
            
            # 从列表中删除
            row = self.models_list.row(current_item)
            self.models_list.takeItem(row)
            
            # 清空详细设置区域
            self.custom_model_name.setText("")
            self.custom_model_display_name.setText("")
            self.custom_base_url.setText("")
            self.custom_api_key.setText("")
    
    def on_model_selected(self):
        """当模型选择改变时的处理"""
        # 获取当前选中的项
        current_item = self.models_list.currentItem()
        if not current_item:
            return
        
        # 获取模型ID和信息
        model_id = current_item.data(Qt.UserRole)
        if model_id in self.models_info:
            model_info = self.models_info[model_id]
            
            # 填充详细设置区域
            self.custom_model_name.setText(model_info.get("name", ""))
            self.custom_model_display_name.setText(model_info.get("display_name", ""))
            self.custom_base_url.setText(model_info.get("base_url", ""))
            self.custom_api_key.setText(model_info.get("api_key", ""))
    
    def save_model_details(self):
        """保存当前编辑的模型详细信息"""
        # 获取当前选中的项
        current_item = self.models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "保存失败", "请先选择或添加一个模型")
            return
        
        # 获取模型ID
        model_id = current_item.data(Qt.UserRole)
        
        # 获取编辑的信息
        model_name = self.custom_model_name.text().strip()
        model_display_name = self.custom_model_display_name.text().strip()
        base_url = self.custom_base_url.text().strip()
        api_key = self.custom_api_key.text()
        
        # 验证输入
        if not model_name or not model_display_name:
            QMessageBox.warning(self, "输入错误", "模型名称和显示名称不能为空")
            return
        
        # 更新模型信息
        self.models_info[model_id] = {
            "id": model_id,
            "name": model_name,
            "display_name": model_display_name,
            "base_url": base_url,
            "api_key": api_key
        }
        
        # 更新列表显示
        current_item.setText(model_name)
        
        # 更新模型下拉列表
        self.update_models_dropdown()
        
        # 将其设为当前选择的模型
        model_display_name_to_find = model_display_name
        for i in range(self.ai_model_combo.count()):
            if self.ai_model_combo.itemText(i) == model_display_name_to_find:
                self.ai_model_combo.setCurrentIndex(i)
                break
        
        # 设置为系统环境变量（默认模型）
        os.environ["CUSTOM_MODEL"] = model_name
        os.environ["CUSTOM_BASE_URL"] = base_url
        os.environ["CUSTOM_API_KEY"] = api_key
        
        # 保存设置到文件
        try:
            self._save_settings_to_file()
            QMessageBox.information(self, "保存成功", f"模型 '{model_name}' 的设置已保存")
        except Exception as e:
            QMessageBox.warning(self, "保存警告", f"模型设置已更新，但保存到文件时出错: {str(e)}")
            self.status_bar.showMessage(f"模型设置已更新，但保存到文件时出错", 5000)
    
    def update_models_dropdown(self):
        """更新模型下拉列表"""
        # 清空原有选项
        self.ai_model_combo.clear()
        
        # 添加所有模型
        for model_id, model_info in self.models_info.items():
            display_name = model_info.get("display_name", "未命名模型")
            self.ai_model_combo.addItem(display_name, model_id)

    def delayed_load_settings(self):
        """延迟加载设置，确保UI组件已完全创建"""
        try:
            self.load_settings()
        except Exception as e:
            self.status_bar.showMessage(f"加载设置失败: {str(e)}", 5000)
            import traceback
            traceback.print_exc()
