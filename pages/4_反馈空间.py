"""
反馈空间页面
显示和管理用户反馈数据
"""
import streamlit as st
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 将项目根目录添加到Python路径中
from src.utils import setup_project_path, format_local_time
setup_project_path()

from src.feedback import FeedbackStore

# --- 页面配置 ---
st.set_page_config(
    page_title="反馈空间 - AI RAG Pro",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    /* 卡片容器样式 */
    .feedback-table-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .feedback-table-container:hover {
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    }
    
    /* 指标卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }
    
    /* 评分样式 */
    .positive-rating {
        color: #10b981;
        font-weight: 600;
        font-size: 1.1em;
    }
    
    .negative-rating {
        color: #ef4444;
        font-weight: 600;
        font-size: 1.1em;
    }
    
    /* 文本截断样式 */
    .question-text {
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .answer-text {
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
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
    
    /* 标题样式 */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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
    
    /* 统计指标样式 */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* 选择框样式 */
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
</style>
""", unsafe_allow_html=True)

# 初始化反馈存储
feedback_store = FeedbackStore()

# 页面标题
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='margin: 0; color: #2c3e50; font-size: 2.5rem;'>💬 反馈空间</h1>
    <p style='margin: 0.5rem 0 0 0; color: #5a6c7d; font-size: 1.1rem;'>查看和管理用户反馈数据</p>
</div>
""", unsafe_allow_html=True)

# 页面功能说明
st.info("""
**📋 功能说明：** 收集和管理用户反馈数据，支持按评分筛选、查看详细信息，通过数据分析持续优化系统回答质量。
""")

# 侧边栏 - 筛选和统计
with st.sidebar:
    st.markdown("### 🔍 筛选条件")
    
    # 评分筛选 - 更新为支持0-5分筛选
    rating_filter = st.selectbox(
        "评分筛选",
        ["全部", "5分 ⭐⭐⭐⭐⭐", "4分 ⭐⭐⭐⭐", "3分 ⭐⭐⭐", "2分 ⭐⭐", "1分 ⭐", "0分 ⚪", "无反馈"],
        index=0
    )
    
    # 转换筛选条件
    rating_value = None
    if rating_filter == "5分 ⭐⭐⭐⭐⭐":
        rating_value = 5
    elif rating_filter == "4分 ⭐⭐⭐⭐":
        rating_value = 4
    elif rating_filter == "3分 ⭐⭐⭐":
        rating_value = 3
    elif rating_filter == "2分 ⭐⭐":
        rating_value = 2
    elif rating_filter == "1分 ⭐":
        rating_value = 1
    elif rating_filter == "0分 ⚪":
        rating_value = 0
    # "无反馈" 和 "全部" 保持 rating_value = None
    
    st.markdown("---")
    
    # 统计信息
    st.markdown("### 📊 统计信息")
    total_count = feedback_store.get_feedback_count()
    high_rating_count = feedback_store.get_feedback_count(rating_filter=5) + feedback_store.get_feedback_count(rating_filter=4)
    low_rating_count = feedback_store.get_feedback_count(rating_filter=0) + feedback_store.get_feedback_count(rating_filter=1) + feedback_store.get_feedback_count(rating_filter=2)
    no_feedback_count = feedback_store.get_feedback_count(rating_filter=-1)
    
    st.metric("总记录数", total_count)
    if total_count > 0:
        st.metric("高评分(4-5分)", high_rating_count, delta=f"{high_rating_count/total_count*100:.1f}%")
        st.metric("低评分(0-2分)", low_rating_count, delta=f"{low_rating_count/total_count*100:.1f}%")
        st.metric("无反馈", no_feedback_count, delta=f"{no_feedback_count/total_count*100:.1f}%")
    else:
        st.metric("高评分(4-5分)", high_rating_count)
        st.metric("低评分(0-2分)", low_rating_count)
        st.metric("无反馈", no_feedback_count)
    
    st.markdown("---")
    
    # 操作按钮
    st.markdown("### 🛠️ 操作")
    if st.button("🔄 刷新数据", use_container_width=True):
        # 清除缓存
        st.cache_data.clear()
        st.rerun()
    
    # 自动刷新提示
    st.caption("💡 数据每3秒自动更新，或点击刷新按钮立即更新")
    
    if st.button("📥 导出数据", use_container_width=True):
        # 导出功能
        all_feedback = feedback_store.get_all_feedback(rating_filter=rating_value)
        if all_feedback:
            feedback_json = json.dumps(all_feedback, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                "下载JSON",
                data=feedback_json,
                file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# 主要内容区域
# 获取所有反馈数据（不分页，用于表格展示）
# 使用缓存但设置较短的TTL确保数据实时性
@st.cache_data(ttl=3)  # 3秒缓存，确保反馈数据实时更新
def load_feedback_data(rating_filter_value, filter_type):
    if filter_type == "无反馈":
        # 表格中不显示无反馈的数据，返回空列表
        return []
    else:
        # 只返回有反馈的数据（rating不为None）
        all_fb = feedback_store.get_all_feedback(rating_filter=rating_filter_value)
        return [fb for fb in all_fb if fb["rating"] is not None]

all_feedbacks = load_feedback_data(rating_value, rating_filter)

if not all_feedbacks:
    st.info("📭 暂无反馈数据")
else:
    # 准备表格数据
    table_data = []
    for fb in all_feedbacks:
        # 格式化评分 - 显示分数和星星
        rating_value = fb["rating"]
        if rating_value is None:
            rating_display = "无反馈"
        elif rating_value == 0:
            rating_display = "⚪ 0分"
        else:
            stars = "⭐" * rating_value
            rating_display = f"{stars} {rating_value}分"
        
        # 截断长文本（用于表格显示，完整内容存储在完整字段中）
        question_short = fb["question"][:80] + "..." if len(fb["question"]) > 80 else fb["question"]
        answer_short = fb["answer"][:80] + "..." if len(fb["answer"]) > 80 else fb["answer"]
        correction_short = ""
        if fb.get("correction") and len(fb["correction"].strip()) > 0:
            correction_short = fb["correction"][:50] + "..." if len(fb["correction"]) > 50 else fb["correction"]
        
        # 格式化时间（处理UTC时间和本地时间）
        time_display = format_local_time(fb["created_at"], include_seconds=True)
        
        table_data.append({
            "ID": fb["id"],
            "评分": rating_display,
            "用户问题": question_short,
            "助手回答": answer_short,
            "改进建议": correction_short if correction_short else "无",
            "时间": time_display,
            "完整问题": fb["question"],
            "完整回答": fb["answer"],
            "完整建议": fb.get("correction", ""),
            "来源": fb.get("sources", ""),
            "rating_value": fb["rating"]
        })
    
    # 创建DataFrame
    df = pd.DataFrame(table_data)
    
    # 显示统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总记录数", len(df))
    with col2:
        # 高评分（4-5分）
        high_rating_df = df[df["rating_value"].isin([4, 5])]
        st.metric("高评分(4-5分)", len(high_rating_df), delta=f"{len(high_rating_df)/len(df)*100:.1f}%" if len(df) > 0 else "0%")
    with col3:
        # 低评分（0-2分）
        low_rating_df = df[df["rating_value"].isin([0, 1, 2])]
        st.metric("低评分(0-2分)", len(low_rating_df), delta=f"{len(low_rating_df)/len(df)*100:.1f}%" if len(df) > 0 else "0%")
    with col4:
        has_correction = df[df["完整建议"].str.strip() != ""]
        st.metric("有改进建议", len(has_correction))
    
    st.markdown("---")
    
    # 表格展示区域
    st.markdown("### 📋 反馈数据表格")
    
    # 选择要显示的列（排除内部使用的列，时间放在第一列）
    display_columns = ["时间", "评分", "用户问题", "助手回答", "改进建议"]
    df_display = df[display_columns].copy()
    
    # 使用st.dataframe展示表格，支持排序和选择
    # 为每行添加tooltip显示完整内容
    for idx, row in df_display.iterrows():
        full_question = df.loc[idx, "完整问题"]
        full_answer = df.loc[idx, "完整回答"]
        full_correction = df.loc[idx, "完整建议"]
        
        # 如果内容被截断，添加tooltip提示
        if len(full_question) > 80:
            df_display.at[idx, "用户问题"] = f"{row['用户问题']} (点击查看详情)"
        if len(full_answer) > 80:
            df_display.at[idx, "助手回答"] = f"{row['助手回答']} (点击查看详情)"
        if full_correction and full_correction != "无" and len(full_correction) > 50:
            df_display.at[idx, "改进建议"] = f"{row['改进建议']} (点击查看详情)"
    
    selected_rows = st.dataframe(
        df_display,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "时间": st.column_config.TextColumn("时间", width="medium"),
            "评分": st.column_config.TextColumn("评分", width="medium"),
            "用户问题": st.column_config.TextColumn(
                "用户问题", 
                width="large",
                help="内容较长时请点击下方'详细信息查看'查看完整内容"
            ),
            "助手回答": st.column_config.TextColumn(
                "助手回答", 
                width="large",
                help="内容较长时请点击下方'详细信息查看'查看完整内容"
            ),
            "改进建议": st.column_config.TextColumn(
                "改进建议", 
                width="medium",
                help="内容较长时请点击下方'详细信息查看'查看完整内容"
            )
        }
    )
    
    st.markdown("---")
    
    # 详细信息查看区域
    st.markdown("### 🔍 详细信息查看")
    
    # 选择要查看的反馈ID
    feedback_ids = df["ID"].tolist()
    selected_id = st.selectbox(
        "选择反馈ID查看详细信息",
        feedback_ids,
        index=0 if feedback_ids else None
    )
    
    if selected_id:
        selected_feedback = next((fb for fb in all_feedbacks if fb["id"] == selected_id), None)
        
        if selected_feedback:
            # 创建两列布局
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📝 基本信息")
                rating_value_detail = selected_feedback["rating"]
                if rating_value_detail is None:
                    rating_display_detail = "无反馈"
                elif rating_value_detail == 0:
                    rating_display_detail = "⚪ 0分"
                else:
                    stars_detail = "⭐" * rating_value_detail
                    rating_display_detail = f"{stars_detail} {rating_value_detail}分"
                
                info_data = {
                    "反馈ID": selected_feedback["id"],
                    "评分": rating_display_detail,
                    "提交时间": format_local_time(selected_feedback["created_at"], include_seconds=True)
                }
                for key, value in info_data.items():
                    st.markdown(f"**{key}**: {value}")
            
            with col2:
                st.markdown("#### 🗑️ 操作")
                if st.button("删除此反馈", key=f"delete_detail_{selected_id}", type="primary", use_container_width=True):
                    if feedback_store.delete_feedback(selected_id):
                        st.success("✅ 反馈已删除")
                        st.rerun()
                    else:
                        st.error("❌ 删除失败")
            
            st.markdown("---")
            
            # 详细内容
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ❓ 用户问题")
                st.markdown(f"""
                <div class='question-box'>
                    {selected_feedback['question']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🤖 助手回答")
                st.markdown(f"""
                <div class='answer-box'>
                    {selected_feedback['answer']}
                </div>
                """, unsafe_allow_html=True)
            
            # 改进建议
            if selected_feedback.get("correction") and len(selected_feedback["correction"].strip()) > 0:
                st.markdown("#### ✏️ 改进建议")
                st.markdown(f"""
                <div class='correction-box'>
                    {selected_feedback['correction']}
                </div>
                """, unsafe_allow_html=True)
            
            # 来源信息
            if selected_feedback.get("sources") and len(selected_feedback["sources"].strip()) > 0:
                st.markdown("#### 📚 来源信息")
                try:
                    sources_data = json.loads(selected_feedback["sources"])
                    if sources_data:
                        st.json(sources_data)
                except (json.JSONDecodeError, TypeError, ValueError):
                    st.text(selected_feedback["sources"])
