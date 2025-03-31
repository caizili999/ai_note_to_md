#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI笔记整理工具 - 主程序
将凌乱的笔记转换为结构化的Markdown格式
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """主函数入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("AI笔记整理工具")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 