"""
反馈空间页面
显示和管理用户反馈数据
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.utils import setup_project_path, format_local_time

# 设置项目路径
setup_project_path()

from src.feedback import FeedbackStore
from 首页 import load_rag_manager, get_rag_manager_cache_key

# --- 页面配置 ---
st.set_page_config(
    page_title="反馈空间管理",
    page_icon="📝",
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
    
    /* General Button Style */
    .stButton > button {
        border-radius: 12px;
        font-weight: 500;
    }
    
    /* Sidebar Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Info Box Style */
    .stInfo {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
    }
    
    /* Data Editor (DataFrame) Style */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Metric Style */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown("""
<div style='text-align: left; margin-bottom: 2rem;'>
    <h1 style='margin: 0; color: #2c3e50; font-size: 2.5rem;'>📝 反馈空间</h1>
    <p style='margin: 0.5rem 0 0 0; color: #5a6c7d; font-size: 1.1rem;'>查看和管理用户反馈数据</p>
</div>
""", unsafe_allow_html=True)
st.info("""📋
在这里，您可以审查、分析和管理所有用户的反馈数据。反馈空间是系统自我学习和进化的关键。
- **分析**：通过统计图表洞察反馈数据的分布和趋势。
- **筛选**：使用多种条件精确查找您关心的反馈。
- **操作**：编辑反馈内容，并将优质问答对一键添加到意图空间。
""")

# --- 初始化 ---
feedback_store = FeedbackStore()

# --- 缓存函数 ---
@st.cache_data(ttl=300) # 缓存5分钟
def get_all_feedback_data():
    """加载所有反馈数据并转换为 DataFrame"""
    records = feedback_store.get_all_interactions()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    # 数据清洗和预处理
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(-1).astype(int)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['formatted_time'] = df['created_at'].apply(lambda x: format_local_time(x.isoformat()))
    return df

# --- 加载数据 ---
df_feedback = get_all_feedback_data()

# --- 主体内容 ---
if df_feedback.empty:
    st.info("📬 当前反馈空间为空，暂无用户反馈。")
else:
    # --- Sidebar for Stats ---
    with st.sidebar:
        st.header("📊 统计概览")
        
        total_feedback = len(df_feedback)
        rated_feedback = df_feedback[df_feedback['rating'] != -1]
        total_rated = len(rated_feedback)
        avg_rating = rated_feedback['rating'].mean() if total_rated > 0 else 0
        helpful_count = len(rated_feedback[rated_feedback['rating'] >= 4])
        helpful_rate = (helpful_count / total_rated) * 100 if total_rated > 0 else 0

        st.metric("反馈总数", f"{total_feedback} 条")
        st.metric("已评价数", f"{total_rated} 条")
        st.metric("平均评分", f"{avg_rating:.2f} ⭐")
        st.metric("有帮助占比", f"{helpful_rate:.1f}%")

    # --- Control Panel on Main Page ---
    # st.header("⚙️ 控制面板")
    with st.container():
        # Visualizations remain on the main page
        st.markdown("#### 📈 可视化分析")
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            st.markdown("###### 评分分布")
            if not rated_feedback.empty:
                # 构建评分统计数据
                rating_counts = rated_feedback['rating'].value_counts().to_dict()
                
                # 创建完整的评分列表（0-5）和对应的计数
                x_values = [0, 1, 2, 3, 4, 5]
                y_values = [rating_counts.get(i, 0) for i in x_values]
                
                # 使用 graph_objects 创建柱状图
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=x_values,
                        y=y_values,
                        text=y_values,
                        textposition='outside',
                        marker_color='rgb(102, 126, 234)',
                        hovertemplate='评分: %{x}<br>数量: %{y}<extra></extra>'
                    )
                ])
                
                # 更新布局
                max_count = max(y_values) if y_values else 1
                fig_bar.update_layout(
                    xaxis=dict(
                        title="评分 (0-5)",
                        tickmode='linear',
                        tick0=0,
                        dtick=1,
                        range=[-0.5, 5.5]
                    ),
                    yaxis=dict(
                        title="数量",
                        range=[0, max_count * 1.2]
                    ),
                    height=300,
                    margin=dict(t=20, b=40, l=40, r=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.caption("暂无有效评分数据")
        
        with viz_col2:
            st.markdown("###### 问题类型分布 (Top 5)")
            # [Corrected Logic] Use the filtered 'rated_feedback' DataFrame for tag analysis
            rated_feedback['tags'] = rated_feedback['sources'].apply(lambda x: eval(x).get('tags', []) if isinstance(x, str) and x.startswith('{') else [])
            all_tags = rated_feedback.explode('tags')['tags'].dropna()
            tag_counts = all_tags.value_counts().nlargest(5)
            if not tag_counts.empty:
                fig_pie = px.pie(tag_counts, names=tag_counts.index, values=tag_counts.values, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_traces(textinfo='percent+label', textposition='inside')
                fig_pie.update_layout(
                    showlegend=False, 
                    height=300, 
                    margin=dict(t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.caption("暂无问题标签数据")

    # --- 数据筛选 ---
    st.markdown("---")
    st.markdown("#### 🔍 筛选条件")
    
    # 筛选器
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        search_query = st.text_input("关键词搜索 (问题/回答)", placeholder="输入关键词...")
    with filter_col2:
        rating_range = st.slider("评分范围", min_value=-1, max_value=5, value=(-1, 5), help="包含-1表示未评分")
    with filter_col3:
        # 获取所有标签
        all_tags_list = sorted(list(all_tags.unique()))
        selected_tags = st.multiselect("问题类型标签", options=all_tags_list)

    # 应用筛选
    df_filtered = df_feedback.copy()
    # 为筛选准备tags列
    df_filtered['tags'] = df_filtered['sources'].apply(lambda x: eval(x).get('tags', []) if isinstance(x, str) and x.startswith('{') else [])
    
    if search_query:
        df_filtered = df_filtered[
            df_filtered['question'].str.contains(search_query, case=False, na=False) |
            df_filtered['answer'].str.contains(search_query, case=False, na=False)
        ]
    if rating_range:
        df_filtered = df_filtered[
            (df_filtered['rating'] >= rating_range[0]) & (df_filtered['rating'] <= rating_range[1])
        ]
    if selected_tags:
        df_filtered = df_filtered[df_filtered['tags'].apply(lambda x: any(tag in x for tag in selected_tags))]

    st.markdown("---")
    
    # --- 反馈列表展示 ---
    st.markdown(f"#### 📋 反馈列表 ({len(df_filtered)} 条)")
    
    if df_filtered.empty:
        st.info("没有符合条件的反馈数据")
    else:
        # 整体可折叠的expander
        with st.expander(f"查看全部 {len(df_filtered)} 条反馈", expanded=True):
            for idx, row in df_filtered.iterrows():
                # 评分显示和颜色
                if row['rating'] == -1:
                    rating_display = "未评分"
                    rating_stars = "⚪"
                    rating_color = "#9ca3af"
                else:
                    rating_stars = "⭐" * row['rating'] + "☆" * (5 - row['rating'])
                    rating_display = f"{row['rating']} 分"
                    if row['rating'] >= 4:
                        rating_color = "#10b981"  # 绿色
                    elif row['rating'] >= 3:
                        rating_color = "#f59e0b"  # 橙色
                    else:
                        rating_color = "#ef4444"  # 红色
                
                # 标签显示
                tags_html = ""
                if row['tags']:
                    tags_html = " ".join([f'<span style="background-color: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; margin-right: 4px;">🏷️ {tag}</span>' for tag in row['tags']])
                
                # 卡片容器
                with st.container():
                    # 卡片头部（始终显示）
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        # 构建头部HTML
                        header_html = f'<div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-left: 5px solid {rating_color}; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
                        header_html += f'<div style="display: flex; justify-content: space-between; align-items: center;"><div><span style="font-size: 1.1rem; color: {rating_color}; font-weight: 600;">{rating_stars}</span><span style="margin-left: 8px; color: {rating_color}; font-weight: 500;">{rating_display}</span></div><span style="color: #6b7280; font-size: 0.875rem;">🕐 {row["formatted_time"]}</span></div>'
                        if tags_html:
                            header_html += f'<div style="margin-top: 8px;">{tags_html}</div>'
                        header_html += f'<div style="margin-top: 8px; color: #6b7280; font-size: 0.9rem;">问题: {row["question"][:60]}{"..." if len(row["question"]) > 60 else ""}</div>'
                        header_html += '</div>'
                        st.markdown(header_html, unsafe_allow_html=True)
                    
                    with col2:
                        # 展开/折叠按钮
                        if st.button("📖 展开" if st.session_state.get(f'feedback_expand_{row["id"]}') != True else "📕 收起", 
                                    key=f"toggle_{row['id']}", 
                                    use_container_width=True):
                            current_state = st.session_state.get(f'feedback_expand_{row["id"]}', False)
                            st.session_state[f'feedback_expand_{row["id"]}'] = not current_state
                            st.rerun()
                    
                    # 详细内容（可折叠）
                    if st.session_state.get(f'feedback_expand_{row["id"]}', False):
                        st.markdown("---")
                        
                        # 问题完整内容
                        st.markdown("**❓ 问题**")
                        st.info(row['question'])
                        
                        # 回答完整内容
                        st.markdown("**💬 回答**")
                        st.success(row['answer'])
                        
                        # 修正建议（如果有）
                        if row['correction'] and str(row['correction']).strip():
                            st.markdown("**✏️ 修正建议**")
                            st.warning(row['correction'])
                        
                        # 来源信息
                        if row['sources'] and str(row['sources']).strip():
                            try:
                                sources_dict = eval(row['sources']) if isinstance(row['sources'], str) else row['sources']
                                if isinstance(sources_dict, dict) and sources_dict.get('docs'):
                                    st.markdown("**📚 参考来源**")
                                    for doc_name in sources_dict['docs']:
                                        st.caption(f"• {doc_name}")
                            except:
                                pass
                        
                        st.caption(f"ID: {row['id']}")
                        st.markdown("---")
