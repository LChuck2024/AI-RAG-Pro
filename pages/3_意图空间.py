"""
意图空间页面
显示和管理意图空间中的问答对
"""
import streamlit as st
import sys
import os
import re
import pandas as pd
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path, format_local_time
setup_project_path()

from config.load_key import load_config
from src.feedback import FeedbackStore

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
    
    /* 问答卡片样式 */
    .qa-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .qa-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    
    /* 问题框样式 */
    .question-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    /* 答案框样式 */
    .answer-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
    }
    
    /* 改进建议框样式 */
    .correction-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
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
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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

def parse_qa_file(file_path: str) -> List[Dict[str, str]]:
    """
    解析Q&A格式的文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        List[Dict]: 问答对列表，每个元素包含question, answer, source_file
    """
    qa_pairs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配Q:和A:格式
        pattern = r'Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        file_name = os.path.basename(file_path)
        for question, answer in matches:
            qa_pairs.append({
                'question': question.strip(),
                'answer': answer.strip(),
                'source_file': file_name
            })
    except Exception as e:
        st.error(f"解析文件 {file_path} 时出错: {e}")
    
    return qa_pairs

def load_intent_space() -> List[Dict[str, str]]:
    """
    加载意图空间中的所有问答对
    
    Returns:
        List[Dict]: 所有问答对列表
    """
    config = load_config()
    rag_config = config.get("rag", {})
    intent_space_dir = rag_config.get("intent_space_dir", "./rag_source/intent_space")
    
    all_qa_pairs = []
    
    if not os.path.exists(intent_space_dir):
        return all_qa_pairs
    
    # 遍历目录下的所有txt文件
    for file_name in os.listdir(intent_space_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(intent_space_dir, file_name)
            qa_pairs = parse_qa_file(file_path)
            all_qa_pairs.extend(qa_pairs)
    
    return all_qa_pairs

# 页面标题
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='margin: 0; color: #2c3e50; font-size: 2.5rem;'>🎯 意图空间</h1>
    <p style='margin: 0.5rem 0 0 0; color: #5a6c7d; font-size: 1.1rem;'>查看和管理意图空间中的问答对</p>
</div>
""", unsafe_allow_html=True)

# 页面功能说明
st.info("""
**📋 功能说明：** 管理高质量问答对，提供快速响应。包含问答对管理、高频问题统计、优质问答对提取等功能。
""")

# 初始化反馈存储
feedback_store = FeedbackStore()

# 加载数据 - 使用较短的TTL确保数据实时性
@st.cache_data(ttl=5)  # 5秒缓存，确保数据相对实时
def load_cached_intent_space():
    return load_intent_space()

@st.cache_data(ttl=5)  # 5秒缓存
def load_frequent_questions():
    return feedback_store.get_frequent_questions(min_count=2, limit=30)

@st.cache_data(ttl=5)  # 5秒缓存
def load_high_quality_qa():
    return feedback_store.get_high_quality_qa_pairs(min_rating=4, limit=50)

# 检查是否需要清除缓存（通过session_state控制）
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = 0

# 加载数据
all_qa_pairs = load_cached_intent_space()
frequent_questions = load_frequent_questions()
high_quality_qa = load_high_quality_qa()

# 侧边栏 - 统计和操作
with st.sidebar:
    # 意图空间统计
    st.markdown("### 📊 意图空间统计")
    total_count = len(all_qa_pairs)
    st.metric("文件中的问答对", total_count)
    st.metric("文件数量", len(set([qa['source_file'] for qa in all_qa_pairs])) if all_qa_pairs else 0)
    
    st.markdown("---")
    
    # 可提取的优质内容统计（来自反馈空间）
    st.markdown("### 💎 可提取的优质内容")
    st.metric("高频问题数", len(frequent_questions), 
              help="从反馈空间中统计出的高频问题，建议添加到意图空间")
    st.metric("优质问答对数", len(high_quality_qa),
              help="从反馈空间中提取的优质问答对（评分≥4分），建议添加到意图空间")
    
    st.markdown("---")
    
    # 操作按钮
    st.markdown("### 🛠️ 操作")
    if st.button("🔄 刷新数据", use_container_width=True):
        # 清除所有缓存
        st.cache_data.clear()
        st.session_state.last_refresh_time = datetime.now().timestamp()
        st.rerun()
    
    # 自动刷新提示
    current_time = time.time()
    if current_time - st.session_state.last_refresh_time > 10:  # 10秒后提示可以刷新
        st.caption("💡 数据每5秒自动更新，或点击刷新按钮立即更新")
    
    st.markdown("---")
    
    # 说明
    st.markdown("### 💡 说明")
    st.info("""
    意图空间用于存储高频问题和高质量答案的问答对。
    
    当用户提问时，系统会从意图空间中检索相似的问题，如果相似度足够高，会直接返回对应的标准答案。
    
    您可以通过编辑 `rag_source/intent_space/` 目录下的文件来管理问答对。
    """)

# 主要内容区域 - 使用标签页
tab1, tab2, tab3 = st.tabs(["📁 文件中的问答对", "🔥 高频问题", "⭐ 优质问答对"])

# 标签1：文件中的问答对
with tab1:
    if not all_qa_pairs:
        st.info("📭 意图空间中暂无问答对数据。请将Q&A格式的文件放入 `rag_source/intent_space/` 目录。")
    else:
        # 搜索功能
        search_query = st.text_input("🔍 搜索问答对", placeholder="输入关键词搜索问题或答案...", help="在问题和答案中搜索关键词")
        
        # 筛选数据
        filtered_qa_pairs = all_qa_pairs
        
        if search_query:
            search_lower = search_query.lower()
            filtered_qa_pairs = [
                qa for qa in filtered_qa_pairs
                if search_lower in qa['question'].lower() or search_lower in qa['answer'].lower()
            ]
        
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总问答对数", len(all_qa_pairs))
        with col2:
            st.metric("当前显示", len(filtered_qa_pairs))
        with col3:
            unique_files = len(set([qa['source_file'] for qa in filtered_qa_pairs]))
            st.metric("涉及文件", unique_files)
        with col4:
            avg_answer_length = sum(len(qa['answer']) for qa in filtered_qa_pairs) / len(filtered_qa_pairs) if filtered_qa_pairs else 0
            st.metric("平均答案长度", f"{avg_answer_length:.0f} 字")
        
        st.markdown("---")
        
        # 表格展示
        st.markdown("### 📋 问答对列表")
        
        if not filtered_qa_pairs:
            st.warning("没有找到匹配的问答对。请调整筛选条件或搜索关键词。")
        else:
            # 准备表格数据
            table_data = []
            for idx, qa in enumerate(filtered_qa_pairs, 1):
                # 截断长文本（用于表格显示，完整内容存储在完整字段中）
                question_short = qa['question'][:100] + "..." if len(qa['question']) > 100 else qa['question']
                answer_short = qa['answer'][:100] + "..." if len(qa['answer']) > 100 else qa['answer']
                
                table_data.append({
                    "序号": idx,
                    "问题": question_short,
                    "答案": answer_short,
                    "来源文件": qa['source_file'],
                    "完整问题": qa['question'],
                    "完整答案": qa['answer']
                })
            
            # 创建DataFrame
            df = pd.DataFrame(table_data)
            
            # 选择要显示的列
            display_columns = ["序号", "问题", "答案", "来源文件"]
            df_display = df[display_columns].copy()
            
            # 为每行添加提示（如果内容被截断）
            for idx, row in df_display.iterrows():
                full_question = df.loc[idx, "完整问题"]
                full_answer = df.loc[idx, "完整答案"]
                
                # 如果内容被截断，添加提示
                if len(full_question) > 100:
                    df_display.at[idx, "问题"] = f"{row['问题']} (点击查看详情)"
                if len(full_answer) > 100:
                    df_display.at[idx, "答案"] = f"{row['答案']} (点击查看详情)"
            
            # 使用st.dataframe展示表格
            selected_rows = st.dataframe(
                df_display,
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "序号": st.column_config.NumberColumn("序号", width="small"),
                    "问题": st.column_config.TextColumn(
                        "问题", 
                        width="large",
                        help="内容较长时请点击下方'详细信息查看'查看完整内容"
                    ),
                    "答案": st.column_config.TextColumn(
                        "答案", 
                        width="large",
                        help="内容较长时请点击下方'详细信息查看'查看完整内容"
                    ),
                    "来源文件": st.column_config.TextColumn("来源文件", width="medium"),
                }
            )
            
            st.markdown("---")
            
            # 详细信息查看区域
            st.markdown("### 🔍 详细信息查看")
            
            # 选择要查看的问答对
            qa_options = [f"{idx+1}. {qa['question'][:50]}..." if len(qa['question']) > 50 else f"{idx+1}. {qa['question']}" 
                         for idx, qa in enumerate(filtered_qa_pairs)]
            
            if qa_options:
                selected_idx = st.selectbox(
                    "选择问答对查看详细信息",
                    range(len(qa_options)),
                    format_func=lambda x: qa_options[x],
                    index=0
                )
                
                selected_qa = filtered_qa_pairs[selected_idx]
                
                # 创建两列布局
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("#### 📝 基本信息")
                    info_data = {
                        "序号": selected_idx + 1,
                        "来源文件": selected_qa['source_file'],
                        "问题长度": f"{len(selected_qa['question'])} 字",
                        "答案长度": f"{len(selected_qa['answer'])} 字"
                    }
                    for key, value in info_data.items():
                        st.markdown(f"**{key}**: {value}")
                
                with col2:
                    st.markdown("#### 📊 统计")
                    st.metric("问题字数", len(selected_qa['question']))
                    st.metric("答案字数", len(selected_qa['answer']))
                
                st.markdown("---")
                
                # 详细内容
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ❓ 问题")
                    st.markdown(f"""
                    <div class='question-box'>
                        {selected_qa['question']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 💡 答案")
                    st.markdown(f"""
                    <div class='answer-box'>
                        {selected_qa['answer']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 文件路径信息
                st.markdown("#### 📁 文件信息")
                config = load_config()
                rag_config = config.get("rag", {})
                intent_space_dir = rag_config.get("intent_space_dir", "./rag_source/intent_space")
                file_path = os.path.join(intent_space_dir, selected_qa['source_file'])
                st.code(file_path, language=None)

# 标签2：高频问题
with tab2:
    st.markdown("### 🔥 高频问题（来自反馈空间）")
    st.info("以下是从反馈空间中统计出的高频问题，这些问题被多次提问，建议添加到意图空间中以提高响应速度。")
    
    if not frequent_questions:
        st.warning("暂无高频问题数据。当反馈空间中有重复的问题时，会在这里显示。")
    else:
        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("高频问题数", len(frequent_questions))
        with col2:
            max_count = max([q['count'] for q in frequent_questions]) if frequent_questions else 0
            st.metric("最高出现次数", max_count)
        with col3:
            ratings = [q['avg_rating'] for q in frequent_questions if q['avg_rating'] is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            st.metric("平均评分", f"{avg_rating:.2f}" if ratings else "无反馈")
        
        st.markdown("---")
        
        # 表格展示
        table_data = []
        for idx, fq in enumerate(frequent_questions, 1):
            question_short = fq['question'][:100] + "..." if len(fq['question']) > 100 else fq['question']
            avg_rating_display = f"{fq['avg_rating']:.2f}" if fq['avg_rating'] is not None else "无反馈"
            table_data.append({
                "序号": idx,
                "问题": question_short,
                "出现次数": fq['count'],
                "反馈次数": fq.get('feedback_count', 0),
                "平均评分": avg_rating_display,
                "最后提问": format_local_time(fq['last_asked'], include_seconds=True),
                "完整问题": fq['question']
            })
        
        df_frequent = pd.DataFrame(table_data)
        display_columns = ["序号", "问题", "出现次数", "反馈次数", "平均评分", "最后提问"]
        df_frequent_display = df_frequent[display_columns].copy()
        
        # 为每行添加提示（如果内容被截断）
        for idx, row in df_frequent_display.iterrows():
            full_question = df_frequent.loc[idx, "完整问题"]
            if len(full_question) > 100:
                df_frequent_display.at[idx, "问题"] = f"{row['问题']} (点击查看详情)"
        
        st.dataframe(
            df_frequent_display,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "序号": st.column_config.NumberColumn("序号", width="small"),
                "问题": st.column_config.TextColumn(
                    "问题", 
                    width="large",
                    help="内容较长时请点击下方'详细信息'查看完整内容"
                ),
                "出现次数": st.column_config.NumberColumn("出现次数", width="small"),
                "反馈次数": st.column_config.NumberColumn("反馈次数", width="small"),
                "平均评分": st.column_config.TextColumn("平均评分", width="small"),
                "最后提问": st.column_config.TextColumn("最后提问", width="medium"),
            }
        )
        
        st.markdown("---")
        
        # 详细信息
        st.markdown("### 🔍 详细信息")
        if frequent_questions:
            selected_fq_idx = st.selectbox(
                "选择高频问题查看详情",
                range(len(frequent_questions)),
                format_func=lambda x: f"{x+1}. {frequent_questions[x]['question'][:50]}..." 
                if len(frequent_questions[x]['question']) > 50 
                else f"{x+1}. {frequent_questions[x]['question']}",
                index=0,
                key="frequent_question_select"
            )
            
            selected_fq = frequent_questions[selected_fq_idx]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📊 统计信息")
                st.metric("出现次数", selected_fq['count'])
                st.metric("反馈次数", selected_fq.get('feedback_count', 0))
                avg_rating_display = f"{selected_fq['avg_rating']:.2f}" if selected_fq['avg_rating'] is not None else "无反馈"
                st.metric("平均评分", avg_rating_display)
            with col2:
                st.markdown("#### 📅 时间信息")
                st.markdown(f"**最后提问时间**: {format_local_time(selected_fq['last_asked'], include_seconds=True)}")
            
            st.markdown("#### ❓ 问题内容")
            st.markdown(f"""
            <div class='question-box'>
                {selected_fq['question']}
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 建议：将此问题添加到意图空间文件中，并提供一个标准答案，以提高系统响应速度。")

# 标签3：优质问答对
with tab3:
    st.markdown("### ⭐ 优质问答对（来自反馈空间）")
    st.info("以下是从反馈空间中提取的优质问答对，这些问答对评分高（≥4分）或有改进建议，建议添加到意图空间中。")
    
    if not high_quality_qa:
        st.warning("暂无优质问答对数据。当反馈空间中有高评分（≥4分）的反馈时，会在这里显示。")
    else:
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("优质问答对数", len(high_quality_qa))
        with col2:
            with_correction = len([qa for qa in high_quality_qa if qa['has_correction']])
            st.metric("有改进建议", with_correction)
        with col3:
            avg_rating = sum([qa['rating'] for qa in high_quality_qa]) / len(high_quality_qa) if high_quality_qa else 0
            st.metric("平均评分", f"{avg_rating:.2f}")
        with col4:
            max_rating = max([qa['rating'] for qa in high_quality_qa]) if high_quality_qa else 0
            st.metric("最高评分", max_rating)
        
        st.markdown("---")
        
        # 筛选选项
        col1, col2 = st.columns(2)
        with col1:
            show_only_correction = st.checkbox("仅显示有改进建议的", value=False)
        with col2:
            min_rating_filter = st.slider("最低评分", min_value=4, max_value=5, value=4)
        
        # 筛选数据
        filtered_high_quality = high_quality_qa
        if show_only_correction:
            filtered_high_quality = [qa for qa in filtered_high_quality if qa['has_correction']]
        filtered_high_quality = [qa for qa in filtered_high_quality if qa['rating'] >= min_rating_filter]
        
        st.markdown(f"显示 {len(filtered_high_quality)} 条优质问答对")
        st.markdown("---")
        
        # 表格展示
        table_data = []
        for idx, qa in enumerate(filtered_high_quality, 1):
            question_short = qa['question'][:100] + "..." if len(qa['question']) > 100 else qa['question']
            answer_short = qa['answer'][:100] + "..." if len(qa['answer']) > 100 else qa['answer']
            correction_indicator = "✅" if qa['has_correction'] else ""
            
            table_data.append({
                "序号": idx,
                "问题": question_short,
                "答案": answer_short,
                "评分": qa['rating'],
                "改进": correction_indicator,
                "时间": format_local_time(qa['created_at'], include_seconds=True),
                "完整问题": qa['question'],
                "完整答案": qa['answer'],
                "原始答案": qa.get('original_answer', ''),
                "改进建议": qa.get('correction', ''),
                "反馈ID": qa['id']
            })
        
        df_quality = pd.DataFrame(table_data)
        display_columns = ["序号", "问题", "答案", "评分", "改进", "时间"]
        df_quality_display = df_quality[display_columns].copy()
        
        # 为每行添加提示（如果内容被截断）
        for idx, row in df_quality_display.iterrows():
            full_question = df_quality.loc[idx, "完整问题"]
            full_answer = df_quality.loc[idx, "完整答案"]
            
            # 如果内容被截断，添加提示
            if len(full_question) > 100:
                df_quality_display.at[idx, "问题"] = f"{row['问题']} (点击查看详情)"
            if len(full_answer) > 100:
                df_quality_display.at[idx, "答案"] = f"{row['答案']} (点击查看详情)"
        
        st.dataframe(
            df_quality_display,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "序号": st.column_config.NumberColumn("序号", width="small"),
                "问题": st.column_config.TextColumn(
                    "问题", 
                    width="large",
                    help="内容较长时请点击下方'详细信息'查看完整内容"
                ),
                "答案": st.column_config.TextColumn(
                    "答案", 
                    width="large",
                    help="内容较长时请点击下方'详细信息'查看完整内容"
                ),
                "评分": st.column_config.NumberColumn("评分", width="small"),
                "改进": st.column_config.TextColumn("改进", width="small"),
                "时间": st.column_config.TextColumn("时间", width="medium"),
            }
        )
        
        st.markdown("---")
        
        # 详细信息
        st.markdown("### 🔍 详细信息")
        if filtered_high_quality:
            selected_qa_idx = st.selectbox(
                "选择优质问答对查看详情",
                range(len(filtered_high_quality)),
                format_func=lambda x: f"{x+1}. {filtered_high_quality[x]['question'][:50]}..." 
                if len(filtered_high_quality[x]['question']) > 50 
                else f"{x+1}. {filtered_high_quality[x]['question']}",
                index=0,
                key="quality_qa_select"
            )
            
            selected_qa = filtered_high_quality[selected_qa_idx]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("#### 📝 基本信息")
                info_data = {
                    "反馈ID": selected_qa['id'],
                    "评分": f"{selected_qa['rating']}/5",
                    "有改进建议": "是" if selected_qa['has_correction'] else "否",
                    "时间": format_local_time(selected_qa['created_at'], include_seconds=True)
                }
                for key, value in info_data.items():
                    st.markdown(f"**{key}**: {value}")
            with col2:
                st.markdown("#### 📊 统计")
                st.metric("评分", selected_qa['rating'])
            
            st.markdown("---")
            
            # 问题和答案
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ❓ 问题")
                st.markdown(f"""
                <div class='question-box'>
                    {selected_qa['question']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💡 答案")
                st.markdown(f"""
                <div class='answer-box'>
                    {selected_qa['answer']}
                </div>
                """, unsafe_allow_html=True)
            
            # 如果有改进建议，显示原始答案和改进建议
            if selected_qa['has_correction']:
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 📝 原始答案")
                    st.markdown(f"""
                    <div style='background: #fff3e0; padding: 1rem; border-radius: 8px; border-left: 4px solid #FF9800;'>
                        {selected_qa.get('original_answer', '')}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("#### ✏️ 改进建议")
                    st.markdown(f"""
                    <div style='background: #e1f5fe; padding: 1rem; border-radius: 8px; border-left: 4px solid #03A9F4;'>
                        {selected_qa.get('correction', '')}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.info("💡 建议：将此优质问答对添加到意图空间文件中，以提高系统回答质量。")

