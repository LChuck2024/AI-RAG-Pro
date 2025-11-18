"""
知识空间页面
显示和管理知识空间中的文档内容
"""
import streamlit as st
import os
import pandas as pd
import plotly.express as px
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from src.utils import setup_project_path, format_local_time

# 将项目根目录添加到Python路径中
setup_project_path()

from config.load_key import load_config
from 首页 import load_rag_manager, get_rag_manager_cache_key

st.set_page_config(
    page_title="知识空间管理",
    page_icon="📚",
    layout="wide",
)

# 自定义CSS
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
        max-width: 1600px;
    }
    
    /* 文档卡片样式 */
    .doc-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .doc-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    
    /* 文档内容框样式 */
    .doc-content-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    /* 按钮样式优化 */
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
    
    /* 信息框样式 */
    .stInfo {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
    }
    
    /* 表格样式优化 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 统计指标样式 */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* 搜索框样式 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e1e8ed;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_knowledge_space() -> list[dict[str, str]]:
    """
    加载知识空间中的所有文档
    
    Returns:
        list[dict]: 文档列表，每个元素包含file_name, content, file_path
    """
    config = load_config()
    rag_config = config.get("rag", {})
    knowledge_space_dir = rag_config.get("knowledge_space_dir", "./rag_source/knowledge_space")
    
    documents = []
    if not os.path.exists(knowledge_space_dir):
        return documents
    
    # 遍历目录下的所有文件
    for file_name in os.listdir(knowledge_space_dir):
        file_path = os.path.join(knowledge_space_dir, file_name)
        if os.path.isfile(file_path) and (file_name.endswith('.txt') or file_name.endswith('.md')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents.append({
                    'file_name': file_name,
                    'content': content,
                    'file_path': file_path,
                    'file_size': len(content),
                    'word_count': len(content)
                })
            except Exception as e:
                st.warning(f"读取文件 {file_name} 时出错: {e}")
    
    return documents

# 页面标题
st.markdown("""
<div style='text-align: left; margin-bottom: 2rem;'>
    <h1 style='margin: 0; color: #2c3e50; font-size: 2.5rem;'>📚 知识空间</h1>
    <p style='margin: 0.5rem 0 0 0; color: #5a6c7d; font-size: 1.1rem;'>查看和管理知识空间中的文档内容</p>
</div>
""", unsafe_allow_html=True)

# 页面功能说明
st.info("""
**📋 功能说明：** 管理知识空间中的文档，这些文档将用于RAG检索。支持查看文档内容、搜索关键词、统计文档信息等功能。
""")

# 加载数据
@st.cache_data(ttl=5)  # 5秒缓存，确保数据实时更新
def load_cached_knowledge_space():
    return load_knowledge_space()

all_documents = load_cached_knowledge_space()

# 侧边栏 - 统计信息
with st.sidebar:
    st.markdown("### 📊 统计信息")
    
    if all_documents:
        total_docs = len(all_documents)
        total_words = sum(doc['word_count'] for doc in all_documents)
        avg_words = total_words / total_docs if total_docs > 0 else 0
        total_size = sum(doc['file_size'] for doc in all_documents)
        
        st.metric("文档总数", total_docs)
        st.metric("总字数", f"{total_words:,}")
        st.metric("平均字数", f"{avg_words:.0f}")
        st.metric("总大小", f"{total_size / 1024:.2f} KB")
    else:
        st.metric("文档总数", 0)
        st.metric("总字数", 0)
    
    st.markdown("---")
    
    # 操作按钮
    st.markdown("### 🛠️ 操作")
    if st.button("🔄 刷新数据", use_container_width=True):
        # 清除缓存
        st.cache_data.clear()
        st.rerun()
    
    # 自动刷新提示
    st.caption("💡 数据每5秒自动更新，或点击刷新按钮立即更新")

# --- 缓存函数 ---
@st.cache_data(ttl=3600)  # 缓存1小时
def get_loaded_documents(_rag_manager):
    """从知识空间目录加载文档列表和内容"""
    if _rag_manager and hasattr(_rag_manager, 'knowledge_space_dir'):
        docs_dir = _rag_manager.knowledge_space_dir
        if os.path.exists(docs_dir):
            doc_list = []
            for filename in os.listdir(docs_dir):
                if not filename.startswith('.'):  # 忽略隐藏文件
                    filepath = os.path.join(docs_dir, filename)
                    try:
                        # 获取文件元数据
                        stat = os.stat(filepath)
                        last_modified = format_local_time(datetime.fromtimestamp(stat.st_mtime).isoformat())
                        file_size = f"{stat.st_size / 1024:.2f} KB" if stat.st_size > 1024 else f"{stat.st_size} B"
                        
                        # 读取文件内容（限制大小以避免UI卡顿）
                        content = ""
                        if stat.st_size < 1024 * 1024: # 只读取小于1MB的文件内容
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        
                        doc_list.append({
                            "name": filename,
                            "modified": last_modified,
                            "size": file_size,
                            "content": content
                        })
                    except Exception as e:
                        st.warning(f"读取文件 '{filename}' 失败: {e}")
            # 按文件名排序
            return sorted(doc_list, key=lambda x: x['name'])
    return []

# --- 页面加载 ---
rag_manager = None
try:
    cache_key = get_rag_manager_cache_key()
    rag_manager = load_rag_manager(_cache_key=cache_key)
except Exception as e:
    st.error(f"❌ RAG 管理器加载失败: {e}")
    st.warning("请检查 API 密钥配置和网络连接。")

# --- 主体内容 ---
if rag_manager:
    # st.header("📚 文档概览")

    with st.container():
        # --- 统计信息 ---
        st.markdown("#### 📊 统计概览")
        documents_for_stats = get_loaded_documents(rag_manager)
        
        if documents_for_stats:

            # --- Visualizations ---
            df_stats = pd.DataFrame(documents_for_stats)
            df_stats['word_count'] = df_stats['content'].str.len()
            df_stats['file_type'] = df_stats['name'].apply(lambda x: x.split('.')[-1])

            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                # File Type Distribution (Pie Chart)
                st.markdown("###### 文件类型分布")
                file_type_counts = df_stats['file_type'].value_counts().reset_index()
                file_type_counts.columns = ['file_type', 'count']
                fig_pie = px.pie(
                    file_type_counts, 
                    names='file_type', 
                    values='count', 
                    title='', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_traces(
                    textinfo='percent+label', 
                    textposition='inside',
                    hovertemplate='类型: %{label}<br>数量: %{value}<br>占比: %{percent}'
                )
                fig_pie.update_layout(
                    showlegend=False, 
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with viz_col2:
                # Document Length Distribution (Bar Chart)
                st.markdown("###### 文档长度分布 (按字数)")
                bins = [0, 500, 2000, 5000, float('inf')]
                labels = ['0-500', '500-2k', '2k-5k', '5k+']
                df_stats['length_bin'] = pd.cut(df_stats['word_count'], bins=bins, labels=labels, right=False)
                length_counts = df_stats['length_bin'].value_counts().sort_index().reset_index()
                length_counts.columns = ['length_bin', 'count']
                fig_bar = px.bar(
                    length_counts, 
                    x='length_bin', 
                    y='count', 
                    title='',
                    text_auto=True # Display count on bars
                )
                fig_bar.update_traces(
                    marker_color='rgb(102, 126, 234)', 
                    marker_line_color='rgb(8, 48, 107)',
                    marker_line_width=1.5, 
                    opacity=0.8,
                    hovertemplate='字数区间: %{x}<br>文档数量: %{y}'
                )
                fig_bar.update_layout(
                    xaxis_title=None, 
                    yaxis_title="文档数", 
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            

        else:
            st.metric("文档总数", "0 篇")
        
        st.markdown("---")
        
        # --- File Upload Section ---
        st.markdown("#### ⬆️ 上传新文档")
        uploaded_files = st.file_uploader(
            "将文件拖拽至此或点击上传",
            accept_multiple_files=True,
            type=['txt', 'md', 'pdf', 'docx', 'csv'],
            label_visibility="collapsed"
        )
        if uploaded_files:
            success_count = 0
            for uploaded_file in uploaded_files:
                save_path = os.path.join(rag_manager.knowledge_space_dir, uploaded_file.name)
                try:
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ 文件 '{uploaded_file.name}' 上传失败: {e}")
            if success_count > 0:
                st.success(f"✅ 成功上传 {success_count} 个文件！")
                st.info("💡 请点击下方的 **刷新索引** 按钮以应用更改。")
                get_loaded_documents.clear()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 刷新知识索引", use_container_width=True, type="primary"):
                with st.spinner("正在刷新知识空间索引..."):
                    try:
                        rag_manager.refresh_knowledge_index()
                        st.success("✅ 知识空间索引已刷新！")
                        get_loaded_documents.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 刷新索引时出错: {e}")
        with col2:
            if st.button("💥 重置向量库", use_container_width=True):
                st.session_state['confirm_reset'] = True
        st.markdown("---")


    st.markdown("#### 📂 文档列表")
    documents = get_loaded_documents(rag_manager)
    
    if not documents:
        st.info("当前知识空间为空。请在右侧上传您的第一个文档。")
    else:
        # [Corrected Logic] Move expander outside the loop
        with st.expander(f"查看全部 {len(documents)} 个文档", expanded=True):
            # Loop through documents inside the expander
            for doc in documents:
                file_extension = doc['name'].split('.')[-1]
                icon_map = {"md": "📝", "txt": "📄", "pdf": "📕", "docx": "📘", "csv": "📊"}
                icon = icon_map.get(file_extension, "📁")

                with st.container():
                    col1, col2 = st.columns([0.8, 0.2]) # 80% for info, 20% for buttons
                    with col1:
                        st.markdown(f"""
                        <div class="doc-card">
                            <div class="doc-title">{icon} {doc['name']}</div>
                            <div class="doc-meta">大小: {doc['size']} | 最后修改: {doc['modified']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.write("") # Spacer for vertical alignment
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            # Toggle view state on button click
                            if st.button("查看", key=f"view_{doc['name']}", use_container_width=True):
                                if st.session_state.get('doc_to_view_name') == doc['name']:
                                    st.session_state['doc_to_view_name'] = None
                                else:
                                    st.session_state['doc_to_view_name'] = doc['name']
                        with btn_col2:
                            if st.button("删除", key=f"delete_{doc['name']}", use_container_width=True, type="secondary"):
                                st.session_state['doc_to_delete'] = doc

                    # In-place preview logic
                    if st.session_state.get('doc_to_view_name') == doc['name']:
                        st.markdown("---")
                        st.code(doc['content'] if doc['content'] else "（文件内容为空或过大无法预览）", language="markdown")
                        if st.button("关闭预览", key=f"close_view_{doc['name']}", use_container_width=True):
                            st.session_state['doc_to_view_name'] = None
                            st.rerun()
    
    # --- Modal logic for deletion/reset ---
    if st.session_state.get('doc_to_delete'):
        doc = st.session_state['doc_to_delete']
        st.warning(f"您确定要删除文件 **{doc['name']}** 吗？此操作不可恢复。")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 确认删除", use_container_width=True, type="primary"):
                try:
                    os.remove(os.path.join(rag_manager.knowledge_space_dir, doc['name']))
                    st.success(f"文件 '{doc['name']}' 已删除。请刷新索引。")
                    del st.session_state['doc_to_delete']
                    get_loaded_documents.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除文件时出错: {e}")
                    del st.session_state['doc_to_delete']
     
        with c2:
            if st.button("❌ 取消", use_container_width=True):
                del st.session_state['doc_to_delete']
                st.rerun()

        if st.session_state.get('confirm_reset'):
            st.warning("您确定要重置整个向量数据库吗？所有索引都将被删除并需要重新构建。")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 确认重置", use_container_width=True, type="primary"):
                    with st.spinner("正在重置向量数据库..."):
                        try:
                            result = rag_manager.reset_vector_db()
                            st.success(f"✅ {result}")
                            load_rag_manager.clear()
                            get_loaded_documents.clear()
                            del st.session_state['confirm_reset']
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 重置向量数据库时出错: {e}")
                            del st.session_state['confirm_reset']
            with c2:
                if st.button("❌ 取消重置", use_container_width=True):
                    del st.session_state['confirm_reset']
                    st.rerun()
else:
    # RAG Manager 加载失败时的提示
    st.error("❌ RAG 管理器加载失败。")
    st.warning("请检查 API 密钥配置或网络连接。")

