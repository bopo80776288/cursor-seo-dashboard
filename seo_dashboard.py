import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="SEO Dashboard", layout="wide")

st.title("SEO 數據儀表板")

def clean_dataframe(df):
    # Remove all-empty rows
    df = df.dropna(how='all', axis=0)
    # Remove all-empty columns
    df = df.dropna(how='all', axis=1)
    # Reset index after dropping rows
    df = df.reset_index(drop=True)
    return df

uploaded_file = st.file_uploader("請上傳你的關鍵字數據檔案 (.csv)", type=["csv"])

if uploaded_file:
    # Read without assuming header
    df_raw = pd.read_csv(uploaded_file, header=None)
    df_clean = clean_dataframe(df_raw)

    # Try to detect header row (first non-empty row)
    header_row_idx = df_clean.apply(lambda row: row.notnull().sum(), axis=1).idxmax()
    df_clean.columns = df_clean.iloc[header_row_idx]
    df_clean = df_clean.drop(index=range(0, header_row_idx+1)).reset_index(drop=True)

    # Remove all-empty columns again (in case header row had blanks)
    df_clean = df_clean.dropna(how='all', axis=1)

    # Keep only the specified columns
    keep_cols = ["Keyword", "Impressions", "Clicks", "CTR", "Position"]
    df_clean = df_clean[[col for col in keep_cols if col in df_clean.columns]]

    # Clean the CTR column: remove % and convert to float
    if "CTR" in df_clean.columns:
        df_clean["CTR"] = (
            df_clean["CTR"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df_clean["CTR"] = pd.to_numeric(df_clean["CTR"], errors="coerce")

    # Try to convert columns to numeric where possible
    for col in df_clean.columns:
        if col != "Keyword":
            df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')

    st.success("成功載入數據並自動清理空白行與欄！")
    st.info(f"清理後數據行數: {df_clean.shape[0]}，欄位數: {df_clean.shape[1]}")

    # --- 區塊 1: 數據現況 (Data Overview) ---
    st.header("📊 數據現況")
    st.write("顯示數據摘要、欄位說明、行數與基本統計。")

    # KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("關鍵字數量", int(df_clean.shape[0]))
    with kpi2:
        st.metric("總曝光 (Impressions)", int(df_clean["Impressions"].sum()) if "Impressions" in df_clean.columns else "-")
    with kpi3:
        st.metric("總點擊 (Clicks)", int(df_clean["Clicks"].sum()) if "Clicks" in df_clean.columns else "-")
    with kpi4:
        st.metric("平均CTR", f"{df_clean['CTR'].mean():.2f}%" if "CTR" in df_clean.columns and not df_clean['CTR'].isnull().all() else "-")
    with kpi5:
        st.metric("平均排名 (Position)", f"{df_clean['Position'].mean():.1f}" if "Position" in df_clean.columns and not df_clean['Position'].isnull().all() else "-")

    # Top 5 Keywords Table
    st.subheader("Top 5 關鍵字 (依點擊排序)")
    if all(col in df_clean.columns for col in ["Keyword", "Clicks"]):
        st.dataframe(df_clean.sort_values("Clicks", ascending=False)[["Keyword", "Impressions", "Clicks", "CTR", "Position"]].head(5))
    else:
        st.info("缺少 'Keyword' 或 'Clicks' 欄位，無法顯示 Top 5 關鍵字。")

    # --- 區塊 2: 數據解讀 (Data Analysis) ---
    st.header("🔍 數據解讀")
    st.write("深入分析各項SEO指標的分布與關聯，協助發現優化機會。")

    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader("CTR 分布 (Histogram)")
        if "CTR" in df_clean.columns:
            fig1, ax1 = plt.subplots()
            sns.histplot(df_clean["CTR"].dropna(), bins=20, ax=ax1)
            ax1.set_xlabel("CTR (%)")
            st.pyplot(fig1)
        else:
            st.info("缺少 'CTR' 欄位。")
    with chart2:
        st.subheader("排名分布 (Histogram)")
        if "Position" in df_clean.columns:
            fig2, ax2 = plt.subplots()
            sns.histplot(df_clean["Position"].dropna(), bins=20, ax=ax2)
            ax2.set_xlabel("Position")
            st.pyplot(fig2)
        else:
            st.info("缺少 'Position' 欄位。")

    chart3, chart4 = st.columns(2)
    with chart3:
        st.subheader("點擊 vs 曝光 (Scatter)")
        if all(col in df_clean.columns for col in ["Impressions", "Clicks"]):
            fig3, ax3 = plt.subplots()
            sns.scatterplot(data=df_clean, x="Impressions", y="Clicks", ax=ax3)
            ax3.set_xlabel("Impressions")
            ax3.set_ylabel("Clicks")
            st.pyplot(fig3)
        else:
            st.info("缺少 'Impressions' 或 'Clicks' 欄位。")
    with chart4:
        st.subheader("CTR vs 排名 (Scatter)")
        if all(col in df_clean.columns for col in ["Position", "CTR"]):
            fig4, ax4 = plt.subplots()
            sns.scatterplot(data=df_clean, x="Position", y="CTR", ax=ax4)
            ax4.set_xlabel("Position")
            ax4.set_ylabel("CTR (%)")
            st.pyplot(fig4)
        else:
            st.info("缺少 'Position' 或 'CTR' 欄位。")

    # Outlier Highlights
    st.subheader("潛力關鍵字 (高曝光低CTR)")
    if all(col in df_clean.columns for col in ["Keyword", "Impressions", "CTR"]):
        avg_ctr = df_clean["CTR"].mean()
        high_impr = df_clean["Impressions"] > df_clean["Impressions"].median()
        low_ctr = df_clean["CTR"] < avg_ctr
        potential = df_clean[high_impr & low_ctr].sort_values("Impressions", ascending=False)
        st.dataframe(potential[["Keyword", "Impressions", "CTR", "Position"]].head(5))
    else:
        st.info("缺少 'Keyword', 'Impressions' 或 'CTR' 欄位。")

    # --- 區塊 3: 排序行動 (Actionable Recommendations) ---
    st.header("🚀 排序行動建議")
    st.write("根據分析，提供具體優化建議，協助提升SEO表現。")

    # 1. 高曝光、低 CTR (曝光 > 5000 且 CTR < 5%)
    st.subheader("優化建議：高曝光、低CTR (曝光 > 5000 且 CTR < 5%)")
    if all(col in df_clean.columns for col in ["Keyword", "Impressions", "CTR"]):
        mask = (df_clean["Impressions"] > 5000) & (df_clean["CTR"] < 5)
        table1 = df_clean[mask].sort_values(["Impressions", "CTR"], ascending=[False, True])
        st.dataframe(table1[["Keyword", "Impressions", "Clicks", "CTR", "Position"]].head(10))
    else:
        st.info("缺少 'Keyword', 'Impressions' 或 'CTR' 欄位。")

    # 2. 曝光不錯但排名後段（曝光 > 1000 且排名 > 40)
    st.subheader("優化建議：曝光不錯但排名後段 (曝光 > 1000 且 排名 > 40)")
    if all(col in df_clean.columns for col in ["Keyword", "Impressions", "Position"]):
        mask = (df_clean["Impressions"] > 1000) & (df_clean["Position"] > 40)
        table2 = df_clean[mask].sort_values(["Impressions", "Position"], ascending=[False, True])
        st.dataframe(table2[["Keyword", "Impressions", "Clicks", "CTR", "Position"]].head(10))
    else:
        st.info("缺少 'Keyword', 'Impressions' 或 'Position' 欄位。")

    # Content Guidance for selected keyword
    st.subheader("內容建議 (針對單一關鍵字)")
    if "Keyword" in df_clean.columns:
        selected_keyword = st.selectbox("選擇關鍵字以獲得建議：", df_clean["Keyword"].dropna().unique())
        kw_row = df_clean[df_clean["Keyword"] == selected_keyword]
        if not kw_row.empty:
            st.write(f"**關鍵字：** {selected_keyword}")
            if "Impressions" in kw_row.columns:
                st.write(f"- 曝光：{int(kw_row['Impressions'].values[0])}")
            if "Clicks" in kw_row.columns:
                st.write(f"- 點擊：{int(kw_row['Clicks'].values[0])}")
            if "CTR" in kw_row.columns:
                st.write(f"- CTR：{kw_row['CTR'].values[0]:.2f}%")
            if "Position" in kw_row.columns:
                st.write(f"- 排名：{kw_row['Position'].values[0]:.1f}")
            # Actionable suggestions
            suggestions = []
            if "CTR" in kw_row.columns and "Impressions" in kw_row.columns:
                if kw_row["CTR"].values[0] < df_clean["CTR"].mean():
                    suggestions.append("CTR 低於平均，建議優化標題與描述，提升吸引力。")
            if "Position" in kw_row.columns:
                if kw_row["Position"].values[0] > 10:
                    suggestions.append("排名在第2頁以後，建議加強內容深度與內部連結。")
                else:
                    suggestions.append("排名已在第1頁，可持續優化內容與外部連結。")
            if suggestions:
                st.write("**建議：**")
                for s in suggestions:
                    st.write(f"- {s}")
            else:
                st.write("- 無特別建議，請持續追蹤。")
    else:
        st.info("缺少 'Keyword' 欄位，無法提供內容建議。")

    # Export Option for cleaned data
    st.subheader("匯出清理後的數據")
    csv = df_clean.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下載清理後的數據 (CSV)",
        data=csv,
        file_name='seo_dashboard_cleaned.csv',
        mime='text/csv',
    )

    # Export Option for actionable analysis results
    st.subheader("匯出分析建議結果")
    analysis_frames = []
    if 'table1' in locals() and not table1.empty:
        table1_export = table1.copy()
        table1_export["建議類型"] = "高曝光低CTR"
        analysis_frames.append(table1_export)
    if 'table2' in locals() and not table2.empty:
        table2_export = table2.copy()
        table2_export["建議類型"] = "曝光不錯但排名後段"
        analysis_frames.append(table2_export)
    if analysis_frames:
        analysis_result = pd.concat(analysis_frames, ignore_index=True)
        export_cols = ["Keyword", "Impressions", "Clicks", "CTR", "Position", "建議類型"]
        analysis_result = analysis_result[[col for col in export_cols if col in analysis_result.columns]]
        csv_analysis = analysis_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下載分析建議結果 (CSV)",
            data=csv_analysis,
            file_name='seo_dashboard_analysis.csv',
            mime='text/csv',
        )
    else:
        st.info("目前沒有符合條件的分析建議可供下載。")
else:
    st.warning("請先上傳 CSV 數據檔案以開始分析。")
