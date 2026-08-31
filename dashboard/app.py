# app.py
#
# WearWise 後台數據視覺化面板
#
# 
#
# ============================================================
# 這一版的重點修正（相較上一版）：
# 1. 補上「使用情境」統計圖（問卷第1題：運動/日常生活/商務/健康管理/穿搭），
#    上一版誤把這題跟第9題的「使用情境定位」搞混，只做了後者。
# 2. 側邊欄的來源篩選（filter / chat）、日期範圍篩選，現在是真的會
#    影響所有圖表與 KPI 數字，因為底層資料改成「一筆一筆的原始事件」，
#    篩選後才即時用 pandas 重新計算統計，不再是套用寫死的總和數字。
# 3. 「資料範圍」不是一個會被清空或重置的東西，只是「這次要看哪個
#    時間窗口」的篩選條件；資料庫本身會持續累積，之後接上後端1的
#    真實資料時，使用者可以自由選擇要看近7天、近30天或自訂區間。
#
# 之後串接後端1：
#   把「資料來源」區塊的 `events_df = pd.DataFrame(MOCK_EVENTS)`
#   換成呼叫後端1的原始事件 API，例如：
#   events_df = pd.DataFrame(requests.get(f"{API_BASE}/analytics/events").json())
#   其餘統計、篩選、圖表程式碼完全不用改。
#
# 執行方式：
#   pip install -r requirements.txt
#   streamlit run app.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
import requests

from mock_data import MOCK_EVENTS, SPONSORED_BRANDS, BUDGET_OPTIONS

# ============================================================
# 頁面基本設定
# ============================================================
st.set_page_config(
    page_title="WearWise 數據儀表板",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 品牌色彩（對齊 Flutter App 的深海藍 + 電光藍主題）
# ============================================================
NAVY = "#0A0E1A"
CARD_BG = "#111827"
BORDER = "#1E293B"
BLUE = "#3B82F6"
BLUE_LIGHT = "#60A5FA"
TEXT_MAIN = "#E5E7EB"
TEXT_SUB = "#94A3B8"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
SPONSOR_GOLD = "#F59E0B"

CHART_COLORWAY = ["#3B82F6", "#60A5FA", "#93C5FD", "#1D4ED8", "#0EA5E9", "#38BDF8", "#818CF8"]

# ============================================================
# 自訂 CSS
# ============================================================
st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; }}
    .kpi-card {{
        background-color: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
    }}
    .kpi-label {{ color: {TEXT_SUB}; font-size: 13px; margin-bottom: 6px; }}
    .kpi-value {{ color: {TEXT_MAIN}; font-size: 26px; font-weight: 700; line-height: 1.2; }}
    .kpi-sub {{ color: {SUCCESS}; font-size: 12px; margin-top: 4px; }}
    .section-title {{
        color: {TEXT_MAIN}; font-size: 17px; font-weight: 600;
        margin: 4px 0 14px 0; padding-left: 12px; border-left: 4px solid {BLUE};
    }}
    .insight-box {{
        background-color: {CARD_BG}; border: 1px solid {BORDER}; border-left: 4px solid {BLUE};
        border-radius: 10px; padding: 16px 20px; color: {TEXT_SUB}; font-size: 14px; line-height: 1.8;
    }}
    .insight-box b {{ color: {TEXT_MAIN}; }}
    .chart-card {{
        background-color: {CARD_BG}; border: 1px solid {BORDER};
        border-radius: 14px; padding: 14px 16px 4px 16px;
    }}
    .empty-state {{
        background-color: {CARD_BG}; border: 1px dashed {BORDER}; border-radius: 12px;
        padding: 40px 20px; text-align: center; color: {TEXT_SUB};
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 共用工具函式
# ============================================================
def style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    """統一套用深色主題到圖表上"""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MAIN, size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SUB)),
        colorway=CHART_COLORWAY,
    )
    fig.update_xaxes(showgrid=False, color=TEXT_SUB, linecolor=BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, color=TEXT_SUB, zeroline=False)
    
    # 預設 hover 提示裡的「=」換成「：」
    for trace in fig.data:
        if trace.hovertemplate:
            trace.hovertemplate = trace.hovertemplate.replace("=", "：")
    
    return fig


