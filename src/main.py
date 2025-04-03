#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
AI笔记整理工具 - 主程序
将凌乱的笔记转换为结构化的Markdown格式
"""

import sys
import os
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_config():
    """加载配置文件"""
    try:
        # 获取项目根目录
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        
        # 设置文件路径
        config_file = project_root / "settings.json"
        
        # 检查文件是否存在
        if not config_file.exists():
            return
        
        # 读取设置
        with open(config_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # 设置环境变量
        for key, value in settings.items():
            if value:  # 只设置非空值
                os.environ[key] = value
                
    except Exception as e:
        print(f"加载配置文件时出错: {e}")


def main():
    """主函数入口"""
    # 加载配置
    load_config()
    
    app = QApplication(sys.argv)
    app.setApplicationName("AI笔记整理工具")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 