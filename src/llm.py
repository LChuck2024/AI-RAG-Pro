"""
LLM服务模块
负责大模型的调用和管理，实现前后端分离
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Generator, Tuple, Dict, Any
from openai import OpenAI

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.load_key import get_api_key, get_model_config, get_available_llm
try:
    from prompt import get_general_assistant_prompt
except ImportError:
    get_general_assistant_prompt = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LLMService:
    """LLM服务类，负责大模型的调用"""
    
    def __init__(self):
        """初始化LLM客户端"""
        self.client = None
        self.model_name = None
        self._init_client()
    
    def _init_client(self) -> None:
        """初始化LLM客户端，按优先级选择可用的API"""
        # 按优先级获取API密钥
        deepseek_api_key = get_api_key("DEEPSEEK_API_KEY")
        openai_api_key = get_api_key("OPENAI_API_KEY")
        dashscope_api_key = get_api_key("DASHSCOPE_API_KEY")
        
        if deepseek_api_key:
            # 使用 DeepSeek API
            self.client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            self.model_name = "deepseek-chat"
            logging.info("使用 DeepSeek API")
        elif openai_api_key:
            # 使用 OpenAI API
            self.client = OpenAI(api_key=openai_api_key)
            self.model_name = "gpt-3.5-turbo"
            logging.info("使用 OpenAI API")
        elif dashscope_api_key:
            # 使用 DashScope (Qwen) API
            self.client = OpenAI(
                api_key=dashscope_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            self.model_name = "qwen-plus"
            logging.info("使用 DashScope (Qwen) API")
        else:
            logging.warning("未找到可用的 API 密钥")
            self.client = None
            self.model_name = None
    
    def is_available(self) -> bool:
        """检查LLM服务是否可用"""
        return self.client is not None and self.model_name is not None
    
    def _prepare_prompt(self, user_prompt: str, show_thinking: bool = False) -> Tuple[str, str]:
        """
        准备提示词
        
        Args:
            user_prompt: 用户输入的问题
            show_thinking: 是否显示思考过程
        
        Returns:
            Tuple[str, str]: (system_prompt, user_prompt)
        """
        # 加载通用助手提示词作为系统消息
        if get_general_assistant_prompt is not None:
            try:
                system_prompt = get_general_assistant_prompt()
            except Exception as e:
                logging.warning(f"加载通用助手提示词失败: {e}")
                system_prompt = "你是小艾，由凡梦文化创建的智能助手。"
        else:
            system_prompt = "你是小艾，由凡梦文化创建的智能助手。"
        
        # 如果启用思考过程，在提示词中添加要求
        if show_thinking:
            thinking_instruction = "\n\n## 回答要求\n在回答之前，请先展示你的思考过程，包括：\n1. 理解问题的关键点\n2. 分析问题的思路\n3. 组织答案的逻辑\n\n请按以下格式输出：\n\n**思考过程：**\n[你的思考过程]\n\n**回答：**\n[你的最终回答]"
            user_prompt_with_thinking = user_prompt + thinking_instruction
        else:
            user_prompt_with_thinking = user_prompt
        
        return system_prompt, user_prompt_with_thinking
    
    def _separate_thinking_and_answer(self, full_response: str) -> Tuple[str, str]:
        """
        分离思考过程和回答
        
        Args:
            full_response: 完整的响应内容
        
        Returns:
            Tuple[str, str]: (thinking_part, answer_part)
        """
        if "**回答：**" in full_response:
            parts = full_response.split("**回答：**", 1)
            if len(parts) == 2:
                thinking_part = parts[0].replace("**思考过程：**", "").strip()
                answer_part = parts[1].strip()
                return thinking_part, answer_part
        
        return "", full_response
    
    def stream_chat(
        self, 
        user_prompt: str, 
        show_thinking: bool = False
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式调用LLM生成回答
        
        Args:
            user_prompt: 用户输入的问题
            show_thinking: 是否显示思考过程
        
        Yields:
            Dict[str, Any]: 包含以下键的字典
                - "type": "thinking" 或 "content" 或 "done"
                - "content": 内容（token或完整内容）
                - "thinking": 思考过程（如果有）
                - "answer": 最终回答（done时）
        """
        if not self.is_available():
            yield {
                "type": "error",
                "content": "未找到可用的 API 密钥。请在 config/config.json 中配置 DEEPSEEK_API_KEY、OPENAI_API_KEY 或 DASHSCOPE_API_KEY。"
            }
            return
        
        system_prompt, user_prompt_final = self._prepare_prompt(user_prompt, show_thinking)
        
        full_response = ""
        thinking_content = ""
        is_thinking_phase = True
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_final}
                ],
                stream=True
            )
            
            for chunk in stream:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta is None:
                    continue
                
                # 检查是否有思考内容（支持思考模型的reasoning_content）
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    thinking_content += delta.reasoning_content
                    yield {
                        "type": "thinking",
                        "content": thinking_content,
                        "is_streaming": True
                    }
                    is_thinking_phase = True
                
                # 处理正常内容
                token = getattr(delta, "content", None) or ""
                if token:
                    full_response += token
                    
                    # 如果启用了思考过程，检查是否包含思考标记
                    if show_thinking and "**思考过程：**" in full_response:
                        if "**回答：**" in full_response:
                            # 已经包含回答部分，分离显示
                            thinking_part, answer_part = self._separate_thinking_and_answer(full_response)
                            yield {
                                "type": "content",
                                "content": answer_part,
                                "thinking": thinking_part,
                                "is_streaming": True
                            }
                        else:
                            # 还在思考阶段
                            thinking_part = full_response.replace("**思考过程：**", "").strip()
                            yield {
                                "type": "thinking",
                                "content": thinking_part,
                                "is_streaming": True
                            }
                    else:
                        # 没有思考过程标记，直接显示
                        yield {
                            "type": "content",
                            "content": full_response,
                            "is_streaming": True
                        }
            
            # 最终处理：分离思考过程和回答
            thinking_part_final = ""
            answer_part_final = ""
            
            if show_thinking and "**回答：**" in full_response:
                thinking_part_final, answer_part_final = self._separate_thinking_and_answer(full_response)
            elif thinking_content:
                # 如果有来自reasoning_content的思考内容
                thinking_part_final = thinking_content
                answer_part_final = full_response
            else:
                answer_part_final = full_response
            
            yield {
                "type": "done",
                "content": answer_part_final,
                "thinking": thinking_part_final,
                "is_streaming": False
            }
            
        except Exception as e:
            logging.error(f"流式调用LLM失败: {e}")
            yield {
                "type": "error",
                "content": f"流式输出错误: {e}"
            }
    
    def chat(
        self, 
        user_prompt: str, 
        show_thinking: bool = False
    ) -> Dict[str, Any]:
        """
        非流式调用LLM生成回答
        
        Args:
            user_prompt: 用户输入的问题
            show_thinking: 是否显示思考过程
        
        Returns:
            Dict[str, Any]: 包含以下键的字典
                - "success": bool, 是否成功
                - "content": str, 回答内容
                - "thinking": str, 思考过程（如果有）
                - "error": str, 错误信息（如果失败）
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "未找到可用的 API 密钥。请在 config/config.json 中配置 DEEPSEEK_API_KEY、OPENAI_API_KEY 或 DASHSCOPE_API_KEY。"
            }
        
        system_prompt, user_prompt_final = self._prepare_prompt(user_prompt, show_thinking)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_final}
                ]
            )
            full_response = resp.choices[0].message.content
            
            # 处理思考过程和回答的分离
            thinking_part = ""
            answer_part = ""
            
            if show_thinking and "**回答：**" in full_response:
                thinking_part, answer_part = self._separate_thinking_and_answer(full_response)
            else:
                answer_part = full_response
            
            return {
                "success": True,
                "content": answer_part,
                "thinking": thinking_part
            }
            
        except Exception as e:
            logging.error(f"调用LLM失败: {e}")
            return {
                "success": False,
                "error": f"生成回答错误: {e}"
            }


# 全局LLM服务实例
_llm_service = None

def get_llm_service() -> LLMService:
    """获取LLM服务实例（单例模式）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

