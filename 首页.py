"""
AI RAG Pro 首页
项目介绍和导航页面 - 优化版
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
import os
from pathlib import Path

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path
setup_project_path()

from config.load_key import load_key

# 加载配置文件中的API密钥到环境变量
load_key()

# --- 页面配置 ---
st.set_page_config(
    page_title="AI RAG Pro - 智能问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS，美化界面
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* 隐藏默认的Streamlit元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
    
    /* 导航卡片 */
    .nav-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        height: 100%;
        border: 3px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .nav-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .nav-card:hover::before {
        left: 100%;
    }
    
    .nav-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.25);
        border-color: #667eea;
    }
    
    .nav-icon {
        font-size: 4.5rem;
        margin-bottom: 1.5rem;
        display: block;
        transition: transform 0.3s;
    }
    
    .nav-card:hover .nav-icon {
        transform: scale(1.1) rotate(5deg);
    }
    
    .nav-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.75rem;
    }
    
    .nav-desc {
        color: #718096;
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .nav-arrow {
        color: #667eea;
        font-size: 1.5rem;
        opacity: 0;
        transition: all 0.3s;
    }
    
    .nav-card:hover .nav-arrow {
        opacity: 1;
        transform: translateX(5px);
    }
    
    /* 功能卡片 */
    .feature-card {
        background: white;
        border-radius: 24px;
        padding: 3rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        border-left: 6px solid;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }
    
    .feature-card:nth-child(1) { border-left-color: #667eea; }
    .feature-card:nth-child(2) { border-left-color: #f093fb; }
    .feature-card:nth-child(3) { border-left-color: #4facfe; }
    .feature-card:nth-child(4) { border-left-color: #43e97b; }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.15);
    }
    
    .feature-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-right: 1.5rem;
        transition: transform 0.3s;
    }
    
    .feature-card:hover .feature-icon {
        transform: scale(1.1) rotate(-5deg);
    }
    
    .feature-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #2d3748;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .feature-desc {
        color: #4a5568;
        line-height: 1.9;
        font-size: 1.05rem;
    }
    
    .feature-desc ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .feature-desc li {
        margin-bottom: 0.9rem;
        position: relative;
    }
    
    .feature-desc li::marker {
        color: #667eea;
    }
    
    /* 技术栈卡片 */
    .tech-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .tech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        transform: scaleX(0);
        transition: transform 0.4s;
    }
    
    .tech-card:hover::before {
        transform: scaleX(1);
    }
    
    .tech-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .tech-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
        transition: transform 0.3s;
    }
    
    .tech-card:hover .tech-icon {
        transform: scale(1.15) rotate(5deg);
    }
    
    .tech-name {
        font-size: 1.35rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.75rem;
    }
    
    .tech-desc {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .stat-card:hover::before {
        opacity: 1;
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .stat-number {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        line-height: 1;
    }
    
    .stat-label {
        color: #4a5568;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* 分隔线 */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        margin: 4rem 0;
        border: none;
    }
    
    /* 章节标题 */
    .section-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .section-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }
    
    /* 侧边栏样式 */
    .sidebar-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: rotate 15s linear infinite;
    }
    
    .sidebar-header h2 {
        color: white;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 800;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-header p {
        color: rgba(255, 255, 255, 0.95);
        margin: 0.75rem 0 0 0;
        font-size: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        padding: 4rem 2rem;
        color: white;
        margin-top: 5rem;
        position: relative;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
    }
    
    .footer p {
        margin: 0.75rem 0;
        font-size: 1.05rem;
    }
    
    .footer-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.8rem;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
        }
        
        .nav-card {
            padding: 2rem 1.5rem;
        }
        
        .feature-card {
            padding: 2rem 1.5rem;
        }
    }
    
    /* 动画 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 架构图容器 */
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
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    .diagram-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #2d3748;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    
    /* SVG样式 */
    .arch-svg {
        width: 100%;
        height: auto;
        max-width: 1000px;
        margin: 0 auto;
        display: block;
    }
    
    .arch-node {
        fill: white;
        stroke: #667eea;
        stroke-width: 2.5;
        rx: 12;
        transition: all 0.3s;
    }
    
    .arch-node:hover {
        fill: #f0f4ff;
        stroke-width: 3;
        filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
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
        stroke: #667eea;
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
        stroke: #f093fb;
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
st.markdown('<p class="section-title">🚀 快速开始</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">点击下方卡片快速访问各个功能模块</p>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

nav_items = [
    ("💬", "问答系统", "智能问答助手，支持通用和行业两种模式", "pages/1_问答系统.py"),
    ("📚", "知识空间", "管理知识文档，构建知识库索引", "pages/2_知识空间.py"),
    ("🎯", "意图空间", "管理问答对，实现快速响应", "pages/3_意图空间.py"),
    ("💬", "反馈空间", "查看用户反馈，优化系统性能", "pages/4_反馈空间.py"),
]

for idx, (col, (icon, title, desc, page)) in enumerate(zip([nav_col1, nav_col2, nav_col3, nav_col4], nav_items)):
    with col:
        st.markdown(f"""
        <div class="nav-card fade-in-up" style="animation-delay: {idx * 0.1}s;">
            <span class="nav-icon">{icon}</span>
            <div class="nav-title">{title}</div>
            <div class="nav-desc">{desc}</div>
            <div class="nav-arrow">→</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"进入{title}", use_container_width=True, type="primary", key=f"nav_{idx}"):
            st.switch_page(page)

