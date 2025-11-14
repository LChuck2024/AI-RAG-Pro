"""
行业助手模块
处理使用RAG的行业问答逻辑，包括意图空间和知识空间查询
"""
import streamlit as st
import logging
import inspect
from typing import Tuple, Optional, Any
from src.retriever import RAGManager

logger = logging.getLogger(__name__)


def _separate_thinking_and_answer(
    content: str,
    message_placeholder,
    thinking_placeholder: Optional[st.delta_generator.DeltaGenerator],
    show_thinking: bool
) -> Tuple[str, str]:
    """
    分离思考过程和回答内容
    
    Returns:
        Tuple[str, str]: (answer_part, thinking_part)
    """
    if show_thinking and "**回答：**" in content:
        parts = content.split("**回答：**", 1)
        if len(parts) == 2:
            thinking_part = parts[0].replace("**思考过程：**", "").strip()
            answer_part = parts[1].strip()
            return answer_part, thinking_part
    
    return content, ""


def _handle_streaming_response(
    response_stream: Any,
    message_placeholder,
    thinking_placeholder: Optional[st.delta_generator.DeltaGenerator],
    show_thinking: bool
) -> Tuple[str, str]:
    """
    处理流式响应
    
    Returns:
        Tuple[str, str]: (full_response, thinking_content_final)
    """
    full_response = ""
    thinking_content_final = ""
    
    if hasattr(response_stream, 'response_gen'):
        # 流式响应
        for token in response_stream.response_gen:
            full_response += token
            
            # 如果启用了思考过程，在流式输出时分离显示
            if show_thinking and "**思考过程：**" in full_response:
                if "**回答：**" in full_response:
                    # 已经包含回答部分，分离显示
                    answer_part, thinking_part = _separate_thinking_and_answer(
                        full_response, message_placeholder, thinking_placeholder, show_thinking
                    )
                    if thinking_placeholder and thinking_part:
                        thinking_placeholder.markdown(f"💭 **思考过程：**\n\n{thinking_part}▌")
                    message_placeholder.markdown(answer_part + "▌")
                else:
                    # 还在思考阶段
                    thinking_part = full_response.replace("**思考过程：**", "").strip()
                    if thinking_placeholder:
                        thinking_placeholder.markdown(f"💭 **思考过程：**\n\n{thinking_part}▌")
            else:
                # 没有思考过程标记，直接显示
                message_placeholder.markdown(full_response + "▌")
        
        # 最终处理：分离思考过程和回答
        if show_thinking and "**回答：**" in full_response:
            answer_part, thinking_part = _separate_thinking_and_answer(
                full_response, message_placeholder, thinking_placeholder, show_thinking
            )
            message_placeholder.markdown(answer_part)
            full_response = answer_part
            thinking_content_final = thinking_part
        else:
            message_placeholder.markdown(full_response)
        
        # 清除流式输出时的thinking_placeholder，避免与expander重复
        if thinking_placeholder:
            thinking_placeholder.empty()
            thinking_placeholder = None
    else:
        # 非流式响应
        if hasattr(response_stream, "response"):
            full_response = str(response_stream.response)
        elif hasattr(response_stream, "get_response"):
            full_response = str(response_stream.get_response())
        else:
            full_response = str(response_stream)
        
        # 处理思考过程和回答的分离
        if show_thinking and "**回答：**" in full_response:
            answer_part, thinking_part = _separate_thinking_and_answer(
                full_response, message_placeholder, thinking_placeholder, show_thinking
            )
            message_placeholder.markdown(answer_part)
            full_response = answer_part
            thinking_content_final = thinking_part
        else:
            message_placeholder.markdown(full_response)
    
    return full_response, thinking_content_final


def _query_intent_space(
    rag_manager: RAGManager,
    prompt: str,
    k_intent: int,
    intent_threshold: float,
    show_thinking: bool
) -> Tuple[str, float, list]:
    """
    查询意图空间
    
    Returns:
        Tuple[str, float, list]: (intent_text, intent_score, intent_src_nodes)
    """
    intent_text = ""
    intent_score = 0.0
    intent_src_nodes = []
    
    # 检查意图空间索引是否可用
    if rag_manager.intent_index is None:
        logger.warning("意图空间索引不可用，跳过意图空间查询")
        return intent_text, intent_score, intent_src_nodes
    
    try:
        intent_engine = rag_manager.get_intent_query_engine(
            streaming=False, 
            similarity_top_k=k_intent, 
            show_thinking=show_thinking
        )
        intent_response = intent_engine.query(prompt)
        
        # 获取响应文本
        if hasattr(intent_response, "response"):
            intent_text = str(intent_response.response)
        elif hasattr(intent_response, "get_response"):
            intent_text = str(intent_response.get_response())
        else:
            intent_text = str(intent_response)
        
        intent_src_nodes = getattr(intent_response, "source_nodes", [])
        if intent_src_nodes:
            top = intent_src_nodes[0]
            intent_score = getattr(top, "score", 0.0) or 0.0
    except Exception as e:
        logger.warning(f"意图空间查询失败: {e}", exc_info=True)
        intent_text = ""
    
    return intent_text, intent_score, intent_src_nodes


