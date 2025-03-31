#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI处理模块
负责通过自定义模型处理笔记内容，转换为Markdown格式
"""

from abc import ABC, abstractmethod
import os
import openai
import json
from datetime import datetime

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
        self.model_name = os.environ.get("CUSTOM_MODEL_NAME", "gpt-3.5-turbo")
        
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
            
            # 记录测试成功的配置
            self._cache_valid_config()
            
            return answer, f"连接测试成功 | 模型：{self.model_name}"
        except Exception as e:
            return False, f"未处理的异常：{str(e)}"

 
            
    def _verify_model_capability(self, response_text: str) -> bool:
        """验证模型基本能力"""
        return len(response_text) > 5 and any(c.isalpha() for c in response_text)
        
    def _cache_valid_config(self):
        """缓存当前有效配置"""
        config_cache = {
            "base_url": self.base_url,
            "api_key": self.api_key,
            "model": self.model_name,
            "last_success": datetime.now().isoformat()
        }
        with open("ai_config_cache.json", "w") as f:
            json.dump(config_cache, f)
    
    def process_note(self, note_content, format_options=None):
        """使用自定义模型处理笔记"""
        # TODO: 实现实际API调用逻辑
        # 在这里实现使用自定义模型处理笔记的逻辑
        # 返回处理后的Markdown内容
        
        # 举个例子
        prompt = self._build_prompt(note_content, format_options)
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
        
        # return "# 自定义模型处理结果示例\n\n这是通过自定义模型生成的Markdown内容"
    
    def _build_prompt(self, note_content, format_options):
        """构建处理提示"""
        prompt = "请将以下笔记内容转换为Markdown格式:\n\n"
        prompt += note_content + "\n\n"
        
        prompt += "请遵循以下格式要求:\n"
        if 'header_level' in format_options:
            prompt += f"- 标题级别从 {format_options['header_level']} 开始\n"
        if 'list_style' in format_options:
            prompt += f"- 列表样式使用 {format_options['list_style']}\n"
        if 'code_language' in format_options:
            prompt += f"- 代码块使用 {format_options['code_language']} 作为默认语言\n"
        
        return prompt
