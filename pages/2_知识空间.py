"""
知识空间页面
显示和管理知识空间中的文档内容
"""
import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path
setup_project_path()

from config.load_key import load_config

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

def load_knowledge_space() -> List[Dict[str, str]]:
    """
    加载知识空间中的所有文档
    
    Returns:
        List[Dict]: 文档列表，每个元素包含file_name, content, file_path
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
<div style='text-align: center; margin-bottom: 2rem;'>
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

# 主要内容区域
if not all_documents:
    st.info("📭 知识空间中暂无文档。请将文档文件（.txt 或 .md 格式）放入 `rag_source/knowledge_space/` 目录。")
else:
    # 搜索功能
    search_query = st.text_input("🔍 搜索文档", placeholder="输入关键词搜索文档名称或内容...", help="在文档名称和内容中搜索关键词")
    
    # 筛选数据（排除空文档）
    filtered_documents = [doc for doc in all_documents if doc['content'].strip()]
    if search_query:
        search_lower = search_query.lower()
        filtered_documents = [
            doc for doc in filtered_documents
            if search_lower in doc['file_name'].lower() or search_lower in doc['content'].lower()
        ]
    
    # 显示统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总文档数", len(all_documents))
    with col2:
        st.metric("当前显示", len(filtered_documents))
    with col3:
        total_words_display = sum(doc['word_count'] for doc in filtered_documents)
        st.metric("总字数", f"{total_words_display:,}")
    with col4:
        avg_words_display = total_words_display / len(filtered_documents) if filtered_documents else 0
        st.metric("平均字数", f"{avg_words_display:.0f}")
    
    st.markdown("---")
    
    # 表格展示
    st.markdown("### 📋 文档列表")
    
    if not filtered_documents:
        st.warning("没有找到匹配的文档。请调整搜索关键词。")
    else:
        # 准备表格数据
        table_data = []
        for idx, doc in enumerate(filtered_documents, 1):
            # 截断长文本（用于表格显示，完整内容存储在完整字段中）
            # 移除空行和多余空白，将内容压缩为单行预览
            content_clean = doc['content'].strip()
            # 移除所有换行符和多余空格，压缩为单行
            content_clean = ' '.join([line.strip() for line in content_clean.split('\n') if line.strip()])
            content_short = content_clean[:150] + "..." if len(content_clean) > 150 else content_clean
            
            table_data.append({
                "序号": idx,
                "文件名": doc['file_name'],
                "内容预览": content_short,
                "字数": doc['word_count'],
                "大小": f"{doc['file_size'] / 1024:.2f} KB",
                "完整内容": doc['content']
            })
        
        # 创建DataFrame
        df = pd.DataFrame(table_data)
        
        # 选择要显示的列
        display_columns = ["序号", "文件名", "内容预览", "字数", "大小"]
        df_display = df[display_columns].copy()
        
        # 为每行添加提示（如果内容被截断）
        for idx, row in df_display.iterrows():
            full_content = df.loc[idx, "完整内容"]
            if len(full_content) > 150:
                df_display.at[idx, "内容预览"] = f"{row['内容预览']} (点击查看详情)"
        
        # 使用st.dataframe展示表格
        selected_rows = st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "序号": st.column_config.NumberColumn("序号", width="small"),
                "文件名": st.column_config.TextColumn("文件名", width="medium"),
                "内容预览": st.column_config.TextColumn(
                    "内容预览", 
                    width="large",
                    help="内容较长时请点击下方'详细信息查看'查看完整内容"
                ),
                "字数": st.column_config.NumberColumn("字数", width="small"),
                "大小": st.column_config.TextColumn("大小", width="small"),
            }
        )
        
        st.markdown("---")
        
        # 详细信息查看区域
        st.markdown("### 🔍 详细信息查看")
        
        # 选择要查看的文档
        doc_options = [f"{idx+1}. {doc['file_name']}" for idx, doc in enumerate(filtered_documents)]
        
        if doc_options:
            selected_idx = st.selectbox(
                "选择文档查看详细信息",
                range(len(doc_options)),
                format_func=lambda x: doc_options[x],
                index=0
            )
            
            selected_doc = filtered_documents[selected_idx]
            
            # 创建两列布局
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("#### 📝 基本信息")
                info_data = {
                    "文件名": selected_doc['file_name'],
                    "字数": f"{selected_doc['word_count']:,} 字",
                    "文件大小": f"{selected_doc['file_size'] / 1024:.2f} KB",
                    "文件路径": selected_doc['file_path']
                }
                for key, value in info_data.items():
                    st.markdown(f"**{key}**: {value}")
            
            with col2:
                st.markdown("#### 📊 统计")
                st.metric("字数", selected_doc['word_count'])
                st.metric("大小", f"{selected_doc['file_size'] / 1024:.2f} KB")
            
            st.markdown("---")
            
            # 文档内容（默认收起）
            with st.expander("📄 查看文档内容", expanded=False):
                # 使用st.markdown直接渲染Markdown内容
                st.markdown(selected_doc['content'])