def _query_knowledge_space(
    rag_manager: RAGManager,
    prompt: str,
    k_knowledge: int,
    message_placeholder,
    thinking_placeholder: Optional[st.delta_generator.DeltaGenerator],
    show_thinking: bool
) -> Tuple[str, str, list]:
    """
    查询知识空间
    
    Returns:
        Tuple[str, str, list]: (full_response, thinking_content_final, src_nodes)
    """
    full_response = ""
    thinking_content_final = ""
    src_nodes = []
    
    try:
        # 检查方法是否支持 show_thinking 参数
        sig = inspect.signature(rag_manager.get_knowledge_query_engine)
        if 'show_thinking' in sig.parameters:
            query_engine = rag_manager.get_knowledge_query_engine(
                streaming=True, 
                similarity_top_k=k_knowledge, 
                show_thinking=show_thinking
            )
        else:
            # 旧版本不支持 show_thinking 参数，使用默认调用
            logger.warning("RAGManager 版本较旧，不支持 show_thinking 参数，使用默认调用")
            query_engine = rag_manager.get_knowledge_query_engine(
                streaming=True, 
                similarity_top_k=k_knowledge
            )
            # 清除缓存以重新加载新版本
            st.cache_resource.clear()
        
        response_stream = query_engine.query(prompt)
        full_response, thinking_content_final = _handle_streaming_response(
            response_stream, message_placeholder, thinking_placeholder, show_thinking
        )
        
        # 在回答完成后，使用expander显示思考过程（默认折叠）
        if show_thinking and thinking_content_final:
            with st.expander("💭 查看思考过程", expanded=False):
                st.markdown(thinking_content_final)
        
        src_nodes = getattr(response_stream, "source_nodes", [])
        
    except RuntimeError as e:
        # RAG未启用或嵌入不可用的错误
        error_msg = str(e)
        if "RAG未启用" in error_msg or "嵌入不可用" in error_msg:
            # 提取详细错误信息
            error_detail = error_msg
            if "原因：" in error_msg:
                error_detail = error_msg.split("原因：", 1)[1].strip()
            
            detailed_error = f"""
            **❌ 知识空间查询失败**
            
            **错误原因：** RAG未启用或嵌入模型不可用
            
            **详细错误信息：**
            {error_detail}
            
            **解决步骤：**
            1. 检查 `config/config.json` 中的 DashScope API Key 配置
            2. 确保已安装依赖：`pip install llama-index llama-index-embeddings-dashscope`
            3. 验证 API Key 是否有效（可以在 DashScope 控制台检查）
            4. 确保 `rag_source/knowledge_space` 目录中有文档文件
            5. 重启应用以重新加载配置
            
            **临时方案：** 可以使用"通用助手"模式，该模式不依赖知识库。
            """
            st.error(detailed_error)
            full_response = "⚠️ 知识空间暂时不可用，请检查配置或使用通用助手模式。"
        elif "LLM未初始化" in error_msg or "LLM" in error_msg:
            # LLM 初始化失败的错误
            error_detail = error_msg
            if "LLM未初始化" in error_msg:
                error_detail = error_msg.replace("LLM未初始化。", "").strip()
            
            detailed_error = f"""
            **❌ 知识空间查询失败**
            
            **错误原因：** LLM（大语言模型）未初始化
            
            **详细错误信息：**
            {error_detail}
            
            **解决步骤：**
            1. **如果使用 DeepSeek 或其他非 OpenAI API：**
               - 运行：`pip install 'numpy<2'` 解决 NumPy 版本冲突
               - 重启应用
            
            2. **如果使用 OpenAI API：**
               - 检查 `config/config.json` 中的 `OPENAI_API_KEY` 配置
               - 确保 API Key 有效
            
            3. **通用解决方案：**
               - 检查配置文件中的 LLM 配置
               - 确保 API Key 已正确配置
               - 重启应用以重新加载配置
            
            **临时方案：** 可以使用"通用助手"模式，该模式不依赖知识库。
            """
            st.error(detailed_error)
            full_response = "⚠️ 知识空间暂时不可用，请检查配置或使用通用助手模式。"
        else:
            st.error(f"知识空间查询失败: {error_msg}")
            full_response = "抱歉，查询知识空间时出现错误，请稍后重试。"
        message_placeholder.markdown(full_response)
        logger.error(f"知识空间查询RuntimeError: {error_msg}", exc_info=True)
    except Exception as e:
        error_msg = f"知识空间查询失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        full_response = "抱歉，查询知识空间时出现错误，请稍后重试。"
        message_placeholder.markdown(full_response)
    
    return full_response, thinking_content_final, src_nodes


