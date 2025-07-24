import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="SEO Dashboard", layout="wide")

st.title("SEO 數據儀表板")

uploaded_file = st.file_uploader("請上傳你的關鍵字數據檔案 (.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("成功載入數據！")

    # --- 區塊 1: 數據現況 ---
    st.header("📊 數據現況")
    st.write("顯示數據摘要、欄位說明、行數與基本統計。")
    st.dataframe(df.head())
    st.write(df.describe())

    # --- 區塊 2: 數據解讀 ---
    st.header("🔍 數據解讀")
    st.write("繪製 CTR、Impressions、Position 等指標的分布與關聯。")

    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x="Impressions", y="CTR", ax=ax)
    st.pyplot(fig)

    # 可加其他圖表例如 CTR vs Position 等

    # --- 區塊 3: 排序行動 ---
    st.header("🚀 排序行動建議")
    st.write("根據分析，提供優化建議。")

    avg_ctr = df["CTR"].mean()
    underperforming = df[df["CTR"] < avg_ctr]
    st.write(f"🔻 CTR 低於平均 ({avg_ctr:.2f}) 的關鍵字：", underperforming[['Keyword', 'CTR', 'Position']].head(5))

else:
    st.warning("請先上傳 CSV 數據檔案以開始分析。")