def kpi_card(col, label: str, value: str, sub: str = ""):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def counter_to_df(counter: Counter, key_name: str, value_name: str = "次數") -> pd.DataFrame:
    """把 Counter 轉成排序好的 DataFrame，次數由大到小"""
    df = pd.DataFrame(counter.items(), columns=[key_name, value_name])
    return df.sort_values(value_name, ascending=False).reset_index(drop=True)


def count_single_value_column(df: pd.DataFrame, column: str, drop_empty: bool = True) -> Counter:
    """統計「單選欄位」：每一列就是一個值，直接數次數"""
    series = df[column].astype(str)
    if drop_empty:
        series = series[series.str.strip() != ""]
    return Counter(series)


def count_multi_value_column(df: pd.DataFrame, column: str, sep: str = ",") -> Counter:
    """
    統計「逗號分隔的多選欄位」（例如 features、usage）。
    每一列可能是 "GPS,睡眠追蹤"，要展開成多筆再統計，
    這對應到之前文件裡說的「後端用 Python Counter 展開計算」做法，
    只是這裡直接在前端做，不用等後端寫這段邏輯。
    """
    counter = Counter()
    for cell in df[column].dropna():
        for item in str(cell).split(sep):
            item = item.strip()
            if item:
                counter[item] += 1
    return counter


# ============================================================
# 資料來源
# ------------------------------------------------------------
# 目前讀取假資料（一筆一筆的原始事件）；
# 之後後端1把 /analytics/events 接上後，只要把這行換成呼叫 API，
# 下面所有統計、篩選、圖表程式碼都不用改。
# ============================================================
# 開關：後端1的 /analytics/events 還沒好之前先用 True
USE_MOCK_DATA = False
API_BASE = "https://champion-sandpit-rash.ngrok-free.dev"  # 後端1的 ngrok 網址

if USE_MOCK_DATA:
    events_df = pd.DataFrame(MOCK_EVENTS)
else:
    response = requests.get(
        f"{API_BASE}/analytics/events",
        headers={"ngrok-skip-browser-warning": "true"},
        timeout=10,
    )

    # 先檢查 HTTP 狀態碼跟實際回傳內容，不要直接 .json()
    if response.status_code != 200:
        st.error(f"後端回應狀態碼異常：{response.status_code}")
        st.code(response.text[:1000])  # 印出前1000字，看實際回了什麼
        st.stop()

    try:
        events_df = pd.DataFrame(response.json())
    except ValueError:
        st.error("後端回應的不是 JSON 格式，以下是實際收到的內容：")
        st.code(response.text[:1000])
        st.stop()

events_df["created_at"] = pd.to_datetime(events_df["created_at"])

# budget_min/budget_max 換算成跟問卷一致的級距文字，
# 沿用原本 "budget_bucket" 欄位名稱，下面圖表程式碼不用再改
events_df["budget_bucket"] = pd.cut(
    events_df[["budget_min", "budget_max"]].mean(axis=1),
    bins=[-1, 5000, 15000, 30000, float("inf")],
    labels=BUDGET_OPTIONS,
)

# 特別處理「跳過預算題」的情況（min=0 且 max=999999），
# 不能被 pd.cut 誤判成「30,000以上」，要獨立標成「未填寫」
skipped_budget = (events_df["budget_min"] == 0) & (events_df["budget_max"] == 999999)
events_df["budget_bucket"] = events_df["budget_bucket"].astype(str)
events_df.loc[skipped_budget, "budget_bucket"] = ""

# 所有可能跳過的單選欄位，一次補空字串，避免變成假分類 "nan"
skippable_columns = ["os", "device_type", "usage_scope"]
for col in skippable_columns:
    events_df[col] = events_df[col].fillna("")

data_min_date = events_df["created_at"].min().date()
data_max_date = events_df["created_at"].max().date()


