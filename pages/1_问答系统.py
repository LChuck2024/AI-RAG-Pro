import streamlit as st
import sys
import os
import logging
from pathlib import Path

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path
setup_project_path()

from src.retriever import RAGManager
from src.feedback import FeedbackStore
from src.general_assistant import handle_general_assistant
from src.industry_assistant import handle_industry_assistant
from src.evaluation import calculate_metrics, format_metrics_display
from config.load_key import load_key
from src.llm import get_llm_service
from 首页 import load_rag_manager, get_rag_manager_cache_key

# 加载配置文件中的API密钥到环境变量
from config.load_key import load_key
load_key()

# 自定义CSS，美化界面
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 聊天容器样式 */
    .stChatInputContainer {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e1e8ed;
    }
    
    .stChatInputContainer > div {
        background: white;
        border-radius: 15px;
    }
    
    /* 用户消息样式 */
    [data-testid="stChatMessageContent"][data-testid*="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px 18px 5px 18px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        border: none;
    }
    
    /* AI助手消息样式 */
    [data-testid="stChatMessageContent"]:not([data-testid*="user"]) {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e1e8ed;
        border-radius: 18px 18px 18px 5px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* 加载动画 */
    .stSpinner {
        text-align: center;
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* 聊天区域容器 */
    .chat-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .chat-container:hover {
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: #e8f5e8;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #2e7d32;
        margin-bottom: 1rem;
    }
    
    /* 思考内容样式 */
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        margin-top: 0.5rem;
    }
    
    /* 侧边栏标题样式 */
    .sidebar-title {
        text-align: center;
        padding: 1.25rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .sidebar-title h2 {
        margin: 0;
        font-size: 1.5rem;
        color: white;
    }
    
    /* 表单元素样式 */
    .stRadio > div {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e1e8ed;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSlider > div > div {
        border-radius: 12px;
    }
    
    .stCheckbox > label {
        font-weight: 500;
    }
    
    /* 状态指示器优化 */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 12px;
        font-size: 0.85rem;
        color: #10b981;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
    }
    
    /* 信息框样式 */
    .stInfo {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
    }
    
    /* 成功消息样式 */
    .stSuccess {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
    }
    
    /* 错误消息样式 */
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
    }
    
    /* 警告消息样式 */
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化反馈存储实例
feedback_store = FeedbackStore()

# 侧边栏配置
with st.sidebar:
    st.markdown("""
    <div class='sidebar-title'>
        <h2>🤖 AI RAG Pro</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>智能问答系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ 系统配置")
    
    # 检查 RAG 依赖是否可用
    rag_available = False
    rag_error_msg = ""
    try:
        import llama_index
        from llama_index.embeddings.dashscope import DashScopeEmbedding
        from config.load_key import get_api_key
        if get_api_key("DASHSCOPE_API_KEY"):
            rag_available = True
        else:
            rag_error_msg = "未配置 DashScope API Key"
    except ImportError as e:
        rag_error_msg = f"缺少依赖: {str(e)}"
    except Exception as e:
        rag_error_msg = f"检查失败: {str(e)}"
    
    qa_mode = st.radio(
        "助手模式", 
        ["通用助手", "行业助手"], 
        index=0,
        help="通用助手：直接使用大模型回答；行业助手：从知识空间、意图空间和反馈空间中检索相关信息后回答",
        horizontal=True
    )
    rag_enabled = (qa_mode == "行业助手")
    
    # 如果选择了行业助手但依赖不可用，显示警告
    if rag_enabled and not rag_available:
        st.warning(f"⚠️ 行业助手当前不可用: {rag_error_msg}")
        st.info("""
        **解决方案：**
        1. 确保已激活正确的 conda 环境（如 `llamaindex_310`）
        2. 安装依赖：`pip install llama-index llama-index-embeddings-dashscope`
        3. 检查 `config/config.json` 中的 DashScope API Key 配置
        4. 重启 Streamlit 应用
        """)
    
    # 显示思考过程选项
    show_thinking = st.checkbox("💭 显示思考过程", value=False, help="开启后，模型会展示其思考推理过程")
    
    # RAG检索参数（仅在RAG模式下显示）
    if rag_enabled:
        st.markdown("---")
        st.markdown("### 📊 RAG检索参数")
        k_knowledge = st.slider("知识空间TopK", min_value=1, max_value=10, value=3, help="从知识空间检索的文档数量")
        k_intent = st.slider("意图空间TopK", min_value=1, max_value=5, value=1, help="从意图空间检索的问答对数量")
        intent_threshold = st.slider("意图直返阈值", min_value=0.5, max_value=0.99, value=0.85, step=0.01, 
                                     help="意图空间相似度超过此值时直接返回答案，否则继续查询知识空间")
    else:
        # 通用问答模式下设置默认值（虽然不会使用）
        k_knowledge = 3
        k_intent = 1
        intent_threshold = 0.85
    
    st.markdown("---")
    st.markdown("### 🛠️ 管理功能")
    col1, col2, col3 = st.columns(3)
    with col1:
        clear_chat = st.button("🗑️ 清空会话", use_container_width=True)
    with col2:
        export_chat = st.button("📥 导出对话", use_container_width=True)
    with col3:
        clear_cache = st.button("🔄 清除缓存", use_container_width=True, help="清除 RAG 管理器缓存，强制重新加载配置")
    
    st.markdown("---")
    
    # 使用提示
    st.markdown("""
    <div style='background: #e8f4fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196F3;'>
        <h4 style='margin: 0 0 0.5rem 0; color: #1976D2;'>💡 使用提示</h4>
        <ul style='margin: 0; padding-left: 1rem; font-size: 0.85rem; color: #424242;'>
            <li>选择适合的助手模式（通用助手或行业助手）</li>
            <li>详细描述您的问题</li>
            <li>行业助手会从知识空间、意图空间检索信息</li>
            <li>可以调整检索参数优化回答质量</li>
            <li>反馈有助于系统改进</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 处理侧边栏操作
if clear_chat:
    st.session_state.messages = []
    st.rerun()

if clear_cache:
    load_rag_manager.clear()
    st.success("✅ 缓存已清除，RAG 管理器将重新加载")
    st.rerun()

if export_chat:
    import json
    chat_data = json.dumps(st.session_state.get("messages", []), ensure_ascii=False, indent=2)
    st.sidebar.download_button(
        "📥 下载JSON", 
        data=chat_data, 
        file_name=f"chat_{st.session_state.get('session_id', 'export')}.json",
        mime="application/json"
    )


# --- 获取当前使用的LLM提供商 ---
llm_provider_name = ""
try:
    if rag_enabled:
        # 行业助手模式
        cache_key = get_rag_manager_cache_key()
        rag_manager = load_rag_manager(_cache_key=cache_key)
        if rag_manager and hasattr(rag_manager, 'llm_provider') and rag_manager.llm_provider:
            llm_provider_name = rag_manager.llm_provider
    else:
        # 通用助手模式
        llm_service = get_llm_service()
        if llm_service and hasattr(llm_service, 'provider') and llm_service.provider:
            llm_provider_name = llm_service.provider
except Exception as e:
    logging.warning(f"无法获取LLM提供商名称: {e}")

# 主要内容区域
# 根据助手模式动态显示描述
subtitle_base = "基于知识库的智能问答助手" if rag_enabled else "通用智能问答助手"
subtitle_text = f"{subtitle_base} (模型: {llm_provider_name})" if llm_provider_name else subtitle_base

st.markdown(f"""
<div class='chat-container'>
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <h1 style='margin: 0; color: #2c3e50; font-size: 2.2rem;'>🤖 AI RAG Pro 问答系统</h1>
        <p style='margin: 0.5rem 0 0 0; color: #5a6c7d; font-size: 1rem;'>{subtitle_text}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 状态指示器
status_color = "#e8f5e8" if rag_enabled else "#fff3cd"
status_text_color = "#2e7d32" if rag_enabled else "#856404"
mode_display = "🔍 行业助手" if rag_enabled else "🤖 通用助手"

st.markdown(f"""
<div style='display: flex; justify-content: center; margin-bottom: 1rem;'>
    <div style='display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; 
                background: {status_color}; border-radius: 20px; font-size: 0.85rem; color: {status_text_color};'>
        <span>{mode_display}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 初始化聊天会话 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "您好！我是 AI RAG Pro 智能问答助手 🤖\n\n我可以为您提供两种助手模式：\n\n1. **通用助手**：直接使用大模型进行回答，适合一般性问题\n2. **行业助手**：从知识空间、意图空间和反馈空间中检索相关信息后回答，适合需要专业知识的问题\n\n💡 提示：您可以在侧边栏选择助手模式，调整检索参数来优化回答质量，也可以对回答进行反馈以帮助系统改进。"
        }
    ]

# --- 显示历史消息 ---
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 为助手消息显示反馈功能
        if message["role"] == "assistant" and idx > 0:  # 跳过欢迎消息
            # 初始化该消息的反馈状态
            feedback_key = f"feedback_{idx}"
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = {
                    "fb_choice": "👍 有帮助",
                    "stars": 4,
                    "tags": [],
                    "correction": "",
                    "submitted": False
                }
            
            # 如果已经提交过，显示已提交状态
            if st.session_state[feedback_key]["submitted"]:
                st.info("✅ 反馈已提交，感谢您的反馈！")
            else:
                # 显示反馈功能
                with st.expander("💬 反馈", expanded=False):
                    fb_choice = st.radio(
                        "是否有帮助", 
                        ["👍 有帮助", "👎 无帮助"], 
                        horizontal=True,
                        key=f"fb_choice_{idx}",
                        index=0 if st.session_state[feedback_key]["fb_choice"] == "👍 有帮助" else 1
                    )
                    # 检查选择是否改变，如果改变则自动调整评分
                    old_choice = st.session_state[feedback_key]["fb_choice"]
                    st.session_state[feedback_key]["fb_choice"] = fb_choice
                    
                    # 如果选择改变了，自动调整评分
                    if old_choice != fb_choice:
                        st.session_state[feedback_key]["stars"] = 4 if fb_choice.startswith("👍") else 2
                    
                    # 星星评分组件
                    st.markdown("**评分**")
                    stars = st.session_state[feedback_key]["stars"]
                    cols = st.columns(6)
                    for i in range(6):  # 0-5分，共6个选项
                        with cols[i]:
                            label = f"{i}分" if i == 0 else f"{i}⭐"
                            if st.button(
                                label,
                                key=f"star_{i}_{idx}",
                                use_container_width=True,
                                type="primary" if stars == i else "secondary"
                            ):
                                st.session_state[feedback_key]["stars"] = i
                                st.rerun()
                    stars = st.session_state[feedback_key]["stars"]
                    # 显示当前评分
                    if stars > 0:
                        st.markdown(f"当前评分：{'⭐' * stars} ({stars}/5)")
                    else:
                        st.markdown("当前评分：⚪ (0/5)")
                    
                    tags = st.multiselect(
                        "问题类型", 
                        ["事实错误", "不清晰", "过时", "不相关", "其他"], 
                        default=st.session_state[feedback_key]["tags"],
                        key=f"tags_{idx}"
                    )
                    st.session_state[feedback_key]["tags"] = tags
                    
                    correction = st.text_area(
                        "改进答案（可选）", 
                        value=st.session_state[feedback_key]["correction"], 
                        height=100,
                        key=f"correction_{idx}"
                    )
                    st.session_state[feedback_key]["correction"] = correction
                    
                    if st.button("提交反馈", use_container_width=True, key=f"submit_feedback_{idx}"):
                        rating = stars  # 使用用户选择的评分（0-5）
                        # 获取对应的用户问题
                        user_question = st.session_state.messages[idx - 1]["content"] if idx > 0 else ""
                        assistant_answer = message["content"]
                        
                        # 更新已存在的交互记录的反馈信息
                        interaction_id = st.session_state[feedback_key].get("interaction_id")
                        if interaction_id:
                            # 更新已存在的记录
                            sources_payload = {
                                "tags": tags, 
                                "source_nodes": []
                            }
                            feedback_store.update_interaction_feedback(interaction_id, rating, correction)
                        else:
                            # 如果没有interaction_id，创建新记录（兼容旧逻辑）
                            sources_payload = {
                                "tags": tags, 
                                "source_nodes": []
                            }
                            feedback_store.add_interaction(user_question, assistant_answer, str(sources_payload), rating, correction)
                        
                        # 标记为已提交
                        st.session_state[feedback_key]["submitted"] = True
                        
                        # 清除相关页面的缓存，确保数据实时更新
                        # 清除反馈空间和意图空间的缓存
                        st.cache_data.clear()
                        
                        # 如果有正面反馈和改进建议，更新意图索引
                        if rating >= 4 and len(correction.strip()) > 0:
                            try:
                                cache_key = get_rag_manager_cache_key()
                                rag_manager = load_rag_manager(_cache_key=cache_key)
                                if rag_manager:
                                    rag_manager.refresh_intent_index()
                                    st.info("🔄 意图索引已更新")
                            except Exception as e:
                                st.warning(f"⚠️ 更新意图索引时出错: {e}")
                        
                        st.rerun()  # 刷新页面以显示已提交状态

# --- 接收用户输入并生成响应 ---
if prompt := st.chat_input("请在这里输入您的问题..."):
    # 将用户消息添加到聊天记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示思考中的提示
    with st.chat_message("assistant"):
        # 初始化变量，确保在所有代码路径中都有定义
        thinking_content_final = ""  # 用于存储最终的思考过程内容
        full_response = ""  # 用于存储最终的回答内容
        thinking_placeholder = None
        src_nodes = []  # 源节点列表
        sources_str = ""  # 来源字符串
        used_intent_space = False  # 是否使用意图空间
        intent_score = 0.0  # 意图空间相似度分数
        if show_thinking:
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("💭 **思考过程：**\n\n*正在分析问题...*")
        message_placeholder = st.empty()
        message_placeholder.markdown("正在思考中...")

        try:
            if rag_enabled:
                # 行业助手模式：参考知识空间、意图空间和反馈空间
                try:
                    cache_key = get_rag_manager_cache_key()
                    rag_manager = load_rag_manager(_cache_key=cache_key)
                    if rag_manager is not None:
                        try:
                            full_response, src_nodes, sources_str, used_intent_space, intent_score = handle_industry_assistant(
                                rag_manager=rag_manager,
                                prompt=prompt,
                                message_placeholder=message_placeholder,
                                thinking_placeholder=thinking_placeholder,
                                k_intent=k_intent,
                                k_knowledge=k_knowledge,
                                intent_threshold=intent_threshold,
                                show_thinking=show_thinking
                            )
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                        except Exception as e:
                            logging.error(f"行业助手处理失败: {e}", exc_info=True)
                            error_msg = f"❌ 行业助手处理失败: {str(e)}"
                            st.error(error_msg)
                            full_response = f"抱歉，处理问题时出现错误: {str(e)}"
                            message_placeholder.markdown(full_response)
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            src_nodes = []
                            sources_str = ""
                            used_intent_space = False
                            intent_score = 0.0
                    else:
                        full_response = "抱歉，系统初始化失败，请稍后重试或使用通用助手模式。"
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        src_nodes = []
                        sources_str = ""
                        used_intent_space = False
                        intent_score = 0.0
                except ImportError as e:
                    # 依赖缺失错误
                    error_msg = f"""
                    **❌ 缺少必要的依赖包**
                    
                    **错误信息：** {str(e)}
                    
                    **解决方案：**
                    1. 激活正确的 conda 环境：
                       ```bash
                       conda activate llamaindex_310
                       ```
                    2. 安装依赖：
                       ```bash
                       pip install llama-index llama-index-embeddings-dashscope
                       ```
                    3. 重启 Streamlit 应用：
                       ```bash
                       python -m streamlit run 首页.py
                       ```
                    """
                    logging.error(f"依赖缺失: {e}", exc_info=True)
                    st.error(error_msg)
                    full_response = "⚠️ 缺少必要的依赖包，请按照提示安装后重启应用。"
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    src_nodes = []
                    sources_str = ""
                    used_intent_space = False
                    intent_score = 0.0
                except Exception as e:
                    logging.error(f"加载RAG管理器失败: {e}", exc_info=True)
                    error_msg = f"❌ 加载RAG管理器失败: {str(e)}"
                    st.error(error_msg)
                    full_response = f"抱歉，系统初始化失败: {str(e)}。请稍后重试或使用通用助手模式。"
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    src_nodes = []
                    sources_str = ""
                    used_intent_space = False
                    intent_score = 0.0
            else:
                # 通用助手模式：直接调用LLM，不使用RAG
                full_response, src_nodes, sources_str = handle_general_assistant(
                    prompt=prompt,
                    message_placeholder=message_placeholder,
                    thinking_placeholder=thinking_placeholder,
                    show_thinking=show_thinking
                )
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                used_intent_space = False
                intent_score = 0.0
            
            # 自动记录问答交互（无反馈），用于统计高频问题
            sources_payload = {
                "source_nodes": src_nodes and [getattr(n.node, "metadata", {}) for n in src_nodes] or []
            }
            interaction_id = feedback_store.add_interaction_without_feedback(
                prompt, 
                full_response, 
                str(sources_payload)
            )
            # 将interaction_id存储到session_state，以便后续更新反馈
            current_msg_idx = len(st.session_state.messages) - 1
            feedback_key = f"feedback_{current_msg_idx}"
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = {
                    "fb_choice": "👍 有帮助",
                    "stars": 4,
                    "tags": [],
                    "correction": "",
                    "submitted": False,
                    "interaction_id": interaction_id  # 存储交互ID
                }
            else:
                st.session_state[feedback_key]["interaction_id"] = interaction_id
            
            # 计算并显示评估指标
            metrics = calculate_metrics(
                answer=full_response,
                src_nodes=src_nodes,
                used_intent_space=used_intent_space,
                intent_score=intent_score
            )
            
            # 显示评估指标（紧凑版）
            with st.expander("📊 评估指标", expanded=False):
                if rag_enabled:
                    # 行业助手模式：紧凑布局
                    # 第一行：基础指标
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("检索文档数", metrics.retrieval_count)
                    with col2:
                        st.metric("回答长度", f"{metrics.answer_length} 字符")
                    with col3:
                        if metrics.max_similarity_score > 0:
                            st.metric("最高相似度", f"{metrics.max_similarity_score:.3f}")
                        else:
                            st.metric("最高相似度", "N/A")
                    with col4:
                        st.metric("意图匹配", "✅" if metrics.used_intent_space else "❌")
                    
                    # 第二行：评估指标（置信度、精确率、召回率、F1）
                    eval_col1, eval_col2, eval_col3, eval_col4 = st.columns(4)
                    with eval_col1:
                        st.metric("置信度", f"{metrics.confidence:.3f}")
                    with eval_col2:
                        st.metric("精确率", f"{metrics.precision:.3f}")
                    with eval_col3:
                        st.metric("召回率", f"{metrics.recall:.3f}")
                    with eval_col4:
                        st.metric("F1分数", f"{metrics.f1_score:.3f}")
                else:
                    # 通用助手模式：紧凑布局
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("回答长度", f"{metrics.answer_length} 字符")
                    with col2:
                        st.metric("回答词数", f"{metrics.answer_word_count} 词")
                    with col3:
                        st.metric("置信度", f"{metrics.confidence:.3f}" if metrics.confidence > 0 else "N/A")
                    with col4:
                        st.caption("💡 通用助手模式不使用RAG检索")
            
            # 显示来源信息
            if rag_enabled and src_nodes:
                with st.expander("📚 来源与评分", expanded=False):
                    for i, n in enumerate(src_nodes[:3], 1):  # 只显示前3个
                        md = getattr(n.node, "metadata", {})
                        sc = getattr(n, "score", None)
                        st.markdown(f"**来源 {i}**")
                        st.json({"metadata": md, "相似度分数": sc})
            
            # 反馈功能 - 为新生成的回答创建反馈
            # 获取当前消息的索引（已在上面定义）
            
            # 如果已经提交过，显示已提交状态
            if st.session_state[feedback_key]["submitted"]:
                st.info("✅ 反馈已提交，感谢您的反馈！")
            else:
                # 显示反馈功能
                with st.expander("💬 反馈", expanded=False):
                    fb_choice = st.radio(
                        "是否有帮助", 
                        ["👍 有帮助", "👎 无帮助"], 
                        horizontal=True,
                        key=f"fb_choice_{current_msg_idx}",
                        index=0 if st.session_state[feedback_key]["fb_choice"] == "👍 有帮助" else 1
                    )
                    # 检查选择是否改变，如果改变则自动调整评分
                    old_choice = st.session_state[feedback_key]["fb_choice"]
                    st.session_state[feedback_key]["fb_choice"] = fb_choice
                    
                    # 如果选择改变了，自动调整评分
                    if old_choice != fb_choice:
                        st.session_state[feedback_key]["stars"] = 4 if fb_choice.startswith("👍") else 2
                    
                    # 星星评分组件
                    st.markdown("**评分**")
                    stars = st.session_state[feedback_key]["stars"]
                    cols = st.columns(6)
                    for i in range(6):  # 0-5分，共6个选项
                        with cols[i]:
                            star_text = "⭐" * i if i > 0 else "⚪"
                            label = f"{i}分" if i == 0 else f"{i}⭐"
                            if st.button(
                                label,
                                key=f"star_{i}_{current_msg_idx}",
                                use_container_width=True,
                                type="primary" if stars == i else "secondary"
                            ):
                                st.session_state[feedback_key]["stars"] = i
                                st.rerun()
                    stars = st.session_state[feedback_key]["stars"]
                    # 显示当前评分
                    if stars > 0:
                        st.markdown(f"当前评分：{'⭐' * stars} ({stars}/5)")
                    else:
                        st.markdown("当前评分：⚪ (0/5)")
                    
                    tags = st.multiselect(
                        "问题类型", 
                        ["事实错误", "不清晰", "过时", "不相关", "其他"], 
                        default=st.session_state[feedback_key]["tags"],
                        key=f"tags_{current_msg_idx}"
                    )
                    st.session_state[feedback_key]["tags"] = tags
                    
                    correction = st.text_area(
                        "改进答案（可选）", 
                        value=st.session_state[feedback_key]["correction"], 
                        height=100,
                        key=f"correction_{current_msg_idx}"
                    )
                    st.session_state[feedback_key]["correction"] = correction
                    
                    if st.button("提交反馈", use_container_width=True, key=f"submit_feedback_{current_msg_idx}"):
                        rating = stars  # 使用用户选择的评分（0-5）
                        # 更新已存在的交互记录的反馈信息
                        interaction_id = st.session_state[feedback_key].get("interaction_id")
                        if interaction_id:
                            # 更新已存在的记录
                            sources_payload = {
                                "tags": tags, 
                                "source_nodes": src_nodes and [getattr(n.node, "metadata", {}) for n in src_nodes] or []
                            }
                            # 更新sources字段以包含tags
                            feedback_store.update_interaction_feedback(interaction_id, rating, correction)
                        else:
                            # 如果没有interaction_id，创建新记录（兼容旧逻辑）
                            sources_payload = {
                                "tags": tags, 
                                "source_nodes": src_nodes and [getattr(n.node, "metadata", {}) for n in src_nodes] or []
                            }
                            feedback_store.add_interaction(prompt, full_response, str(sources_payload), rating, correction)
                        
                        # 标记为已提交
                        st.session_state[feedback_key]["submitted"] = True
                        
                        # 清除相关页面的缓存，确保数据实时更新
                        # 清除反馈空间和意图空间的缓存
                        st.cache_data.clear()
                        
                        # 如果有正面反馈和改进建议，更新意图索引
                        if rating >= 4 and len(correction.strip()) > 0 and rag_manager is not None:
                            try:
                                rag_manager.refresh_intent_index()
                                st.info("🔄 意图索引已更新")
                            except Exception as e:
                                st.warning(f"⚠️ 更新意图索引时出错: {e}")
                        
                        st.rerun()  # 刷新页面以显示已提交状态

        except Exception as e:
            error_message = f"抱歉，回答时遇到了一个错误：{str(e)}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            # 确保变量已定义（使用默认值）
            if not full_response:
                full_response = error_message
            
            # 即使出错也显示评估指标（如果有部分数据）
            try:
                metrics = calculate_metrics(
                    answer=full_response,
                    src_nodes=src_nodes,
                    used_intent_space=used_intent_space,
                    intent_score=intent_score
                )
                with st.expander("📊 评估指标", expanded=False):
                    st.caption("⚠️ 由于发生错误，部分指标可能不完整")
                    if rag_enabled:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("检索文档数", metrics.retrieval_count)
                        with col2:
                            st.metric("置信度", f"{metrics.confidence:.3f}")
                        with col3:
                            st.metric("精确率", f"{metrics.precision:.3f}")
                        with col4:
                            st.metric("召回率", f"{metrics.recall:.3f}")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("回答长度", f"{metrics.answer_length} 字符")
                        with col2:
                            st.metric("置信度", f"{metrics.confidence:.3f}" if metrics.confidence > 0 else "N/A")
            except Exception as eval_error:
                logging.warning(f"计算评估指标失败: {eval_error}")
