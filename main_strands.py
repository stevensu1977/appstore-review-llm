import streamlit as st
import sys
from app_reviews_strands import analyze_app_reviews

st.set_page_config(
    page_title="App Store Review Analysis",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("App Store Review Analysis")

# 侧边栏选项
with st.sidebar:
    st.header("Configuration")
    
    # 商店选择
    store_options = ["Google Play", "Apple", "Steam"]
    selected_store_option = st.selectbox("Select Store", store_options)
    
    # 应用名称输入
    app_name = st.text_input("App Name", "Genshin Impact")
    
    # 国家选择
    country_options = ["us", "cn", "jp", "kr", "gb", "de", "fr"]
    selected_country_option = st.selectbox("Select Country", country_options)
    
    # 评分过滤
    rank_options = [("All", -1), ("1 Star", 1), ("2 Stars", 2), ("3 Stars", 3), ("4 Stars", 4), ("5 Stars", 5)]
    selected_rank_label, selected_rank_option = st.selectbox(
        "Filter by Rank",
        rank_options,
        format_func=lambda x: x[0]
    )
    
    # 分析按钮
    analyze_button = st.button("Analyze Reviews")

# 主界面
if analyze_button:
    with st.spinner("Analyzing app reviews... This may take a few minutes."):
        try:
            # 使用Strands Agents分析应用评论
            app_id, result = analyze_app_reviews(
                selected_store_option,
                app_name,
                selected_country_option,
                selected_rank_option
            )
            
            # 显示结果
            st.markdown(result)
            
            # 保存结果到文件
            with open(f"output/{app_id}_analysis.md", "w", encoding="utf-8") as f:
                f.write(result)
            
            st.success(f"Analysis saved to output/{app_id}_analysis.md")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
else:
    st.info("Configure the options and click 'Analyze Reviews' to start.")