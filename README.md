# AI 笔记整理工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

智能笔记转换工具，支持多格式文档解析与AI增强的Markdown结构化处理。

## 🌟 核心功能

### 多格式解析引擎
- **文档解析**：支持多种格式，包括TXT、DOCX、PDF、Markdown
- **图像OCR**：支持PNG、JPG、JPEG、BMP、TIFF、GIF等图像格式的文本识别
- **灵活的OCR选项**：支持百度OCR、腾讯云OCR和自定义OCR服务

### AI增强处理
- **多模型支持**：可同时配置多个AI模型，灵活切换
- **自定义提示词**：支持自定义提示词模板，优化AI处理效果
- **格式控制**：支持设置标题级别、列表样式和代码语言
- **连接测试**：内置模型连接测试功能，确保配置正确

### 便捷的用户体验
- **批量处理**：一次性处理整个文件夹内的笔记和图像
- **实时预览**：图像文件自动预览，OCR结果即时显示
- **进度显示**：文件处理过程中显示进度，提升用户体验
- **配置保存**：自动保存用户设置，下次启动自动加载

## 🛠️ 安装指南

### 前置要求
- Python 3.8+
- 如需使用OCR功能，需配置相应的OCR服务:
  - 百度OCR: 需创建百度智能云账号并获取相关API参数
  - 腾讯云OCR: 需创建腾讯云账号并获取相关API参数
  - 自定义OCR: 需提供支持OCR的API端点

### 安装步骤
```bash
# 克隆代码库
git clone https://github.com/caizili999/ai_note_to_md.git
cd ai_note_to_md

# 安装依赖
pip install -r requirements.txt
```

## 💡 使用说明

### 启动程序
```bash
# Windows
python src/main.py

# Linux/Mac
python3 src/main.py
```

或直接从releases下载zip版本的解压点击运行，Windows推荐使用这个无需安装环境:
- Windows: 双击`点击运行.bat`

### 基础使用流程
1. 在"设置"标签页配置AI模型和OCR服务
2. 在"单文件处理"标签页上传或粘贴笔记内容
3. 点击"整理笔记"按钮处理内容
4. 查看生成的Markdown结果并导出

### 批量处理
1. 在"批量处理"标签页选择包含笔记文件的文件夹
2. 点击"批量处理"按钮
3. 处理完成后，结果将保存在所选文件夹内的"markdown_output"子文件夹中

## ⚙️ 配置说明

### AI模型配置
- 支持添加多个自定义模型
- 每个模型需配置名称、显示名称、API地址和API密钥
- 可随时在处理文件时切换所用模型

### OCR配置
- 百度OCR: 需配置APP_ID、API_KEY和SECRET_KEY
- 腾讯OCR: 需配置SecretId、SecretKey和Region(默认ap-beijing)
- 自定义OCR: 需配置API地址和可选的API密钥

## 🧑‍💻 高级功能

### 自定义提示词
可在单文件处理界面调整AI处理的提示词模板，优化生成效果。

### OCR设置测试
在设置界面可测试OCR连接或直接上传图片进行OCR测试，快速验证配置是否正确。

### 环境变量和配置文件
所有设置会自动保存到项目目录下的`settings.json`文件，程序启动时自动加载。

## 📝 贡献指南
1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可协议
本项目采用 MIT License，详情请查看 [LICENSE](LICENSE) 文件。

## 📬 联系方式
- GitHub: [caizili999](https://github.com/caizili999)
- 项目地址: [https://github.com/caizili999/ai_note_to_md](https://github.com/caizili999/ai_note_to_md)