# --- 核心特性 ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="section-title">✨ 核心特性</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">了解AI RAG Pro的强大功能</p>', unsafe_allow_html=True)

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
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    .diagram-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #2d3748;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        stroke: #667eea;
        stroke-width: 2.5;
        rx: 12;
        transition: all 0.3s;
    }
    
    .arch-node:hover {
        fill: #f0f4ff;
        stroke-width: 3;
        filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
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
        stroke: #667eea;
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
        stroke: #f093fb;
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
                <polygon points="0 0, 10 3, 0 6" fill="#667eea" />
            </marker>
            <marker id="arrowhead-cycle" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#f093fb" />
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
        <text x="920" y="420" class="arch-desc" fill="#f093fb" font-weight="600">持续优化</text>
        
        <path d="M 50 540 Q 0 400, 50 300" class="arch-cycle-arrow"/>
        <text x="10" y="420" class="arch-desc" fill="#f093fb" font-weight="600">知识更新</text>
        
        <line x1="250" y1="240" x2="400" y2="240" class="arch-arrow" opacity="0.5"/>
        <line x1="400" y1="260" x2="250" y2="260" class="arch-arrow" opacity="0.5"/>
        <text x="325" y="245" class="arch-desc" fill="#667eea" font-size="10px">知识提取</text>
    </svg>
    
    <div style="margin-top: 2rem; padding: 1.5rem; background: #f7fafc; border-radius: 16px; border-left: 4px solid #667eea;">
        <h4 style="color: #2d3748; margin-bottom: 1rem; font-weight: 700;">🔄 持续优化闭环说明</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; color: #4a5568; line-height: 1.8;">
            <div>
                <strong style="color: #667eea;">1. 知识检索</strong><br/>
                用户提问 → 从三层空间检索相关信息
            </div>
            <div>
                <strong style="color: #667eea;">2. 智能生成</strong><br/>
                RAG引擎融合信息 → LLM生成回答
            </div>
            <div>
                <strong style="color: #f093fb;">3. 评估反馈</strong><br/>
                评估指标 + 用户反馈 → 识别改进点
            </div>
            <div>
                <strong style="color: #f093fb;">4. 持续优化</strong><br/>
                优质反馈 → 更新意图空间 → 提升响应质量
            </div>
        </div>
    </div>
</div>
"""

components.html(diagram_html, height=900)

feature_col1, feature_col2 = st.columns(2)

features = [
    ("🎯", "三层知识空间架构", [
        "<strong>知识空间</strong>：存储原始知识文档，提供权威信息源",
        "<strong>意图空间</strong>：存储高质量问答对，实现快速响应和意图引导",
        "<strong>反馈空间</strong>：收集用户反馈，形成持续学习和优化的闭环"
    ]),
    ("🔍", "智能检索系统", [
        "基于向量相似度的语义检索，精准匹配相关内容",
        "可配置的检索参数（TopK、相似度阈值）",
        "支持意图空间快速匹配，提升响应速度",
        "提供检索来源和评分信息，确保可追溯性"
    ]),
    ("🤖", "双模式助手", [
        "<strong>通用助手</strong>：直接使用大模型，适合一般性问题",
        "<strong>行业助手</strong>：基于RAG技术，从知识库检索后回答，适合专业场景",
        "支持思考过程展示，帮助理解AI推理过程",
        "流式输出，实时响应，提升交互体验"
    ]),
    ("📊", "评估与反馈", [
        "多维度评估指标（置信度、精确率、召回率、F1分数）",
        "用户反馈系统（评分、标签、改进建议）",
        "高频问题统计，发现用户关注点",
        "优质问答对自动提取，持续优化系统"
    ]),
]

for idx, (col, (icon, title, items)) in enumerate(zip([feature_col1, feature_col2, feature_col1, feature_col2], features)):
    with col:
        items_html = "".join([f"<li>{item}</li>" for item in items])
        st.markdown(f"""
        <div class="feature-card fade-in-up" style="animation-delay: {idx * 0.15}s;">
            <div class="feature-header">
                <span class="feature-icon">{icon}</span>
                <h3 class="feature-title">{title}</h3>
            </div>
            <div class="feature-desc">
                <ul>{items_html}</ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 技术栈 ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="section-title">🛠️ 技术栈</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">基于先进的技术栈构建</p>', unsafe_allow_html=True)

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

tech_stack = [
    ("🌐", "Streamlit", "快速构建交互式Web界面"),
    ("🔗", "LlamaIndex", "完整的RAG管道组件"),
    ("💾", "ChromaDB", "高性能向量存储和检索"),
    ("🧠", "Multi-LLM", "支持多种大语言模型"),
]

for idx, (col, (icon, name, desc)) in enumerate(zip([tech_col1, tech_col2, tech_col3, tech_col4], tech_stack)):
    with col:
        st.markdown(f"""
        <div class="tech-card fade-in-up" style="animation-delay: {idx * 0.1}s;">
            <span class="tech-icon">{icon}</span>
            <div class="tech-name">{name}</div>
            <div class="tech-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 使用指南 ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="section-title">📖 使用指南</p>', unsafe_allow_html=True)

guide_col1, guide_col2, guide_col3 = st.columns(3)

with guide_col1:
    with st.expander("🚀 快速开始", expanded=False):
        st.markdown("""
        #### 1. 配置API密钥
        编辑 `config/config.json` 文件：
        - **DEEPSEEK_API_KEY**（可选）
        - **OPENAI_API_KEY**（可选）
        - **DASHSCOPE_API_KEY**（必需）
        
        #### 2. 准备知识文档
        将文档放入 `rag_source/knowledge_space/` 目录
        
        #### 3. 开始使用
        点击导航按钮进入问答系统
        """)

with guide_col2:
    with st.expander("💡 功能说明", expanded=False):
        st.markdown("""
        #### 💬 问答系统
        - 通用助手：直接使用大模型
        - 行业助手：基于RAG检索
        
        #### 📚 知识空间
        - 查看和管理知识文档
        
        #### 🎯 意图空间
        - 管理问答对
        
        #### 💬 反馈空间
        - 查看用户反馈
        """)

with guide_col3:
    with st.expander("⚙️ 配置说明", expanded=False):
        st.markdown("""
        #### 模型配置
        - 默认LLM模型
        - 模型优先级顺序
        
        #### RAG配置
        - 知识空间目录
        - 检索参数设置
        - 相似度阈值配置
        """)

# --- 侧边栏信息 ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>🤖 AI RAG Pro</h2>
        <p>智能问答系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 项目信息")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric("版本", "1.0.0", delta="最新")
    with info_col2:
        st.metric("Python", "3.8+")
    
    st.info("""
    **许可证**: MIT
    
    **状态**: 开发中
    """)
    
    st.markdown("### 🔗 快速链接")
    st.markdown("""
    - 📄 [项目文档](docs/)
    - ⚙️ [配置文件](config/)
    - 📚 [知识源](rag_source/)
    """)
    
    st.markdown("### ⚠️ 注意事项")
    st.warning("""
    1. 确保已配置API密钥
    2. DashScope API Key必需
    3. 首次使用需构建索引
    4. 推荐Python 3.10+
    """)
    
    st.markdown("### 📊 系统状态")
    try:
        from src.feedback import FeedbackStore
        feedback_store = FeedbackStore()
        total_feedback = feedback_store.get_feedback_count()
        st.success(f"✅ 反馈数据: {total_feedback} 条")
    except:
        st.info("ℹ️ 系统初始化中...")

# --- 页脚 ---
st.markdown("""
<div class="footer">
    <p class="footer-title">🤖 AI RAG Pro</p>
    <p>基于大语言模型和检索增强生成技术的智能问答系统</p>
    <p style="opacity: 0.85; font-size: 0.95rem; margin-top: 1rem;">Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