# ============================================================
# 側邊欄：篩選條件（會真正影響下面所有統計）與說明
# ============================================================
with st.sidebar:
    st.markdown("### ⌚ WearWise")
    st.caption("合作廠商 × 使用者偏好　數據後台")
    st.divider()

    st.markdown("**事件來源**")
    source_options = sorted(events_df["source"].unique().tolist())
    selected_sources = st.multiselect(
        "顯示的事件來源", options=source_options, default=source_options,
        help="filter：問卷篩選　／　chat：AI 聊天室　（此篩選會即時重新計算下方所有圖表）",
        label_visibility="collapsed",
    )

    st.markdown("**時間範圍**")
    st.caption("選擇時間範圍")
    date_range = st.date_input(
        "選擇日期區間", value=(data_min_date, data_max_date),
        min_value=data_min_date, max_value=data_max_date,
        label_visibility="collapsed",
    )
    # st.date_input 在只選了一個日期時會回傳單一 date 而非 tuple，這裡防呆處理
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = data_min_date, data_max_date

    st.divider()
    st.markdown("**🔒 隱私原則**")
    st.caption(
        "本頁僅呈現去識別化後的統計數字（年齡層、功能需求等分類欄位），"
        "不包含任何可反查回個別使用者的資訊，如帳號、暱稱或聯絡方式。"
    )

    st.divider()
    st.caption(f"儀表板載入時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption(f"目前資料庫涵蓋範圍：{data_min_date} ～ {data_max_date}")


# ============================================================
# 套用篩選：來源 + 日期區間
# ============================================================
filtered_df = events_df[
    (events_df["source"].isin(selected_sources))
    & (events_df["created_at"].dt.date >= start_date)
    & (events_df["created_at"].dt.date <= end_date)
]

# ============================================================
# 頁首
# ============================================================
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("## WearWise 數據儀表板")
    st.caption("匿名化使用者偏好統計報告")
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 重新整理資料", use_container_width=True)

st.write("")

# ------------------------------------------------------------
# 篩選後沒有任何資料：顯示空狀態，不要讓圖表區塊直接報錯或空白一片
# ------------------------------------------------------------
if filtered_df.empty:
    st.markdown(
        '<div class="empty-state">📭　所選的時間範圍或事件來源內沒有資料，請調整左側篩選條件</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# 統計運算（全部根據 filtered_df 即時算出）
# ============================================================
usage_counter = count_multi_value_column(filtered_df, "usage")
feature_counter = count_multi_value_column(filtered_df, "features")
device_counter = count_single_value_column(filtered_df, "device_type")
budget_counter = count_single_value_column(filtered_df, "budget_bucket")
os_counter = count_single_value_column(filtered_df, "os")
age_counter = count_single_value_column(filtered_df, "age_range")
usage_scope_counter = count_single_value_column(filtered_df, "usage_scope", drop_empty=True)
brand_counter = count_multi_value_column(filtered_df, "top_brands")
platform_counter = count_multi_value_column(filtered_df, "top_platforms")
source_counter = count_single_value_column(filtered_df, "source")

df_trend = (
    filtered_df.groupby(filtered_df["created_at"].dt.date)
    .size()
    .reset_index(name="count")
    .rename(columns={"created_at": "date"})
)

sponsored_set = set(SPONSORED_BRANDS)
sponsored_exposure = sum(v for k, v in brand_counter.items() if k in sponsored_set)
total_brand_count = sum(brand_counter.values())
sponsored_ratio = (sponsored_exposure / total_brand_count * 100) if total_brand_count else 0

top_usage = usage_counter.most_common(1)[0][0] if usage_counter else "—"
top_feature = feature_counter.most_common(1)[0][0] if feature_counter else "—"
top_platform = platform_counter.most_common(1)[0][0] if platform_counter else "—"
top_brand = brand_counter.most_common(1)[0][0] if brand_counter else "—"
top_device = device_counter.most_common(1)[0][0] if device_counter else "—"

# ============================================================
# KPI 總覽列
# ============================================================
kpi_cols = st.columns(4)
kpi_card(kpi_cols[0], "篩選後事件數", f"{len(filtered_df)}", f"共 {len(events_df)} 筆資料中")
kpi_card(kpi_cols[1], "熱門使用情境", top_usage.split("（")[0], f"{usage_counter[top_usage]} 次提及")
kpi_card(kpi_cols[2], "熱門來源平台", top_platform, f"{platform_counter[top_platform]} 次曝光")
kpi_card(kpi_cols[3], "最關注的功能需求", top_feature, f"{feature_counter[top_feature]} 次提及")

st.write("")

# ============================================================
# 文字洞察摘要
# ============================================================
insight_text = f"""
在目前篩選範圍（{start_date} ～ {end_date}，來源：{ "、".join(selected_sources) }）中，
使用者最主要的使用情境是 <b>{top_usage}</b>，最關注的功能需求是 <b>{top_feature}</b>，
裝置偏好以 <b>{top_device}</b> 為主；推薦結果前3名中，合作品牌
（{ "、".join(sponsored_set) }）合計佔 <b>{sponsored_ratio:.1f}%</b>，
<b>{top_brand}</b> 是曝光次數最高的品牌，來源平台以 <b>{top_platform}</b> 曝光最多。
"""
st.markdown(f'<div class="insight-box">💡 {insight_text}</div>', unsafe_allow_html=True)

st.write("")
st.write("")

# ============================================================
# 分頁籤
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯　需求與預算",
    "👥　裝置與族群",
    "🏷️　品牌與平台曝光",
    "📈　查詢趨勢",
])

