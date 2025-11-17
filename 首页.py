"""
AI RAG Pro 启动与配置脚本
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
import os
from pathlib import Path
import logging

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path
setup_project_path()

from src.retriever import RAGManager

# --- RAG管理器加载函数 ---
@st.cache_resource
def load_rag_manager(_cache_key=None):
    """
    加载RAG管理器
    使用缓存键确保配置改变时重新加载
    """
    try:
        from llama_index.embeddings.dashscope import DashScopeEmbedding
    except ImportError:
        pass
    return RAGManager()

def get_rag_manager_cache_key():
    """生成缓存键，基于配置文件的修改时间"""
    config_file = Path(__file__).parent / "config" / "config.json"
    if config_file.exists():
        return str(config_file.stat().st_mtime)
    return "default"

# --- 页面配置 (必须是第一个st命令) ---
st.set_page_config(
    page_title="AI RAG Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 加载API密钥 ---
from config.load_key import load_key
load_key()

# --- 预加载RAG管理器 ---
try:
    cache_key = get_rag_manager_cache_key()
    load_rag_manager(_cache_key=cache_key)
except Exception as e:
    logging.warning(f"无法在首页预加载RAG管理器: {e}")

# --- 自定义CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA;
        color: #212529;
    }

    .stApp {
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 2rem;
    }

    .stButton>button {
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
    }

    /* Hero区域 */
    .hero-section {
        text-align: center;
        padding: 5rem 3rem;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 32px;
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.2);
        margin-bottom: 4rem;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.1;
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.75rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    .hero-description {
        font-size: 1.15rem;
        color: #718096;
        max-width: 850px;
        margin: 0 auto;
        line-height: 1.9;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        z-index: 1;
    }
    
    /* Features Section */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    .feature-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
        border: 1px solid #E9ECEF;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .feature-description {
        font-size: 0.95rem;
        color: #6C757D;
        line-height: 1.5;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid #E9ECEF;
        color: #8A9AAB;
    }
    .footer-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #343A40;
    }
    
    @keyframes fade-in-up {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .fade-in-up {
        animation: fade-in-up 0.6s ease-out forwards;
    }

</style>
""", unsafe_allow_html=True)


# --- Hero区域 ---
st.markdown("""
<div class="hero-section fade-in-up">
    <div class="hero-title">🤖 AI RAG Pro</div>
    <div class="hero-subtitle">智能问答系统</div>
    <div class="hero-description">
        基于大语言模型（LLM）和检索增强生成（RAG）技术的智能问答系统，
        采用三层知识空间架构，提供精准、可追溯、可进化的问答服务。
    </div>
    <div class="hero-badge">✨ 让AI更智能，让知识更易用</div>
</div>
""", unsafe_allow_html=True)


# --- 快速导航 ---
st.subheader("功能导航")
cols = st.columns(4)
nav_items = {
    "问答系统": {"icon": "💬", "page": "1_问答系统.py"},
    "知识空间": {"icon": "📚", "page": "2_知识空间.py"},
    "意图空间": {"icon": "🎯", "page": "3_意图空间.py"},
    "反馈空间": {"icon": "📝", "page": "4_反馈空间.py"}
}

for i, (title, props) in enumerate(nav_items.items()):
    with cols[i]:
        if st.button(f"{props['icon']} {title}", use_container_width=True, key=f"nav_{i}"):
            st.switch_page(f"pages/{props['page']}")


