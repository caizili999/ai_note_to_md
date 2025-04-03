#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   ai_processor.py
@Time    :   2025/04/03
@Author  :   Maker 
@Version :   1.0
'''

"""
AI处理模块
负责通过自定义模型处理笔记内容，转换为Markdown格式
"""

from abc import ABC, abstractmethod
import os
import openai
import json
from datetime import datetime
from pathlib import Path

class AIProcessor(ABC):
    """AI处理器抽象基类"""
    
    @abstractmethod
    def process_note(self, note_content, format_options=None):
        """处理笔记内容"""
        pass

def get_processor(api_key=None, base_url=None):
    """获取自定义处理器实例"""
    return CustomProcessor(api_key=api_key, base_url=base_url)

class CustomProcessor(AIProcessor):
    """自定义模型处理器"""
    
    def __init__(self, api_key=None, base_url=None):
        """初始化自定义处理器
        Args:
            api_key: 模型API密钥
            base_url: 模型API基础地址
        """
        self.base_url = base_url or os.environ.get("CUSTOM_BASE_URL")
        self.api_key = api_key or os.environ.get("CUSTOM_API_KEY")
        self.model_name = os.environ.get("CUSTOM_MODEL", "gpt-3.5-turbo")
        
    def test_connection(self, prompt: str = "你好，你是谁") -> tuple:
        """测试自定义模型连接并进行完整功能验证
        Args:
            prompt: 测试用的提示词，默认使用基础测试提示
            
        Returns:
            tuple: (测试结果, 状态信息)
                   - 成功时返回 (response_text, success_message)
                   - 失败时返回 (False, error_message)
        """
        openai.api_key = self.api_key
        openai.base_url= self.base_url
        try:
            # 执行测试请求
            completion =openai.chat.completions.create(
                model= str(self.model_name),
                messages= [
                {
                    "role":"user",
                    "content": str(prompt)
                }
                ],
                stream=False  # 添加此行以确保不使用流式传输
            )
            
            # 验证响应结构
            answer = completion.choices[0].message.content
            
            # 验证模型可用性
            if not self._verify_model_capability(answer):
                return False, "模型响应不符合预期能力"
            
            # # 记录测试成功的配置-不需要先注释
            # self._cache_valid_config()
            
            return answer, f"连接测试成功 | 模型：{self.model_name}"
        except Exception as e:
            return False, f"未处理的异常：{str(e)}"

 
            
    def _verify_model_capability(self, response_text: str) -> bool:
        """验证模型基本能力"""
        return len(response_text) > 5 and any(c.isalpha() for c in response_text)
        
    # 缓存有效配置-不需要上面已注释
    def _cache_valid_config(self):
        """缓存当前有效配置"""
        try:
            # 获取项目根目录路径
            current_dir = Path(__file__).resolve().parent  # models目录
            project_root = current_dir.parent.parent  # ai_note_to_md目录
            
            # 创建配置
            config_cache = {
                "base_url": self.base_url,
                "api_key": self.api_key,
                "model": self.model_name,
                "last_success": datetime.now().isoformat()
            }
            
            # 缓存文件路径
            cache_file = project_root / "ai_config_cache.json"
            
            # 写入缓存文件
            with open(cache_file, "w") as f:
                json.dump(config_cache, f)
                
            print(f"AI配置缓存已保存到: {cache_file}")
        except Exception as e:
            print(f"缓存配置时出错: {e}")
    
    def process_note(self, note_content, format_options=None):
        """使用自定义模型处理笔记"""
        # 举个例子
        prompt_template = format_options.pop('prompt_template', "请将以下笔记内容转换为Markdown格式:\n\n") if format_options else "请将以下笔记内容转换为Markdown格式:\n\n"
        prompt = self._build_prompt(note_content, format_options, prompt_template)
        # 利用自定义api调用
        openai.api_key = self.api_key
        openai.base_url= self.base_url
        completion =openai.chat.completions.create(
            model= str(self.model_name),
            messages= [
            {
                "role":"user",
                "content": str(prompt)
            }
            ],
            stream=False  # 添加此行以确保不使用流式传输
        )
        
        # 验证响应结构
        answer = completion.choices[0].message.content
        return answer
    
    def _build_prompt(self, note_content, format_options, prompt_template="请将以下笔记内容转换为Markdown格式:\n\n"):
        """构建处理提示"""
        prompt = prompt_template
        prompt += note_content + "\n\n"
        
        if format_options:
            prompt += "请遵循以下格式要求:\n"
            for key, value in format_options.items():
                prompt += f"- {key}: {value}\n"
        
        return prompt
