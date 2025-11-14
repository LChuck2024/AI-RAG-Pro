"""
通用助手模块
处理不使用RAG的通用问答逻辑
"""
import streamlit as st
import logging
from typing import Tuple, Optional
from src.llm import get_llm_service
from prompt import get_general_assistant_prompt

logger = logging.getLogger(__name__)


def handle_general_assistant(
    prompt: str,
    message_placeholder,
    thinking_placeholder: Optional[st.delta_generator.DeltaGenerator],
    show_thinking: bool = False
) -> Tuple[str, list, str]:
    """
    处理通用助手模式的问答
    
    Args:
        prompt: 用户输入的问题
        message_placeholder: Streamlit占位符，用于显示回答
        thinking_placeholder: Streamlit占位符，用于显示思考过程（可选）
        show_thinking: 是否显示思考过程
    
    Returns:
        Tuple[str, list, str]: (full_response, src_nodes, sources_str)
            - full_response: 完整的回答内容
            - src_nodes: 来源节点列表（通用助手为空列表）
            - sources_str: 来源字符串（通用助手为空字符串）
    """
    llm_service = get_llm_service()
    
    if not llm_service.is_available():
        error_msg = "❌ 未找到可用的 API 密钥。请在 config/config.json 中配置 DEEPSEEK_API_KEY、OPENAI_API_KEY 或 DASHSCOPE_API_KEY。"
        st.error(error_msg)
        full_response = "抱歉，未配置 API 密钥，无法生成回答。请检查 config/config.json 配置文件。"
        message_placeholder.markdown(full_response)
        return full_response, [], ""
    
    # 获取通用助手提示词
    try:
        system_prompt = get_general_assistant_prompt()
        # 将系统提示词添加到用户提示词前
        enhanced_prompt = f"{system_prompt}\n\n用户问题：{prompt}"
    except Exception as e:
        logger.warning(f"获取通用助手提示词失败: {e}，使用原始提示词")
        enhanced_prompt = prompt
    
    # 使用LLM服务进行流式调用
    full_response = ""
    thinking_content_final = ""
    
    try:
        # 流式调用
        stream_success = False
        for chunk in llm_service.stream_chat(enhanced_prompt, show_thinking=show_thinking):
            if chunk["type"] == "error":
                st.error(chunk["content"])
                full_response = "抱歉，生成回答时出现错误。"
                break
            elif chunk["type"] == "thinking":
                # 显示思考过程
                if thinking_placeholder:
                    thinking_placeholder.markdown(f"💭 **思考过程：**\n\n{chunk['content']}▌")
                thinking_content_final = chunk["content"]
            elif chunk["type"] == "content":
                # 显示回答内容
                if chunk.get("thinking"):
                    # 如果有思考过程，分离显示
                    if thinking_placeholder:
                        thinking_placeholder.markdown(f"💭 **思考过程：**\n\n{chunk['thinking']}▌")
                    thinking_content_final = chunk["thinking"]
                message_placeholder.markdown(chunk["content"] + "▌")
                full_response = chunk["content"]
            elif chunk["type"] == "done":
                # 完成，最终处理
                full_response = chunk["content"]
                thinking_content_final = chunk.get("thinking", "")
                
                # 清除流式输出时的thinking_placeholder
                if thinking_placeholder:
                    thinking_placeholder.empty()
                    thinking_placeholder = None
                
                # 显示最终回答
                message_placeholder.markdown(full_response)
                
                # 在回答完成后，使用expander显示思考过程（默认折叠）
                if show_thinking and thinking_content_final:
                    with st.expander("💭 查看思考过程", expanded=False):
                        st.markdown(thinking_content_final)
                stream_success = True
                break
        
        # 如果流式调用失败，尝试非流式作为回退
        if not stream_success and not full_response:
            result = llm_service.chat(enhanced_prompt, show_thinking=show_thinking)
            if result["success"]:
                full_response = result["content"]
                thinking_content_final = result.get("thinking", "")
                
                # 清除流式输出时的thinking_placeholder
                if thinking_placeholder:
                    thinking_placeholder.empty()
                    thinking_placeholder = None
                
                message_placeholder.markdown(full_response)
                
                # 在回答完成后，使用expander显示思考过程（默认折叠）
                if show_thinking and thinking_content_final:
                    with st.expander("💭 查看思考过程", expanded=False):
                        st.markdown(thinking_content_final)
            else:
                st.error(result.get("error", "生成回答时出现错误"))
                full_response = "抱歉，生成回答时出现错误。"
                message_placeholder.markdown(full_response)
    
    except Exception as e:
        logger.error(f"调用LLM服务失败: {e}")
        st.error(f"调用LLM服务失败: {e}")
        full_response = "抱歉，生成回答时出现错误。"
        message_placeholder.markdown(full_response)
    
    return full_response, [], ""