# --- 功能特性 ---
st.markdown("---")
st.subheader("核心功能")
st.markdown("""
<div class="features-grid">
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">三层知识空间</div>
        <div class="feature-description">独创的知识、意图、反馈三层知识空间架构，实现知识的精准检索与持续进化。</div>
            </div>
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">多源知识接入</div>
        <div class="feature-description">支持文档、数据库、API等多种知识源接入，轻松构建行业专属知识库。</div>
            </div>
    <div class="feature-card">
        <div class="feature-icon">🔄</div>
        <div class="feature-title">智能意图识别</div>
        <div class="feature-description">通过意图空间准确理解用户查询，匹配最相关的知识与服务。</div>
            </div>
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">反馈驱动优化</div>
        <div class="feature-description">利用用户反馈持续优化问答效果，形成数据驱动的系统进化闭环。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- 系统架构图 ---
st.markdown("---")
st.subheader("核心架构")

# --- 三层架构示意图 ---
diagram_html = """
<style>
    .architecture-diagram {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 28px;
        padding: 3rem;
        margin: 3rem 0;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .architecture-diagram::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4f46e5, #312e81, #f97316);
    }
    
    .diagram-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #2d3748;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4f46e5 0%, #312e81 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .diagram-subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }
    
    .arch-svg {
        width: 100%;
        height: auto;
        max-width: 1000px;
        margin: 0 auto;
        display: block;
    }
    
    .arch-node {
        fill: white;
        stroke: #4f46e5;
        stroke-width: 2.5;
        rx: 12;
        transition: all 0.3s;
    }
    
    .arch-node:hover {
        fill: #f0f4ff;
        stroke-width: 3;
        filter: drop-shadow(0 4px 8px rgba(79, 70, 229, 0.3));
    }
    
    .arch-text {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 14px;
        fill: #2d3748;
        text-anchor: middle;
    }
    
    .arch-desc {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 11px;
        fill: #718096;
        text-anchor: middle;
    }
    
    .arch-arrow {
        stroke: #4f46e5;
        stroke-width: 2.5;
        fill: none;
        marker-end: url(#arrowhead);
        opacity: 0.7;
        transition: all 0.3s;
    }
    
    .arch-arrow:hover {
        stroke-width: 3;
        opacity: 1;
    }
    
    .arch-cycle-arrow {
        stroke: #f97316;
        stroke-width: 3;
        fill: none;
        marker-end: url(#arrowhead-cycle);
        stroke-dasharray: 5,5;
        animation: dash 3s linear infinite;
    }
    
    @keyframes dash {
        to {
            stroke-dashoffset: -20;
        }
    }
    
    .arch-icon {
        font-size: 32px;
        text-anchor: middle;
    }
</style>

<div class="architecture-diagram">
    <div class="diagram-title">🎯 三层知识空间架构</div>
    <div class="diagram-subtitle">持续优化闭环流程示意图</div>
    
    <svg class="arch-svg" viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#4f46e5" />
            </marker>
            <marker id="arrowhead-cycle" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#f97316" />
            </marker>
        </defs>
        
        <g>
            <rect x="400" y="20" width="200" height="80" class="arch-node" rx="12"/>
            <text x="500" y="50" class="arch-text">👤 用户提问</text>
            <text x="500" y="70" class="arch-desc">User Query</text>
        </g>
        
        <g>
            <rect x="50" y="180" width="200" height="120" class="arch-node" rx="12"/>
            <text x="150" y="210" class="arch-icon">📚</text>
            <text x="150" y="235" class="arch-text">知识空间</text>
            <text x="150" y="250" class="arch-desc">Knowledge Space</text>
            <text x="150" y="270" class="arch-desc">原始知识文档</text>
            
            <rect x="400" y="180" width="200" height="120" class="arch-node" rx="12"/>
            <text x="500" y="210" class="arch-icon">🎯</text>
            <text x="500" y="235" class="arch-text">意图空间</text>
            <text x="500" y="250" class="arch-desc">Intent Space</text>
            <text x="500" y="270" class="arch-desc">高质量问答对</text>
            
            <rect x="750" y="180" width="200" height="120" class="arch-node" rx="12"/>
            <text x="850" y="210" class="arch-icon">💬</text>
            <text x="850" y="235" class="arch-text">反馈空间</text>
            <text x="850" y="250" class="arch-desc">Feedback Space</text>
            <text x="850" y="270" class="arch-desc">用户反馈数据</text>
        </g>
        
        <g>
            <rect x="350" y="380" width="300" height="100" class="arch-node" rx="12"/>
            <text x="500" y="415" class="arch-icon">🔍</text>
            <text x="500" y="440" class="arch-text">RAG检索引擎</text>
            <text x="500" y="455" class="arch-desc">向量相似度匹配</text>
            <text x="500" y="470" class="arch-desc">智能检索与融合</text>
        </g>
        
        <g>
            <rect x="400" y="540" width="200" height="80" class="arch-node" rx="12"/>
            <text x="500" y="570" class="arch-icon">🤖</text>
            <text x="500" y="590" class="arch-text">LLM生成回答</text>
            <text x="500" y="605" class="arch-desc">生成最终答案</text>
        </g>
        
        <g>
            <rect x="50" y="540" width="200" height="80" class="arch-node" rx="12"/>
            <text x="150" y="570" class="arch-icon">📊</text>
            <text x="150" y="590" class="arch-text">评估指标</text>
            <text x="150" y="605" class="arch-desc">置信度/精确率/召回率</text>
            
            <rect x="750" y="540" width="200" height="80" class="arch-node" rx="12"/>
            <text x="850" y="570" class="arch-icon">👍</text>
            <text x="850" y="590" class="arch-text">用户反馈</text>
            <text x="850" y="605" class="arch-desc">评分/标签/改进建议</text>
        </g>
        
        <line x1="450" y1="100" x2="150" y2="180" class="arch-arrow"/>
        <line x1="500" y1="100" x2="500" y2="180" class="arch-arrow"/>
        <line x1="550" y1="100" x2="850" y2="180" class="arch-arrow"/>
        
        <line x1="150" y1="300" x2="400" y2="430" class="arch-arrow"/>
        <line x1="500" y1="300" x2="500" y2="380" class="arch-arrow"/>
        <line x1="850" y1="300" x2="600" y2="430" class="arch-arrow"/>
        
        <line x1="500" y1="480" x2="500" y2="540" class="arch-arrow"/>
        
        <line x1="450" y1="580" x2="250" y2="580" class="arch-arrow"/>
        <line x1="550" y1="580" x2="750" y2="580" class="arch-arrow"/>
        
        <path d="M 850 540 Q 900 400, 850 300" class="arch-cycle-arrow"/>
        <text x="920" y="420" class="arch-desc" fill="#f97316" font-weight="600">持续优化</text>
        
        <path d="M 50 540 Q 0 400, 50 300" class="arch-cycle-arrow"/>
        <text x="10" y="420" class="arch-desc" fill="#f97316" font-weight="600">知识更新</text>
        
        <line x1="250" y1="240" x2="400" y2="240" class="arch-arrow" opacity="0.5"/>
        <line x1="400" y1="260" x2="250" y2="260" class="arch-arrow" opacity="0.5"/>
        <text x="325" y="245" class="arch-desc" fill="#4f46e5" font-size="10px">知识提取</text>
    </svg>
    
    <div style="margin-top: 2rem; padding: 1.5rem; background: #f7fafc; border-radius: 16px; border-left: 4px solid #4f46e5;">
        <h4 style="color: #2d3748; margin-bottom: 1rem; font-weight: 700;">🔄 持续优化闭环说明</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; color: #4a5568; line-height: 1.8;">
            <div>
                <strong style="color: #4f46e5;">1. 知识检索</strong><br/>
                用户提问 → 从三层空间检索相关信息
            </div>
            <div>
                <strong style="color: #4f46e5;">2. 智能生成</strong><br/>
                RAG引擎融合信息 → LLM生成回答
            </div>
            <div>
                <strong style="color: #f97316;">3. 评估反馈</strong><br/>
                评估指标 + 用户反馈 → 识别改进点
            </div>
            <div>
                <strong style="color: #f97316;">4. 持续优化</strong><br/>
                优质反馈 → 更新意图空间 → 提升响应质量
            </div>
        </div>
     </div>
</div>
"""

components.html(diagram_html, height=900)



# --- 技术栈 ---
st.markdown("---")
st.subheader("技术栈")
st.markdown("""
- **核心框架**: Streamlit, LlamaIndex
- **大语言模型**: OpenAI, DeepSeek, 千问
- **向量数据库**: ChromaDB
- **数据处理**: Pandas, NumPy
""")

# --- 页脚 ---
st.markdown("""
<div class="footer">
    <p class="footer-title">🤖 AI RAG Pro</p>
    <p>基于大语言模型和检索增强生成技术的智能问答系统</p>
    <p style="opacity: 0.85; font-size: 0.95rem; margin-top: 1rem;">Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