def handle_industry_assistant(
    rag_manager: RAGManager,
    prompt: str,
    message_placeholder,
    thinking_placeholder: Optional[st.delta_generator.DeltaGenerator],
    k_intent: int = 1,
    k_knowledge: int = 3,
    intent_threshold: float = 0.85,
    show_thinking: bool = False
) -> Tuple[str, list, str, bool, float]:
    """
    处理行业助手模式的问答
    
    Args:
        rag_manager: RAG管理器实例
        prompt: 用户输入的问题
        message_placeholder: Streamlit占位符，用于显示回答
        thinking_placeholder: Streamlit占位符，用于显示思考过程（可选）
        k_intent: 意图空间检索数量
        k_knowledge: 知识空间检索数量
        intent_threshold: 意图空间相似度阈值
        show_thinking: 是否显示思考过程
    
    Returns:
        Tuple[str, list, str, bool, float]: (full_response, src_nodes, sources_str, used_intent_space, intent_score)
            - full_response: 完整回答
            - src_nodes: 源节点列表
            - sources_str: 来源字符串
            - used_intent_space: 是否使用了意图空间快速匹配
            - intent_score: 意图空间相似度分数
    """
    # 检查知识空间是否可用
    if rag_manager.knowledge_index is None:
        # 获取详细的错误信息
        error_detail = ""
        if hasattr(rag_manager, 'embed_error_msg') and rag_manager.embed_error_msg:
            error_detail = f"\n\n**详细错误信息：**\n{rag_manager.embed_error_msg}"
        
        error_msg = f"""
        **❌ 知识空间不可用**
        
        **可能的原因：**
        1. **嵌入模型未配置**：请检查 `config/config.json` 中的 DashScope API Key 配置
        2. **依赖包未安装**：请运行 `pip install llama-index-embeddings-dashscope`
        3. **API密钥无效**：请确认 DashScope API Key 是否正确
        4. **索引加载失败**：请检查知识空间目录是否存在文档
        {error_detail}
        
        **解决方案：**
        - 检查配置文件中的 `embedding.api_key_env` 设置
        - 确保环境变量或配置文件中有有效的 `DASHSCOPE_API_KEY`
        - 安装必要的依赖包：`pip install llama-index llama-index-embeddings-dashscope`
        - 确保 `rag_source/knowledge_space` 目录中有文档文件
        - 重启应用以重新加载配置
        
        **当前可以使用"通用助手"模式**，该模式不依赖知识库。
        """
        st.error(error_msg)
        full_response = "⚠️ 知识空间暂时不可用，请检查配置或使用通用助手模式。"
        message_placeholder.markdown(full_response)
        logger.error(f"知识空间索引为 None，无法使用行业助手。错误详情：{error_detail}")
        return full_response, [], "", False, 0.0
    
    logger.info(f"开始处理行业助手查询: prompt={prompt[:50]}...")
    
    # 第一步：查询意图空间
    try:
        intent_text, intent_score, intent_src_nodes = _query_intent_space(
            rag_manager, prompt, k_intent, intent_threshold, show_thinking
        )
        logger.info(f"意图空间查询完成: score={intent_score}, has_text={len(intent_text) > 0}")
    except Exception as e:
        logger.error(f"意图空间查询异常: {e}", exc_info=True)
        intent_text = ""
        intent_score = 0.0
        intent_src_nodes = []
    
    # 如果意图空间相似度足够高，直接返回意图空间的答案
    use_intent = (intent_score >= intent_threshold) and (len(intent_text.strip()) > 0)
    
    if use_intent:
        # 使用意图空间的答案（快速响应）
        full_response = intent_text
        thinking_content_final = ""
        
        # 如果启用了思考过程，分离思考过程和回答
        if show_thinking and "**回答：**" in full_response:
            answer_part, thinking_part = _separate_thinking_and_answer(
                full_response, message_placeholder, thinking_placeholder, show_thinking
            )
            message_placeholder.markdown(answer_part)
            full_response = answer_part
            thinking_content_final = thinking_part
        else:
            message_placeholder.markdown(full_response)
        
        # 清除流式输出时的thinking_placeholder，避免与expander重复
        if thinking_placeholder:
            thinking_placeholder.empty()
            thinking_placeholder = None
        
        # 在回答完成后，使用expander显示思考过程（默认折叠）
        if show_thinking and thinking_content_final:
            with st.expander("💭 查看思考过程", expanded=False):
                st.markdown(thinking_content_final)
        
        src_nodes = intent_src_nodes
    else:
        # 第二步：查询知识空间，获取更详细的文档信息
        logger.info(f"意图空间不满足条件，查询知识空间: score={intent_score} < threshold={intent_threshold}")
        try:
            full_response, thinking_content_final, src_nodes = _query_knowledge_space(
                rag_manager, prompt, k_knowledge, message_placeholder, 
                thinking_placeholder, show_thinking
            )
            logger.info(f"知识空间查询完成: response_length={len(full_response)}, src_nodes_count={len(src_nodes)}")
        except Exception as e:
            logger.error(f"知识空间查询异常: {e}", exc_info=True)
            full_response = f"抱歉，查询知识空间时出现错误: {str(e)}"
            message_placeholder.markdown(full_response)
            src_nodes = []
    
    # 构建来源字符串
    sources_str = ",".join([str(getattr(n.node, "metadata", {})) for n in src_nodes])
    
    logger.info(f"行业助手查询完成: response_length={len(full_response)}, used_intent={use_intent}, intent_score={intent_score}")
    return full_response, src_nodes, sources_str, use_intent, intent_score