# ------------------------------------------------------------
# Tab 1：需求與預算
# ------------------------------------------------------------
with tab1:
    section_title("使用情境分布")
    df_usage = counter_to_df(usage_counter, "使用情境")
    fig_usage = px.bar(df_usage, x="次數", y="使用情境", orientation="h", text="次數")
    fig_usage.update_traces(marker_color=BLUE, textposition="outside")
    fig_usage.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(style_fig(fig_usage, height=280), use_container_width=True)

    st.write("")
    section_title("熱門功能需求排行")
    col1, col2 = st.columns([2, 1])
    with col1:
        df_features = counter_to_df(feature_counter, "功能")
        fig = px.bar(df_features, x="次數", y="功能", orientation="h", text="次數")
        fig.update_traces(marker_color=BLUE_LIGHT, textposition="outside")
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(style_fig(fig, height=300), use_container_width=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**功能需求佔比**")
        fig_pie = px.pie(df_features, names="功能", values="次數", hole=0.55)
        fig_pie.update_traces(textinfo="percent", textfont_color=TEXT_MAIN)
        st.plotly_chart(style_fig(fig_pie, height=260), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    section_title("預算區間分布")
    df_budget = counter_to_df(budget_counter, "預算區間", "人數")
    fig_budget = px.bar(df_budget, x="預算區間", y="人數", text="人數")
    fig_budget.update_traces(marker_color=BLUE, textposition="outside")
    st.plotly_chart(style_fig(fig_budget, height=300), use_container_width=True)

    with st.expander("查看原始統計數字"):
        st.dataframe(df_usage, use_container_width=True, hide_index=True)
        st.dataframe(df_features, use_container_width=True, hide_index=True)
        st.dataframe(df_budget, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Tab 2：裝置與族群
# ------------------------------------------------------------
with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**裝置類型偏好**")
        df_device = counter_to_df(device_counter, "裝置")
        fig = px.pie(df_device, names="裝置", values="次數", hole=0.55)
        fig.update_traces(textinfo="percent+label", textfont_color=TEXT_MAIN)
        st.plotly_chart(style_fig(fig, height=280), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**作業系統偏好**")
        df_os = counter_to_df(os_counter, "系統")
        fig = px.pie(df_os, names="系統", values="次數", hole=0.55)
        fig.update_traces(textinfo="percent+label", textfont_color=TEXT_MAIN)
        st.plotly_chart(style_fig(fig, height=280), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**使用情境定位**")
        st.caption("個人使用 / 家庭共用 / 送禮")
        if usage_scope_counter:
            df_scope = counter_to_df(usage_scope_counter, "情境")
            fig = px.pie(df_scope, names="情境", values="次數", hole=0.55)
            fig.update_traces(textinfo="percent+label", textfont_color=TEXT_MAIN)
            st.plotly_chart(style_fig(fig, height=280), use_container_width=True)
        else:
            st.caption("目前篩選範圍內，這一題都沒有人填答")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    section_title("年齡層分布")
    df_age = counter_to_df(age_counter, "年齡層")
    # 依年齡層邏輯順序排列，而不是依次數排序，閱讀起來更直覺
    age_order = ["18歲以下", "19–25歲", "26–35歲", "36–45歲", "46–55歲", "56歲以上"]
    df_age["年齡層"] = pd.Categorical(df_age["年齡層"], categories=age_order, ordered=True)
    df_age = df_age.sort_values("年齡層")
    fig_age = px.bar(df_age, x="年齡層", y="次數", text="次數")
    fig_age.update_traces(marker_color=BLUE, textposition="outside")
    st.plotly_chart(style_fig(fig_age, height=300), use_container_width=True)

    with st.expander("查看原始統計數字"):
        st.dataframe(df_age, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Tab 3：品牌與平台曝光
# ------------------------------------------------------------
with tab3:
    st.caption("🥇 標示為「合作品牌」的長條會用金色特別標示，方便對照加權效果")

    section_title("品牌關注度（推薦結果前3名的品牌次數）")
    df_brand = counter_to_df(brand_counter, "品牌")
    df_brand["是否合作"] = df_brand["品牌"].apply(
        lambda b: "合作品牌" if b in sponsored_set else "一般品牌"
    )
    fig_brand = px.bar(
        df_brand, x="品牌", y="次數", text="次數", color="是否合作",
        color_discrete_map={"合作品牌": SPONSOR_GOLD, "一般品牌": BLUE},
    )
    fig_brand.update_traces(textposition="outside")
    st.plotly_chart(style_fig(fig_brand, height=320), use_container_width=True)

    st.write("")
    section_title("來源平台曝光次數")
    df_platform = counter_to_df(platform_counter, "平台")
    fig_platform = px.bar(df_platform, x="平台", y="次數", text="次數")
    fig_platform.update_traces(marker_color=BLUE_LIGHT, textposition="outside")
    st.plotly_chart(style_fig(fig_platform, height=300), use_container_width=True)

    with st.expander("查看原始統計數字"):
        st.dataframe(df_brand, use_container_width=True, hide_index=True)
        st.dataframe(df_platform, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Tab 4：查詢趨勢
# ------------------------------------------------------------
with tab4:
    section_title(f"每日查詢趨勢（{start_date} ～ {end_date}）")
    fig_trend = px.area(df_trend, x="date", y="count")
    fig_trend.update_traces(line_color=BLUE, fillcolor="rgba(59,130,246,0.15)")
    fig_trend.update_layout(xaxis_title="", yaxis_title="事件數")
    st.plotly_chart(style_fig(fig_trend, height=320), use_container_width=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**事件來源分布**")
        df_source = counter_to_df(source_counter, "來源")
        fig_source = px.pie(df_source, names="來源", values="次數", hole=0.55)
        fig_source.update_traces(textinfo="percent+label", textfont_color=TEXT_MAIN)
        st.plotly_chart(style_fig(fig_source, height=260), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**篩選範圍統計摘要**")
        st.metric("每日平均查詢數", f"{df_trend['count'].mean():.1f} 次")
        st.metric("單日最高查詢數", f"{df_trend['count'].max()} 次")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("查看原始統計數字"):
        st.dataframe(df_trend, use_container_width=True, hide_index=True)

# ============================================================
# 頁尾備註
# ============================================================
st.write("")
st.caption(
    "本儀表板資料皆為去識別化統計結果，僅供內部與合作品牌參考，不代表個別使用者身份。"
)
