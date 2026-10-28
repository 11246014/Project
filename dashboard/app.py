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
# 資料來源切換（改版後）：
#   .streamlit/secrets.toml 設定
#     api_base      = "https://你的ngrok網址"   # 後端1網址，變了只改這裡
#     use_mock_data = true / false              # true＝用 mock_data.py 假資料
#   其餘統計、篩選、圖表程式碼完全不用改。
#
# 2026-10 改版：依「WearWise 後台數據儀表板 改版規劃書」改成
#   「選一個品牌、和競品對照」的結構（品牌總覽 / 受眾與需求 / 競品對戰 /
#   贊助成效 / 品類總覽）。品牌清單由資料自動產生，新品牌會自動出現在側邊欄。
#
# 執行方式：
#   pip install -r requirements.txt
#   streamlit run app.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import html
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
    initial_sidebar_state="auto",
)

# ============================================================
# 密碼保護（給廠商 / 自己看的後臺數據，避免連結外流被隨意查看）
# ============================================================
def check_password():
    """
    密碼驗證函式。
    回傳 True 代表這次瀏覽階段（session）已通過密碼驗證。
    用 st.session_state 記住驗證結果，避免每次互動
    （切換篩選條件、日期範圍等）都要重新輸入密碼。
    """

    def password_entered():
        # 比對輸入框的值與 .streamlit/secrets.toml 裡設定的密碼
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            # 驗證成功後清掉輸入框的值，避免密碼字串殘留
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # 情況一：這次瀏覽階段第一次進來，還沒驗證過
    if "password_correct" not in st.session_state:
        st.text_input(
            "請輸入密碼",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False

    # 情況二：曾經輸入過，但密碼錯誤
    elif not st.session_state["password_correct"]:
        st.text_input(
            "請輸入密碼",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error("😕 密碼錯誤，請再試一次")
        return False

    # 情況三：已通過驗證
    else:
        return True


# 密碼沒過就整個 script 停在這裡，下面所有品牌色彩、CSS、
# 圖表、KPI 計算全部都不會執行，畫面上只會看到密碼輸入框
if not check_password():
    st.stop()


# ============================================================
# 品牌色彩（對齊 Flutter App 的深海藍 + 電光藍主題）
# ============================================================
NAVY = "#F2F5FA"        # 頁面背景（預覽淺色色票 --bg）
CARD_BG = "#FFFFFF"     # 卡片背景（--panel）
BORDER = "#D8DFEA"      # 邊線（--line）
BLUE = "#2563EB"        # 主色（--accent）
BLUE_LIGHT = "#3B82F6"  # 次主色（--accent-2）
TEXT_MAIN = "#0F172A"   # 主要文字（--fg）
TEXT_SUB = "#475569"    # 次要文字（--muted）
SUCCESS = "#15803D"     # 正向（--good）
WARNING = "#D97706"     # 警示 / 合作品牌金（--gold）
SPONSOR_GOLD = "#D97706"
FONT_FAMILY = '"Noto Sans TC", "Microsoft JhengHei", "PingFang TC", system-ui, sans-serif'

CHART_COLORWAY = ["#2563EB", "#3B82F6", "#93C5FD", "#1E40AF", "#0284C7", "#6366F1"]

# ============================================================
# 自訂 CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
/* ------------------------------------------------------------
   色票：預覽（mock_dashboard.html）淺色那組。
   以下「一般 class」（.kpi / .sec / .row ...）是我們自己輸出的 HTML，穩定；
   最底下標示「Streamlit 內部選擇器」的區塊，升級 Streamlit 後若失效，
   只會讓外觀變回預設，不影響任何功能。
   ------------------------------------------------------------ */
:root {
  --bg: #F2F5FA; --panel: #FFFFFF; --panel-2: #F7F9FC; --line: #D8DFEA;
  --fg: #0F172A; --muted: #475569; --accent: #2563EB; --accent-2: #3B82F6;
  --gold: #D97706; --good: #15803D; --bad: #B91C1C;
  --bar-all: #94A3B8; --bar-comp: #64748B; --track: #E6EBF3;
  --st-mod-bg: #FDF0C9; --st-mod-fg: #8A5A00;
  --font: "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", system-ui, sans-serif;
}
.head { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; flex-wrap: wrap; margin-bottom: 4px; }
.head h1 { font-size: 22px; line-height: 1.3; margin: 0; padding: 0; color: var(--fg); font-weight: 700; }
.head .sub { color: var(--muted); font-size: 13px; }
.mode { font-size: 12px; font-weight: 700; padding: 3px 12px; border-radius: 999px; background: var(--accent); color: #fff; white-space: nowrap; }
.mode.cat { background: var(--bar-all); }
.kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 4px 0 14px; }
.kpi { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; min-width: 0; }
.kpi .l { color: var(--muted); font-size: 12.5px; }
.kpi .v { color: var(--fg); font-size: 24px; font-weight: 700; line-height: 1.25; margin-top: 4px; overflow-wrap: anywhere; }
.kpi .s { font-size: 12px; margin-top: 2px; color: var(--muted); }
.kpi .s.up { color: var(--good); } .kpi .s.down { color: var(--bad); } .kpi .s.warn { color: var(--gold); }
.insight { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 10px;
  padding: 13px 16px; color: var(--muted); line-height: 1.8; font-size: 14px; margin-bottom: 14px; }
.insight b { color: var(--fg); }
.sec { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; min-width: 0; margin-bottom: 14px; }
.sec.open { border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: 0; margin-bottom: 0; padding-bottom: 6px; }
.sec-head { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 4px; }
.sec-head h2 { font-size: 15.5px; margin: 0 4px 0 0; padding: 0; color: var(--fg); font-weight: 700; }
.sec-head .n { color: var(--muted); font-size: 12px; margin-left: auto; }
.how { color: var(--muted); font-size: 12.5px; margin: 0 0 12px; }
.how b { color: var(--fg); font-weight: 500; }
.sub-h { font-size: 13px; margin: 0 0 8px; color: var(--fg); font-weight: 700; }
.n-inline { color: var(--muted); font-size: 12px; font-weight: 400; margin-left: 8px; }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
.rows { display: flex; flex-direction: column; gap: 9px; }
.row { display: grid; grid-template-columns: minmax(70px, 120px) minmax(0, 1fr) auto; gap: 10px; align-items: center; }
.row .lb { font-size: 13px; overflow-wrap: anywhere; color: var(--fg); }
.row .lb.sel { color: var(--accent); font-weight: 700; }
.row .vl { font-size: 12.5px; color: var(--muted); text-align: right; min-width: 70px; }
.row .vl.wide { min-width: 150px; line-height: 1.35; }
.track { position: relative; height: 12px; background: var(--track); border-radius: 6px; overflow: hidden; }
.track.thin { height: 7px; }
.fill { height: 100%; border-radius: 6px; background: var(--accent); }
.fill.gold { background: var(--gold); } .fill.all { background: var(--bar-all); } .fill.comp { background: var(--bar-comp); }
.fill.soft { opacity: .45; }
.fill.up { background: var(--accent); } .fill.mid { background: var(--bar-comp); } .fill.low { background: var(--bar-all); opacity: .7; }
.mark { position: absolute; top: -2px; bottom: -2px; width: 0; border-left: 2px dashed var(--fg); opacity: .65; }
.grp { display: flex; flex-direction: column; gap: 3px; }
.grp .glabel { font-size: 13px; margin-bottom: 1px; color: var(--fg); }
.gline { display: grid; grid-template-columns: 62px minmax(0, 1fr) 48px; gap: 8px; align-items: center; font-size: 11.5px; color: var(--muted); }
.gline span:last-child { text-align: right; }
.gwrap { display: flex; flex-direction: column; gap: 12px; }
.key { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--muted); margin-bottom: 10px; }
.key i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.mask { color: var(--muted); font-size: 12px; font-style: italic; }
.opp { font-size: 11px; font-weight: 700; color: var(--st-mod-fg); background: var(--st-mod-bg); border-radius: 999px; padding: 0 7px; margin-left: 6px; }
.hint-box, .empty-state { border: 1px dashed var(--line); border-radius: 12px; padding: 22px; text-align: center; color: var(--muted); background: var(--panel-2); }
.tablewrap { overflow-x: auto; }
.tablewrap table { border-collapse: collapse; width: 100%; font-size: 13px; }
.tablewrap th, .tablewrap td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; color: var(--fg); }
.tablewrap th { color: var(--muted); font-weight: 500; font-size: 12px; }
.tablewrap td.num, .tablewrap th.num { text-align: right; }
.donut-wrap { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
.donut { width: 112px; height: 112px; border-radius: 50%; position: relative; flex: none; }
.donut::after { content: ""; position: absolute; inset: 26px; background: var(--panel); border-radius: 50%; }
.dl { display: flex; flex-direction: column; gap: 3px; font-size: 12.5px; min-width: 0; color: var(--fg); }
.dl i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; }
.foot { color: var(--muted); font-size: 12px; margin: 8px 0 0; }
@media (max-width: 920px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) {
  .row { grid-template-columns: minmax(60px, 90px) minmax(0, 1fr) auto; gap: 8px; }
  .kpi .v { font-size: 20px; }
  .row .vl.wide { min-width: 110px; }
}
@media (prefers-reduced-motion: no-preference) { .fill { transition: width .25s ease; } }

/* ------------------------------------------------------------
   ↓↓ Streamlit 內部選擇器（集中在這裡）↓↓
   這些是 Streamlit 自己產生的元素，版本升級後 class / data-testid 可能改名。
   失效時只會讓外觀退回預設樣式，不會影響任何功能。
   ------------------------------------------------------------ */
.stApp { background: var(--bg); font-family: var(--font); }
.block-container { max-width: 1280px; padding-top: 3.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { border-right: 1px solid var(--line); }
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-weight: 500; padding: 9px 14px; }
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
        font=dict(color=TEXT_MAIN, size=12, family=FONT_FAMILY),
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


def kpi_card(col, label: str, value: str, sub: str = "", sub_color: str = SUCCESS):
    """KPI 卡片；sub_color 可讓『落後 / 樣本不足』用紅或橘色顯示"""
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub" style="color:{sub_color};">{sub}</div>
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
# 使用情境 / 裝置類型 標籤正規化（顯示層）
# ------------------------------------------------------------
# 問卷（FilterScreen）送出的是完整選項字串，但 AI 聊天室那邊
# 經過 backend2 的 normalize_usage() 正規化後，會變成不同粒度
# 的詞（running / sleep / 運動...），導致「使用情境分布」把
# 同一種情境拆成好幾條 bar。這裡統一對應回問卷的 5 個分類。
# 不修改後端2的邏輯，避免影響 AI 比對/評分。
# ============================================================
USAGE_LABEL_MAP = {
    # 運動（跑步 / 健身 / 戶外）
    "運動": "運動（跑步 / 健身 / 戶外）",
    "運動（跑步／健身／戶外）": "運動（跑步 / 健身 / 戶外）",
    "running": "運動（跑步 / 健身 / 戶外）",
    "run": "運動（跑步 / 健身 / 戶外）",
    "跑步": "運動（跑步 / 健身 / 戶外）",
    "健身": "運動（跑步 / 健身 / 戶外）",
    "hiking": "運動（跑步 / 健身 / 戶外）",
    "outdoor": "運動（跑步 / 健身 / 戶外）",
    "登山": "運動（跑步 / 健身 / 戶外）",
    "戶外": "運動（跑步 / 健身 / 戶外）",

    # 日常生活（看時間 / 通知）
    "日常": "日常生活（看時間 / 通知）",
    "日常生活": "日常生活（看時間 / 通知）",
    "看時間": "日常生活（看時間 / 通知）",
    "通知": "日常生活（看時間 / 通知）",

    # 工作 / 商務（訊息 / 行事曆）
    "商務": "工作 / 商務（訊息 / 行事曆）",
    "工作": "工作 / 商務（訊息 / 行事曆）",
    "訊息": "工作 / 商務（訊息 / 行事曆）",
    "行事曆": "工作 / 商務（訊息 / 行事曆）",
    "business": "工作 / 商務（訊息 / 行事曆）",
    "office": "工作 / 商務（訊息 / 行事曆）",

    # 健康管理（心率 / 睡眠）
    "health": "健康管理（心率 / 睡眠）",
    "health_monitoring": "健康管理（心率 / 睡眠）",
    "健康": "健康管理（心率 / 睡眠）",
    "健康監測": "健康管理（心率 / 睡眠）",
    "sleep": "健康管理（心率 / 睡眠）",
    "sleep_monitoring": "健康管理（心率 / 睡眠）",
    "sleep_tracking": "健康管理（心率 / 睡眠）",
    "睡眠": "健康管理（心率 / 睡眠）",
    "睡眠監測": "健康管理（心率 / 睡眠）",
    "心率": "健康管理（心率 / 睡眠）",

    # 穿搭 / 外型
    "穿搭": "穿搭 / 外型",
    "外型": "穿搭 / 外型",
    "style": "穿搭 / 外型",
    "fashion": "穿搭 / 外型",
}


def normalize_usage_label(raw: str) -> str:
    """把單一使用情境字串對應回問卷的 5 個標準分類；查不到就維持原字串
    （這樣未來若出現新詞彙，圖表上還是看得到，方便回來補字典，
    而不是被吃掉查不出問題）"""
    if not raw:
        return raw
    stripped = raw.strip()
    return USAGE_LABEL_MAP.get(stripped) or USAGE_LABEL_MAP.get(stripped.lower(), stripped)


def normalize_usage_column(value: str) -> str:
    """usage 欄位是逗號分隔的多選字串，要逐一正規化後再組回去，
    並去除正規化後可能出現的重複（例如原始資料同時有「運動」跟「跑步」）"""
    if not value or not isinstance(value, str):
        return value
    items = [normalize_usage_label(v) for v in value.split(",") if v.strip()]
    return ",".join(dict.fromkeys(items))  # dict.fromkeys 去重且保留順序


DEVICE_LABEL_MAP = {
    "smartwatch": "手錶",
    "smart_watch": "手錶",
    "手錶": "手錶",

    "smart_band": "手環",
    "smart band": "手環",
    "手環": "手環",

    "smart_ring": "戒指",
    "smart ring": "戒指",
    "戒指": "戒指",
}


def normalize_device_label(raw: str) -> str:
    """把 device_type 的英文 enum（後端2 normalize_device_type 的輸出）
    對應回問卷的 4 個中文分類；查不到就一律歸類到「其他」
    （對應問卷第6題的第4個選項，也涵蓋 earbuds 等未來可能新增的裝置類型）"""
    if not raw:
        return raw
    return DEVICE_LABEL_MAP.get(raw.strip().lower(), "其他")


# ============================================================
# 品牌名稱正規化 BRAND_LABEL_MAP（顯示層，文件 Q1 / 第 6 章）
# ------------------------------------------------------------
# 為什麼需要：品牌分析（份額、競品對戰）全部靠「品牌名稱完全相同」來
# 歸戶。如果同一品牌有多種寫法（Apple / apple / 蘋果 / Apple Watch，
# 或型號混進品牌欄 Garmin Forerunner 255），就會被拆成好幾個品牌，
# 份額被稀釋、競品組出現「自己 vs 自己」。
#
# 作法（只在 app.py 顯示層處理，不動後端 2 的評分）：
#   1. 先查「別名對照表」→ 對到就換成標準名稱
#   2. 查不到時，用「去掉空白與標點、轉小寫」的 key 把寫法不同的同一個詞
#      自動合併（例如 UltraHuman / Ultrahuman / ultra human）
#   3. 全新的品牌維持原字串，會自動出現在側邊欄（不需要手動加）
# 之後若在「資料品質檢查」發現新的別名，只要在下面這張表補一行即可。
# ============================================================
BRAND_LABEL_MAP = {
    # 標準名稱: [別名, ...]（比對時不分大小寫、忽略空白 - _ . 等符號）
    "Apple": ["apple", "蘋果", "apple watch", "iwatch", "apple inc"],
    "Garmin": ["garmin", "佳明"],
    "Amazfit": ["amazfit", "華米", "zepp", "zepp health", "huami"],
    "Xiaomi": ["xiaomi", "小米", "mi", "mi band", "xiaomi band", "xiaomi watch"],
    "Samsung": ["samsung", "三星", "galaxy watch", "galaxy fit", "galaxy ring"],
    "Huawei": ["huawei", "華為", "huawei watch", "huawei band"],
    "Fitbit": ["fitbit", "google fitbit"],
    "Google": ["google", "pixel watch", "google pixel watch"],
    "Oura": ["oura", "oura ring", "奧拉"],
    "Ultrahuman": ["ultrahuman", "ultra human"],
    "Coros": ["coros", "高馳"],
    "Polar": ["polar", "博能"],
    "Suunto": ["suunto", "頌拓"],
    "Withings": ["withings"],
    "Casio": ["casio", "卡西歐", "g-shock"],
    "Fossil": ["fossil", "化石"],
    "Honor": ["honor", "榮耀"],
    "OPPO": ["oppo"],
    "realme": ["realme"],
    "Whoop": ["whoop"],
    "RingConn": ["ringconn"],
    "Mobvoi": ["mobvoi", "ticwatch", "出門問問"],
}


# 後端對「查不到品牌」的商品會填 Other 之類的占位字串，它不是真的品牌，
# 若當成品牌會變成「Other」長條、還會被選成競品。這裡視為「沒有品牌資料」直接排除
# （等同文件說的「沒有品牌欄位的商品被略過」）。
BRAND_IGNORE = {"other", "others", "其他", "unknown", "未知", "none", "null", "n/a", "na", "無", "未分類", "-"}


def is_non_brand(raw: str) -> bool:
    """是否為占位字串（Other / Unknown…），不算品牌"""
    return _brand_key(raw) in BRAND_IGNORE


def _brand_key(text: str) -> str:
    """把品牌字串轉成比對用 key：轉小寫、去掉空白與常見標點"""
    return re.sub(r"[\s\-_.·'’`]+", "", str(text)).lower()


# 別名 key → 標準名稱（標準名稱本身也算別名）
_BRAND_ALIAS_LOOKUP = {}
for _canon, _aliases in BRAND_LABEL_MAP.items():
    _BRAND_ALIAS_LOOKUP[_brand_key(_canon)] = _canon
    for _alias in _aliases:
        _BRAND_ALIAS_LOOKUP[_brand_key(_alias)] = _canon

# 「型號混進品牌欄」的處理：別名夠長（英文 >=4 字、中文 >=2 字）時，
# 只要品牌字串「包含」它就歸到該品牌（例如 "Garmin Forerunner 255" → Garmin）
_BRAND_SUBSTRING_ALIASES = sorted(
    [
        (key, canon) for key, canon in _BRAND_ALIAS_LOOKUP.items()
        if (key.isascii() and len(key) >= 4) or (not key.isascii() and len(key) >= 2)
    ],
    key=lambda kv: -len(kv[0]),  # 長的先比，避免短別名搶先命中
)


def lookup_brand(raw: str):
    """用對照表找標準品牌名稱；找不到回傳 None（交給自動合併處理）"""
    key = _brand_key(raw)
    if not key:
        return None
    if key in _BRAND_ALIAS_LOOKUP:
        return _BRAND_ALIAS_LOOKUP[key]
    for alias_key, canon in _BRAND_SUBSTRING_ALIASES:
        if alias_key in key:
            return canon
    return None


def build_brand_mapping(cells: pd.Series):
    """
    掃描整欄 top_brands，建立「原始寫法 → 標準品牌名稱」的對照字典。
    回傳 (mapping, method, raw_counts)：
      mapping    原始寫法 → 標準名稱
      method     原始寫法 → 處理方式（原樣 / 對照表 / 自動合併）
      raw_counts 原始寫法 → 出現次數（資料品質檢查用）
    """
    raw_counts = Counter()
    for cell in cells.dropna():
        for item in str(cell).split(","):
            item = item.strip()
            if item:
                raw_counts[item] += 1

    mapping, method = {}, {}
    unknown_groups = {}  # 查不到對照表的品牌，依 key 分組（大小寫 / 空白不同視為同一個）
    for raw in raw_counts:
        if is_non_brand(raw):
            mapping[raw] = ""          # 空字串＝排除
            method[raw] = "排除（非品牌）"
            continue
        canon = lookup_brand(raw)
        if canon:
            mapping[raw] = canon
            method[raw] = "原樣" if canon == raw else "對照表"
        else:
            unknown_groups.setdefault(_brand_key(raw), []).append(raw)

    for items in unknown_groups.values():
        # 代表寫法：出現最多次；次數相同時偏好有大寫字母的（Ultrahuman 優於 ultrahuman）
        items.sort(key=lambda r: (-raw_counts[r], not any(ch.isupper() for ch in r), r))
        representative = items[0]
        for raw in items:
            mapping[raw] = representative
            method[raw] = "原樣" if raw == representative else "自動合併"
    return mapping, method, raw_counts


def apply_brand_mapping(cell, mapping: dict) -> str:
    """把一格 top_brands 字串依對照字典換成標準名稱（保留順序，不去重）"""
    if cell is None or (not isinstance(cell, str) and pd.isna(cell)):
        return ""
    mapped = (mapping.get(x.strip(), x.strip()) for x in str(cell).split(",") if x.strip())
    return ",".join(b for b in mapped if b)  # 被排除的占位字串（Other）不留下


def normalize_sponsor_name(name: str, mapping: dict) -> str:
    """合作品牌名單（來自 /sponsors）也要用同一套規則正規化，才對得到事件裡的品牌"""
    canon = lookup_brand(name)
    if canon:
        return canon
    if name in mapping:
        return mapping[name]
    key = _brand_key(name)
    for std in set(mapping.values()):
        if _brand_key(std) == key:
            return std
    return name.strip()


# ============================================================
# 職業歸類 OCCUPATION_LABEL_MAP（顯示層）
# ------------------------------------------------------------
# App 的「職業」是使用者自由輸入（提示：學生、工程師、教師、運動員），
# 同一種職業會有很多寫法（學生 / 大學生 / 研究生…），不歸類的話職業圖
# 會碎成一堆長條、每條都低於最小樣本門檻。這裡用「關鍵字包含」歸成
# 幾個大類；對不到的歸「其他」，並在資料品質檢查列出，方便回來補關鍵字。
# 順序很重要：越前面越優先。
# ============================================================
OCCUPATION_LABEL_MAP = [
    ("學生", ["學生", "大學", "研究所", "研究生", "高中", "國中", "碩士", "博士", "在學", "student"]),
    ("運動 / 健身", ["運動", "教練", "健身", "選手", "trainer", "coach", "athlete"]),
    ("工程師 / 科技業", ["工程", "程式", "軟體", "資訊", "科技", "研發", "設計", "資料", "產品經理",
                     "pm", "developer", "engineer", "designer", "r&d"]),
    ("教育 / 醫療", ["教師", "老師", "教授", "講師", "教育", "護理", "醫", "藥", "治療",
                   "teacher", "nurse", "doctor"]),
    ("自由工作者", ["自由", "接案", "自媒體", "創作", "攝影", "作家", "freelance", "youtuber"]),
    ("上班族", ["上班", "行政", "業務", "會計", "職員", "公司", "行銷", "企劃", "秘書", "助理",
              "公務", "金融", "銀行", "員工", "主管", "經理", "創業", "office"]),
]
OCCUPATION_OTHER = "其他"


def normalize_occupation_label(raw: str) -> str:
    """把自由輸入的職業歸成大類；空值維持空字串，對不到的歸『其他』"""
    if not raw or not isinstance(raw, str) or not raw.strip():
        return ""
    text = raw.strip().lower()
    for group, keywords in OCCUPATION_LABEL_MAP:
        if any(k in text for k in keywords):
            return group
    return OCCUPATION_OTHER


# ============================================================
# 設定讀取：API 網址、密碼、假資料開關都放 .streamlit/secrets.toml
# ------------------------------------------------------------
# 免費版 ngrok 每次重啟網址都會變，網址寫死在程式裡就得改程式；
# 放進設定檔後只要改 secrets.toml 的 api_base，不用動 app.py。
# ============================================================
def get_secret(key: str, default=None):
    """安全讀取 st.secrets：沒有設定檔或沒有該欄位時回傳預設值，不拋錯"""
    try:
        return st.secrets[key]
    except Exception:
        return default


# 開關：True＝使用 mock_data.py 的假資料（展示 / 後端沒好時）；
# False＝呼叫後端1。可在 secrets.toml 寫 use_mock_data = false 切換，
# 沒設定時預設用假資料（避免後端未啟動就整頁報錯）。
USE_MOCK_DATA = bool(get_secret("use_mock_data", True))
API_BASE = str(get_secret("api_base", "")).rstrip("/")  # 後端1的 ngrok 網址

# 品牌新舊判斷：第一次出現的日期在資料最後 N 天內，側邊欄標示 🆕
NEW_BRAND_DAYS = 10
ALL_BRANDS = "全部品牌（品類總覽）"  # 品牌下拉選單的「不選品牌」選項

# 圖表角色顏色（本品牌 / 競品組 / 全體）
COLOR_ME = "#2563EB"
COLOR_RIVAL = "#64748B"
COLOR_ALL = "#94A3B8"
COLOR_NEG = "#B91C1C"
GROUP_COLORS = {"本品牌": COLOR_ME, "競品組": COLOR_RIVAL, "全體": COLOR_ALL, "品類平均": COLOR_ALL}


@st.cache_data(ttl=60, show_spinner="載入資料中…")
def fetch_json(url: str):
    """
    呼叫後端1並回傳 JSON；結果快取 60 秒。
    快取的好處：側邊欄每動一次篩選，整支 script 都會重跑，沒有快取的話
    每次都會重打一次 API（ngrok 有延遲與額度限制）。按「重新整理資料」
    會清掉快取強制重抓。
    """
    resp = requests.get(url, headers={"ngrok-skip-browser-warning": "true"}, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# 統計用工具函式（文件第 6 章：共用計算規格）
# ============================================================
def show_chart(fig: go.Figure, key: str, height: int = 320, card: bool = False):
    """統一畫圖：套主題＋給每張圖獨立 key，避免多張相似圖片 ID 衝突。
    card=True 時圖底改白色，接在 sec_card(open_=True) 標題卡下方，看起來像同一張卡片"""
    fig = style_fig(fig, height=height)
    if card:
        fig.update_layout(paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG, margin=dict(l=18, r=18, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key=key)


def notice(text: str):
    """統一的提示框（未選品牌、樣本不足、無資料等情況，不報錯只提示）"""
    st.markdown(f'<div class="empty-state">{text}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# HTML 呈現小工具（只負責「長相」，數字一律由呼叫端傳入，這裡不做任何計算）
# 注意：st.markdown 會把「縮排 4 格以上」或「含空行」的內容當成程式碼 / 分段，
# 所以所有 HTML 都組成單行字串；從資料來的字串一律先過 esc()。
# ------------------------------------------------------------
def esc(x) -> str:
    """HTML 跳脫：資料來的字串（品牌名等）輸出前都要過這個。
    另外把 $ 轉成實體，避免 markdown 把 NT$…NT$ 當成數學公式。"""
    return html.escape(str(x)).replace("$", "&#36;")


def html_out(markup: str):
    """輸出一段 HTML"""
    st.markdown(markup, unsafe_allow_html=True)


def sec_card(title: str, body: str, n_text: str = "", how: str = "", open_: bool = False) -> str:
    """白底圓角卡片：標題＋右側 n 值＋一行『怎麼讀』＋內容。
    open_=True 表示下面還會接一張 Plotly 圖（卡片下緣不收口）"""
    n_html = f'<span class="n">{n_text}</span>' if n_text else ""
    how_html = f'<p class="how">{how}</p>' if how else ""
    return (f'<section class="sec{" open" if open_ else ""}"><div class="sec-head"><h2>{esc(title)}</h2>{n_html}</div>'
            f'{how_html}{body}</section>')


def hint_box(msg: str) -> str:
    """虛線提示框（msg 可含 <br>；來自資料的字串請先 esc）"""
    return f'<div class="hint-box">{msg}</div>'


def mask_row(label: str, n: int, thr: int) -> str:
    """樣本不足的列：斜體灰字，不畫數字（N9 最小樣本門檻）"""
    return (f'<div class="row"><div class="lb">{esc(label)}</div>'
            f'<div class="mask">樣本不足（n={n} &lt; {thr}）</div><div class="vl"></div></div>')


def bar_row(label: str, frac: float, text: str, cls: str = "", sel: bool = False) -> str:
    """橫向長條一列。frac＝0～1 的長度比例；cls：'' 藍 / gold 合作品牌 / all / comp"""
    width = 0.0 if frac != frac else max(0.0, min(100.0, frac * 100))  # frac != frac 即 NaN
    return (f'<div class="row"><div class="lb{" sel" if sel else ""}">{esc(label)}</div>'
            f'<div class="track"><div class="fill {cls}" style="width:{width:.1f}%"></div></div>'
            f'<div class="vl">{esc(text)}</div></div>')


def rows_block(rows: list) -> str:
    return '<div class="rows">' + "".join(rows) + '</div>'


def grouped_block(label_html: str, lines: list) -> str:
    """「本品牌／競品組／全體」三條一組的細長條。lines＝[(名稱, cls, 0~1 長度, 顯示文字)]"""
    inner = "".join(
        f'<div class="gline"><span>{esc(name)}</span><div class="track thin">'
        f'<div class="fill {cls}" style="width:{max(0.0, min(100.0, frac * 100)):.1f}%"></div></div>'
        f'<span>{esc(text)}</span></div>'
        for name, cls, frac, text in lines
    )
    return f'<div class="grp"><div class="glabel">{label_html}</div>{inner}</div>'


def key_html(items: list) -> str:
    """圖例：[(名稱, 顏色)]"""
    return '<div class="key">' + "".join(
        f'<span><i style="background:{color}"></i>{esc(name)}</span>' for name, color in items) + '</div>'


def html_table(headers: list, rows: list, num_idx: tuple = ()) -> str:
    """HTML 表格。rows 的每個儲存格是『已處理好（已 esc）的 HTML 字串』；num_idx＝靠右的欄位"""
    th = "".join(f'<th class="{"num" if i in num_idx else ""}">{esc(h)}</th>' for i, h in enumerate(headers))
    body = "".join(
        "<tr>" + "".join(f'<td class="{"num" if i in num_idx else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
        for r in rows)
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def count_bars_html(counter: Counter, order: list = None, cls: str = "") -> str:
    """把 Counter 畫成橫向長條（次數＋占比）；T5 的基準圖用，不做樣本遮蔽（維持改版前行為）"""
    if not counter:
        return '<p class="mask">目前篩選範圍內沒有資料</p>'
    keys = [k for k in order if k in counter] if order else [k for k, _ in counter.most_common()]
    total = sum(counter.values()) or 1
    top = max(counter.values())
    return rows_block([
        bar_row(k, counter[k] / top, f"{counter[k]}（{counter[k] / total * 100:.1f}%）", cls) for k in keys
    ])


def donut_html(counter: Counter) -> str:
    """甜甜圈圖（CSS conic-gradient）＋圖例"""
    if not counter:
        return '<p class="mask">目前篩選範圍內沒有資料</p>'
    colors = ["#2563EB", "#3B82F6", "#93C5FD", "#1E40AF", "#0284C7", "#6366F1"]
    items = counter.most_common()
    total = sum(v for _, v in items) or 1
    stops, acc = [], 0
    for i, (_, v) in enumerate(items):
        start = acc / total * 100
        acc += v
        stops.append(f"{colors[i % 6]} {start:.2f}% {acc / total * 100:.2f}%")
    legend = "".join(
        f'<span><i style="background:{colors[i % 6]}"></i>{esc(k)} {v / total * 100:.1f}%</span>'
        for i, (k, v) in enumerate(items))
    return (f'<div class="donut-wrap"><div class="donut" role="img" aria-label="占比圖" '
            f'style="background:conic-gradient({",".join(stops)})"></div><div class="dl">{legend}</div></div>')


def title_with_n(text: str, n=None):
    """區塊標題 + 樣本數 n（N9：每張圖都讓讀者知道是多少筆事件）"""
    suffix = (
        f' <span style="color:{TEXT_SUB};font-size:13px;font-weight:400;">n={n}</span>'
        if n is not None else ""
    )
    section_title(f"{text}{suffix}")


def parse_brands(cell) -> list:
    """top_brands 字串 → 依序的品牌清單（逗號切開、去空白；空值回傳空清單）"""
    if cell is None or (not isinstance(cell, str) and pd.isna(cell)):
        return []
    return [x.strip() for x in str(cell).split(",") if x.strip()]


def build_brand_rank_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    品牌排名表：把每個事件展開成多列。
    欄位：event_idx（DataFrame 的 index，GET 沒回傳事件 id 所以用它代替）、
          brand、best_rank（同品牌重複出現時取最小名次）、appear（出現次數）。
    """
    rows = []
    for idx, cell in df["top_brands"].items():
        seen = {}
        for pos, brand in enumerate(parse_brands(cell), start=1):
            if brand in seen:
                seen[brand][1] += 1
            else:
                seen[brand] = [pos, 1]
        for brand, (rank, times) in seen.items():
            rows.append((idx, brand, rank, times))
    return pd.DataFrame(rows, columns=["event_idx", "brand", "best_rank", "appear"])


def hit_event_index(rank_df: pd.DataFrame, brands) -> set:
    """命中事件：Top3 裡包含任一指定品牌的事件 index 集合"""
    if isinstance(brands, str):
        brands = [brands]
    return set(rank_df.loc[rank_df["brand"].isin(list(brands)), "event_idx"])


def brand_metrics(rank_df: pd.DataFrame, brand: str, n_base: int) -> dict:
    """
    單一品牌的份額指標。
      n_hit      Top3 命中事件數（去重）
      top1       Top1 事件數（最佳名次為 1）
      top3_rate  命中事件數 ÷ 有品牌資料的事件數 × 100
      top1_share Top1 事件數 ÷ 有品牌資料的事件數 × 100
    """
    sub = rank_df[rank_df["brand"] == brand]
    n_hit = int(sub["event_idx"].nunique())
    top1 = int((sub["best_rank"] == 1).sum())
    return {
        "n_hit": n_hit,
        "top1": top1,
        "top3_rate": (n_hit / n_base * 100) if n_base else float("nan"),
        "top1_share": (top1 / n_base * 100) if n_base else float("nan"),
    }


def top_cooccurring(rank_df: pd.DataFrame, brand: str, k: int = 3) -> list:
    """與本品牌同時進 Top3 次數最多的前 k 個品牌（競品組預設值）"""
    hit = hit_event_index(rank_df, brand)
    sub = rank_df[rank_df["event_idx"].isin(hit) & (rank_df["brand"] != brand)]
    if sub.empty:
        return []
    counts = sub.groupby("brand")["event_idx"].nunique().reset_index(name="n")
    counts = counts.sort_values(["n", "brand"], ascending=[False, True])
    return counts["brand"].head(k).tolist()


def duel_table(rank_df: pd.DataFrame, me: str, rivals: list) -> pd.DataFrame:
    """
    競品對戰（N6）：對每個競品 B，
      n    = 本品牌與 B 同時進 Top3 的事件數
      勝場 = 本品牌名次優於 B 的事件數（同事件同品牌重複出現已取最佳名次）
    """
    if rank_df.empty:
        return pd.DataFrame(columns=["競品", "同時出現次數", "本品牌勝場", "勝率"])
    pivot = rank_df.pivot(index="event_idx", columns="brand", values="best_rank")
    rows = []
    for rival in rivals:
        if me in pivot.columns and rival in pivot.columns:
            both = pivot[[me, rival]].dropna()
            n = len(both)
            wins = int((both[me] < both[rival]).sum())
        else:
            n, wins = 0, 0
        rows.append({
            "競品": rival,
            "同時出現次數": n,
            "本品牌勝場": wins,
            "勝率": (wins / n * 100) if n else float("nan"),
        })
    return pd.DataFrame(rows)


def audience_index(base_df: pd.DataFrame, hit_df: pd.DataFrame, column: str, min_n: int):
    """
    受眾輪廓指數（N3）＝ 命中事件中該類別占比 ÷ 全體該類別占比 × 100。
    100＝與整體相同，>100＝本品牌特別吸引該類別。
    回傳 (結果表, 被遮蔽的類別清單, 命中事件中此欄位有填的筆數)。
    類別樣本（命中事件數）低於門檻者不輸出數值。
    """
    base = base_df[column].astype(str).str.strip()
    base = base[base != ""]
    hit = hit_df[column].astype(str).str.strip()
    hit = hit[hit != ""]
    if base.empty or hit.empty:
        return pd.DataFrame(columns=["類別", "命中事件數", "本品牌占比", "全體占比", "指數"]), [], 0

    base_share = base.value_counts(normalize=True)
    hit_counts = hit.value_counts()
    hit_share = hit.value_counts(normalize=True)
    rows, masked = [], []
    for cat, n_cat in hit_counts.items():
        if n_cat < min_n or base_share.get(cat, 0) <= 0:
            masked.append(cat)
            continue
        rows.append({
            "類別": cat,
            "命中事件數": int(n_cat),
            "本品牌占比": round(hit_share[cat] * 100, 1),
            "全體占比": round(base_share[cat] * 100, 1),
            "指數": round(hit_share[cat] / base_share[cat] * 100, 0),
        })
    return pd.DataFrame(rows), masked, int(len(hit))


def group_share_table(groups: dict, column: str, items: list, min_n: int):
    """
    需求對照（N4）：每組事件中提到某項目（功能 / 情境）的比例。
    groups: {顯示名稱: 該組 DataFrame}；多選欄位占比不會加總成 100%。
    回傳 (長表, 因樣本不足而略過的組別)。
    """
    rows, skipped = [], []
    for label, gdf in groups.items():
        non_empty = gdf[column].astype(str).str.strip() != ""
        n_group = int(non_empty.sum())
        if n_group < min_n:
            skipped.append(label)
            continue
        counter = count_multi_value_column(gdf, column)
        for item in items:
            rows.append({
                "項目": item,
                "群組": f"{label}（n={n_group}）",
                "角色": label,
                "占比": counter.get(item, 0) / n_group * 100,
            })
    return pd.DataFrame(rows), skipped


def period_labels(dates: pd.Series, weekly: bool) -> pd.Series:
    """把事件日期轉成『週（週一起算）』或『日』的文字標籤，供趨勢圖分組"""
    day = dates.dt.normalize()
    if weekly:
        day = day - pd.to_timedelta(day.dt.weekday, unit="D")
    return day.dt.strftime("%Y-%m-%d")


# ============================================================
# 資料來源：假資料或後端1
# ============================================================
if USE_MOCK_DATA:
    events_df = pd.DataFrame(MOCK_EVENTS)
else:
    if not API_BASE:
        st.error("尚未設定後端網址：請在 .streamlit/secrets.toml 加上 api_base = \"https://你的ngrok網址\"")
        st.stop()
    try:
        raw_events = fetch_json(f"{API_BASE}/analytics/events")
        if isinstance(raw_events, dict):  # 容錯：後端若包了一層 {"events": [...]}
            raw_events = raw_events.get("events", raw_events.get("data", []))
        events_df = pd.DataFrame(raw_events)
    except requests.HTTPError as exc:
        st.error(f"後端回應狀態碼異常：{exc.response.status_code}")
        st.code(exc.response.text[:1000])  # 印出前1000字，看實際回了什麼
        st.stop()
    except requests.RequestException as exc:
        st.error("無法連線到後端1，請確認 ngrok 網址（secrets.toml 的 api_base）是否仍有效")
        st.code(str(exc)[:500])
        st.stop()
    except ValueError:
        st.error("後端回應的不是 JSON 格式")
        st.stop()

# ============================================================
# 合作品牌名單：跟事件資料用同一個 USE_MOCK_DATA 開關，行為保持一致
# ------------------------------------------------------------
# 真實模式下即時打後端1的 /sponsors，資料庫新增 / 刪除合作品牌時，
# 金色標示與贊助曝光占比會馬上反映，不用重開 dashboard。
# ============================================================
if not USE_MOCK_DATA:
    try:
        SPONSORED_BRANDS = [
            s["brand_name"]
            for s in fetch_json(f"{API_BASE}/sponsors").get("sponsors", [])
        ]
    except Exception:
        # 抓不到的話，退回 mock_data.py 裡寫死的清單，至少畫面不會壞掉
        st.warning("無法取得最新合作品牌名單，暫時顯示預設清單")

# 資料表目前完全沒有任何事件時，不要讓後面的程式碼直接 KeyError
if events_df.empty:
    st.markdown(
        '<div class="empty-state">📭　資料庫目前還沒有任何推薦事件紀錄，'
        '請確認資料庫 /analytics/events 是否已收到 POST 請求（可能是後端2尚未成功寫入）</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# 資料清理（欄位補齊、缺值、正規化）
# ============================================================
# 後端若少回某個欄位（例如舊版沒有 occupation），先補空欄位，避免後面 KeyError
for _col in ["source", "age_range", "occupation", "usage_scope", "device_type", "usage",
             "features", "os", "brand_preference", "top_brands", "top_platforms"]:
    if _col not in events_df.columns:
        events_df[_col] = ""
for _col in ["budget_min", "budget_max", "product_count"]:
    if _col not in events_df.columns:
        events_df[_col] = float("nan")

events_df = events_df.reset_index(drop=True)  # index 當作事件識別（GET 沒有回傳事件 id）
events_df["created_at"] = pd.to_datetime(events_df["created_at"], errors="coerce")
events_df = events_df.dropna(subset=["created_at"]).reset_index(drop=True)
if events_df.empty:
    notice("📭　事件資料的 created_at 格式無法解析")
    st.stop()

# 所有文字欄位的缺值補空字串，避免變成假分類 "nan" / "None"
for _col in ["source", "age_range", "occupation", "usage_scope", "device_type", "usage",
             "features", "os", "top_brands", "top_platforms"]:
    events_df[_col] = events_df[_col].fillna("").astype(str).str.strip()

# budget_min/budget_max 換算成跟問卷一致的級距文字（E28 缺值修正）
events_df["budget_min"] = pd.to_numeric(events_df["budget_min"], errors="coerce")
events_df["budget_max"] = pd.to_numeric(events_df["budget_max"], errors="coerce")
events_df["product_count"] = pd.to_numeric(events_df["product_count"], errors="coerce")
events_df["budget_bucket"] = pd.cut(
    events_df[["budget_min", "budget_max"]].mean(axis=1),
    bins=[-1, 5000, 15000, 30000, float("inf")],
    labels=BUDGET_OPTIONS,
).astype(object)
# 兩欄都缺值 → mean 是 NaN → 轉成空字串（而不是字串 "nan"）
events_df["budget_bucket"] = events_df["budget_bucket"].where(events_df["budget_bucket"].notna(), "")
# 「跳過預算題」（min=0 且 max=999999）不能被誤判成「30,000以上」，獨立標成空字串
skipped_budget = (events_df["budget_min"] == 0) & (events_df["budget_max"] == 999999)
events_df.loc[skipped_budget, "budget_bucket"] = ""

# 使用情境 / 裝置類型 正規化，統一對應回問卷的分類文字，
# 這樣不管資料是問卷送的還是 AI 聊天室送的，圖表都會歸到同一類
events_df["usage"] = events_df["usage"].apply(normalize_usage_column)
events_df["device_type"] = events_df["device_type"].apply(
    lambda v: normalize_device_label(v) if v else ""
)

# 職業（自由輸入）歸類；保留原始寫法供資料品質檢查使用
events_df["occupation_raw"] = events_df["occupation"]
events_df["occupation"] = events_df["occupation"].apply(normalize_occupation_label)

# 品牌名稱正規化（Q1）：保留原始寫法供資料品質檢查，再換成標準名稱
events_df["top_brands_raw"] = events_df["top_brands"]
brand_mapping, brand_method, brand_raw_counts = build_brand_mapping(events_df["top_brands_raw"])
events_df["top_brands"] = events_df["top_brands"].apply(lambda c: apply_brand_mapping(c, brand_mapping))

# 合作品牌名單用同一套規則正規化
SPONSORED_BRANDS = [normalize_sponsor_name(b, brand_mapping) for b in SPONSORED_BRANDS]
sponsored_set = set(SPONSORED_BRANDS)

data_min_date = events_df["created_at"].min().date()
data_max_date = events_df["created_at"].max().date()

# ------------------------------------------------------------
# 品牌清單：從「全部事件」自動產生（不是寫死的名單）
# ------------------------------------------------------------
# 只要推薦結果裡出現新品牌，下次載入 / 按重新整理就會自動出現在側邊欄；
# 後端 /sponsors 新增的合作品牌即使還沒有任何事件，也會自動列入。
# 排序＝出現次數多到少。
rank_all = build_brand_rank_df(events_df)
if rank_all.empty:
    brand_totals = pd.Series(dtype=int)
    brand_first_seen = {}
else:
    brand_totals = rank_all.groupby("brand")["event_idx"].nunique().sort_values(ascending=False)
    _seen = rank_all.merge(
        events_df[["created_at"]], left_on="event_idx", right_index=True
    ).groupby("brand")["created_at"].min()
    brand_first_seen = {b: d.date() for b, d in _seen.items()}

brand_list = list(brand_totals.index)
for _b in SPONSORED_BRANDS:  # 合作品牌即使目前沒有事件，也要能被選到
    if _b and _b not in brand_list:
        brand_list.append(_b)

# 🆕 新品牌：第一次出現在資料最後 NEW_BRAND_DAYS 天內（且資料本身早於這段期間開始）
_new_cutoff = data_max_date - timedelta(days=NEW_BRAND_DAYS - 1)
new_brands = [
    b for b in brand_list
    if b in brand_first_seen and brand_first_seen[b] >= _new_cutoff and data_min_date < _new_cutoff
]


def format_brand(name: str) -> str:
    """下拉選單顯示：合作品牌前加 ★、新偵測到的品牌後加 🆕"""
    if name == ALL_BRANDS:
        return name
    return f"{'★ ' if name in sponsored_set else ''}{name}{' 🆕' if name in new_brands else ''}"


# ============================================================
# 側邊欄：篩選條件（會真正影響下面所有統計）與說明
# ============================================================
with st.sidebar:
    st.markdown("### ⌚ WearWise")
    st.caption("合作廠商 × 使用者偏好　數據後台")
    st.divider()

    st.markdown("**事件來源**")
    source_options = sorted([s for s in events_df["source"].unique().tolist() if s])
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

    # 先算出套用來源 / 日期後的資料，競品組預設值（同時出現最多）要用它來算
    filtered_df = events_df[
        (events_df["source"].isin(selected_sources))
        & (events_df["created_at"].dt.date >= start_date)
        & (events_df["created_at"].dt.date <= end_date)
    ]
    rank_df = build_brand_rank_df(filtered_df)

    st.divider()
    st.markdown("**我的品牌**")
    brand_choices = [ALL_BRANDS] + brand_list
    # 重新整理後若原本選的品牌已不存在，退回「全部品牌」，避免 selectbox 報錯
    if st.session_state.get("sel_my_brand") not in brand_choices + [None]:
        st.session_state["sel_my_brand"] = ALL_BRANDS
    my_choice = st.selectbox(
        "我的品牌", options=brand_choices, format_func=format_brand, key="sel_my_brand",
        label_visibility="collapsed",
        help="品牌清單由資料自動產生：推薦結果只要出現新品牌（或後台新增合作品牌），"
             "重新整理後就會自動出現在這裡，不需要手動新增。★＝合作品牌　🆕＝近期新出現。",
    )
    my_brand = None if my_choice == ALL_BRANDS else my_choice
    if new_brands:
        st.caption(f"🆕 近 {NEW_BRAND_DAYS} 天新偵測到的品牌已自動加入：{'、'.join(new_brands)}")

    rivals = []
    if my_brand:
        st.markdown("**競品組**")
        rival_options = [b for b in brand_list if b != my_brand]
        rival_key = f"sel_rivals__{my_brand}"  # 換品牌就換 key，預設值會重新計算
        if rival_key not in st.session_state:
            st.session_state[rival_key] = [
                b for b in top_cooccurring(rank_df, my_brand) if b in rival_options
            ]
        else:  # 已不存在的品牌從已選清單剔除
            st.session_state[rival_key] = [b for b in st.session_state[rival_key] if b in rival_options]
        rivals = st.multiselect(
            "競品組", options=rival_options, format_func=format_brand, key=rival_key,
            label_visibility="collapsed",
            help="預設為與本品牌同時進推薦前3名次數最多的品牌，可自行增減。",
        )

    st.markdown("**最小樣本數**")
    min_n = int(st.number_input(
        "最小樣本數", min_value=1, max_value=500, value=5, step=1, label_visibility="collapsed",
        help="分組樣本數低於此門檻時顯示「樣本不足」、不畫數字（同時是去識別化做法）。"
             "展示用預設 5，對外報告建議 30。",
    ))

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
# 頁首
# ============================================================
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    # 標題 + 模式標籤（品牌模式：XXX／品類模式）
    mode_html = (f'<span class="mode">品牌模式：{esc(my_brand)}</span>' if my_brand
                 else '<span class="mode cat">品類模式：全部品牌</span>')
    html_out('<div class="head"><div><h1>WearWise 數據儀表板</h1>'
             '<div class="sub">匿名化使用者偏好統計報告（購買前意圖數據）</div></div>' + mode_html + '</div>')
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 重新整理資料", use_container_width=True):
        st.cache_data.clear()  # 清掉 API 快取，下一輪重新向後端抓最新事件與合作品牌
        st.rerun()

st.write("")

# ------------------------------------------------------------
# 篩選後沒有任何資料：顯示空狀態，不要讓圖表區塊直接報錯或空白一片
# ------------------------------------------------------------
if filtered_df.empty:
    notice("📭　所選的時間範圍或事件來源內沒有資料，請調整左側篩選條件")
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
occupation_counter = count_single_value_column(filtered_df, "occupation")
usage_scope_counter = count_single_value_column(filtered_df, "usage_scope", drop_empty=True)
platform_counter = count_multi_value_column(filtered_df, "top_platforms")

df_trend = (
    filtered_df.groupby(filtered_df["created_at"].dt.date)
    .size()
    .reset_index(name="count")
    .rename(columns={"created_at": "date"})
)

# 品牌排名資料（rank_df 已在側邊欄算好）；n_base＝有品牌資料的事件數＝份額的分母
n_base = int(rank_df["event_idx"].nunique()) if not rank_df.empty else 0
brand_event_counts = (
    rank_df.groupby("brand")["event_idx"].nunique().sort_values(ascending=False)
    if not rank_df.empty else pd.Series(dtype=int)
)
total_brand_appear = int(brand_event_counts.sum())
sponsored_exposure = int(sum(v for k, v in brand_event_counts.items() if k in sponsored_set))
sponsored_ratio = (sponsored_exposure / total_brand_appear * 100) if total_brand_appear else 0

top_usage = usage_counter.most_common(1)[0][0] if usage_counter else "—"
top_feature = feature_counter.most_common(1)[0][0] if feature_counter else "—"
top_brand = brand_event_counts.index[0] if len(brand_event_counts) else "—"
top_device = device_counter.most_common(1)[0][0] if device_counter else "—"

# 品牌模式的核心數字
my_metrics, rival_metrics, hit_idx, my_df = None, {}, set(), filtered_df.iloc[0:0]
if my_brand:
    my_metrics = brand_metrics(rank_df, my_brand, n_base)
    hit_idx = hit_event_index(rank_df, my_brand)
    my_df = filtered_df.loc[filtered_df.index.isin(hit_idx)]
    rival_metrics = {r: brand_metrics(rank_df, r, n_base) for r in rivals}

brand_ready = bool(my_brand) and my_metrics["n_hit"] >= min_n if my_brand else False

# ============================================================
# KPI 總覽列（HTML 一排四卡；窄螢幕自動變兩欄 / 一欄）
# ------------------------------------------------------------
# 這一段只改「呈現」：數字全部沿用上面已算好的 filtered_df / my_metrics /
# rival_metrics，沒有任何重算。
# ============================================================
def kpi_item(label: str, value: str, sub: str = "", tone: str = "") -> str:
    """單張 KPI 卡的 HTML。tone：up（綠）/ down（紅）/ warn（金）/ 空字串（灰）"""
    return (
        f'<div class="kpi"><div class="l">{esc(label)}</div>'
        f'<div class="v">{esc(value)}</div><div class="s {tone}">{esc(sub)}</div></div>'
    )


kpi_items = [kpi_item("篩選後事件數", f"{len(filtered_df)}", f"共 {len(events_df)} 筆資料中")]
if not my_brand:  # ---- 品類模式 ----
    kpi_items.append(kpi_item("熱門使用情境", top_usage.split("（")[0], f"{usage_counter[top_usage]} 次提及"))
    kpi_items.append(kpi_item("最關注的功能需求", top_feature, f"{feature_counter[top_feature]} 次提及"))
    kpi_items.append(kpi_item(
        "曝光最高品牌", top_brand,
        f"{int(brand_event_counts.iloc[0])} 個事件進前3名" if len(brand_event_counts) else "",
    ))
else:  # ---- 品牌模式 ----
    if brand_ready:
        kpi_items.append(kpi_item(f"{my_brand} Top1 份額", f"{my_metrics['top1_share']:.1f}%",
                                  f"{my_metrics['top1']} / {n_base} 個事件　含贊助加權"))
        kpi_items.append(kpi_item(f"{my_brand} Top3 出現率", f"{my_metrics['top3_rate']:.1f}%",
                                  f"{my_metrics['n_hit']} / {n_base} 個事件　含贊助加權"))
        valid_rivals = [m["top3_rate"] for m in rival_metrics.values() if m["n_hit"] >= min_n]
        if valid_rivals:
            rival_avg = sum(valid_rivals) / len(valid_rivals)
            diff = my_metrics["top3_rate"] - rival_avg
            kpi_items.append(kpi_item("與競品組平均的差距", f"{diff:+.1f} 個百分點",
                                      f"競品組平均 Top3 出現率 {rival_avg:.1f}%",
                                      tone="up" if diff >= 0 else "down"))
        else:
            kpi_items.append(kpi_item("與競品組平均的差距", "—", "請在側邊欄選擇樣本足夠的競品"))
    else:
        for _label in ["Top1 份額", "Top3 出現率", "與競品組平均的差距"]:
            kpi_items.append(kpi_item(f"{my_brand} {_label}", "樣本不足",
                                      f"n={my_metrics['n_hit']}，低於門檻 {min_n}", tone="warn"))
html_out('<section class="kpis">' + "".join(kpi_items) + '</section>')

# ============================================================
# 文字洞察摘要（依模式產生；所有來自資料的字串先 html.escape）
# ============================================================
scope_text = f"{start_date} ～ {end_date}，來源：{'、'.join(selected_sources)}"
if not my_brand:
    insight_text = f"""
    在目前篩選範圍（{esc(scope_text)}）中，使用者最主要的使用情境是 <b>{esc(top_usage)}</b>，
    最關注的功能需求是 <b>{esc(top_feature)}</b>，裝置偏好以 <b>{esc(top_device)}</b> 為主；
    推薦結果前3名中，合作品牌（{ esc("、".join(sorted(sponsored_set)) or "無") }）合計占 <b>{sponsored_ratio:.1f}%</b>，
    <b>{esc(top_brand)}</b> 是曝光（進前3名事件數）最高的品牌。
    <br>👉 在左側「我的品牌」選一個品牌，可以看它對比競品的份額、受眾與勝率。
    """
elif not brand_ready:
    insight_text = f"""
    在目前篩選範圍（{esc(scope_text)}）中，<b>{esc(my_brand)}</b> 只進入 <b>{my_metrics['n_hit']}</b> 個事件的前3名，
    低於最小樣本數 {min_n}，為避免小樣本誤導與個資回推風險，暫不輸出份額數字。
    可放寬日期 / 來源篩選，或調低左側「最小樣本數」。
    """
else:
    # 主要受眾：命中事件中最多的年齡層與職業（需達樣本門檻）
    def _mode_text(column):
        s = my_df[column].astype(str).str.strip()
        s = s[s != ""]
        if s.empty or s.value_counts().iloc[0] < min_n:
            return None
        return s.value_counts().index[0]

    _age, _occ = _mode_text("age_range"), _mode_text("occupation")
    audience_text = "、".join([x for x in [_age, _occ] if x]) or "（樣本不足以判斷）"
    if rival_metrics and any(m["n_hit"] >= min_n for m in rival_metrics.values()):
        _vals = [m["top3_rate"] for m in rival_metrics.values() if m["n_hit"] >= min_n]
        _avg = sum(_vals) / len(_vals)
        _gap = my_metrics["top3_rate"] - _avg
        gap_text = (
            f"與競品組平均（{_avg:.1f}%）相比，{'領先' if _gap >= 0 else '落後'} "
            f"<b>{abs(_gap):.1f}</b> 個百分點"
        )
    else:
        gap_text = "尚未選擇樣本足夠的競品組，無法比較差距"
    sponsor_text = "（合作品牌，排名含贊助加權）" if my_brand in sponsored_set else ""
    insight_text = f"""
    在目前篩選範圍（{esc(scope_text)}）中，<b>{esc(my_brand)}</b>{sponsor_text}的 Top1 份額為
    <b>{my_metrics['top1_share']:.1f}%</b>、Top3 出現率為 <b>{my_metrics['top3_rate']:.1f}%</b>；
    {gap_text}。被推薦到 {esc(my_brand)} 的使用者以 <b>{esc(audience_text)}</b> 居多。
    """
html_out(f'<div class="insight">💡 {" ".join(insight_text.split())}</div>')

# ============================================================
# 分頁籤（贊助成效頁只有「選了合作品牌」時才出現）
# ============================================================
show_sponsor_tab = bool(my_brand) and my_brand in sponsored_set
tab_labels = ["品牌總覽", "受眾與需求", "競品對戰"]
if show_sponsor_tab:
    tab_labels.append("贊助成效")
tab_labels.append("品類總覽")
tabs = st.tabs(tab_labels)
tab_overview, tab_audience, tab_duel = tabs[0], tabs[1], tabs[2]
tab_sponsor = tabs[3] if show_sponsor_tab else None
tab_category = tabs[-1]

NEED_BRAND_HINT = "請先在左側「我的品牌」選一個品牌，這一頁才會有內容。<br>（目前選的是「全部品牌」，也就是品類總覽。）"

# ------------------------------------------------------------
# T1：品牌總覽（品類品牌排行 + 推薦份額 + 份額趨勢）
# ------------------------------------------------------------
with tab_overview:
    # ---- 品類品牌排行（E19 改造）----
    if rank_df.empty:
        html_out(sec_card("品類品牌排行", hint_box("目前篩選範圍內沒有任何品牌資料"), f"n={n_base}"))
    else:
        rank_tbl = (
            rank_df.groupby("brand")
            .agg(top3=("event_idx", "nunique"), top1=("best_rank", lambda s: int((s == 1).sum())))
            .reset_index()
            .rename(columns={"brand": "品牌", "top3": "Top3 事件數", "top1": "Top1 次數"})
            .sort_values(["Top3 事件數", "Top1 次數"], ascending=False)
            .reset_index(drop=True)
        )
        rank_tbl["類型"] = rank_tbl["品牌"].apply(
            lambda b: "本品牌" if b == my_brand else ("合作品牌" if b in sponsored_set else "一般品牌")
        )
        rank_tbl["Top3 出現率(%)"] = (rank_tbl["Top3 事件數"] / n_base * 100).round(1)
        rank_tbl["Top1 份額(%)"] = (rank_tbl["Top1 次數"] / n_base * 100).round(1)
        max_rate = max(float(rank_tbl["Top3 出現率(%)"].max()), 0.1)  # 最長的條＝最高的 Top3 出現率

        rank_rows = []
        for _, r in rank_tbl.iterrows():
            b = r["品牌"]
            if r["Top3 事件數"] < min_n:  # 樣本不足：只顯示遮蔽文字，不畫數字
                rank_rows.append(mask_row(("★ " if b in sponsored_set else "") + b, int(r["Top3 事件數"]), min_n))
                continue
            gold = "gold" if b in sponsored_set else ""
            rank_rows.append(
                f'<div class="row"><div class="lb{" sel" if b == my_brand else ""}">'
                f'{esc(("★ " if b in sponsored_set else "") + b)}</div>'
                f'<div><div class="track"><div class="fill {gold}" style="width:{r["Top3 出現率(%)"] / max_rate * 100:.1f}%"></div></div>'
                f'<div class="track thin" style="margin-top:3px"><div class="fill {gold} soft" '
                f'style="width:{r["Top1 份額(%)"] / max_rate * 100:.1f}%"></div></div></div>'
                f'<div class="vl wide">Top3 {r["Top3 出現率(%)"]:.1f}%（{int(r["Top3 事件數"])}）<br>'
                f'Top1 {r["Top1 份額(%)"]:.1f}%（{int(r["Top1 次數"])}）</div></div>'
            )
        html_out(sec_card(
            "品類品牌排行",
            rows_block(rank_rows) + '<p class="foot">排名含贊助加權。括號內是事件數；同一事件內同品牌只算一次。</p>',
            f"n={n_base}",
            "<b>怎麼讀：</b>粗條是「出現在前 3 名的事件比例」，細條是「排第一的比例」（兩者用同一把尺）。"
            "金色是合作品牌，藍字是你選的品牌，樣本不足的品牌不畫數字。",
        ))
        with st.expander("查看原始統計數字"):
            st.dataframe(rank_tbl, use_container_width=True, hide_index=True)

    # ---- 推薦份額（N2）----
    if not my_brand:
        html_out(sec_card("推薦份額與趨勢", hint_box(NEED_BRAND_HINT)))
    elif not brand_ready:
        html_out(sec_card("推薦份額與趨勢", hint_box(
            f"{esc(my_brand)} 的樣本不足（n={my_metrics['n_hit']}，低於門檻 {min_n}），暫不顯示份額")))
    else:
        all_metrics = [brand_metrics(rank_df, b, n_base) for b in brand_event_counts.index]
        cat_top1 = sum(m["top1_share"] for m in all_metrics) / len(all_metrics)
        cat_top3 = sum(m["top3_rate"] for m in all_metrics) / len(all_metrics)
        ok_rivals = {r: m for r, m in rival_metrics.items() if m["n_hit"] >= min_n}
        rows = [
            {"群組": "本品牌", "指標": "Top1 份額", "百分比": my_metrics["top1_share"]},
            {"群組": "本品牌", "指標": "Top3 出現率", "百分比": my_metrics["top3_rate"]},
            {"群組": "品類平均", "指標": "Top1 份額", "百分比": cat_top1},
            {"群組": "品類平均", "指標": "Top3 出現率", "百分比": cat_top3},
        ]
        if ok_rivals:
            rows += [
                {"群組": "競品組", "指標": "Top1 份額",
                 "百分比": sum(m["top1_share"] for m in ok_rivals.values()) / len(ok_rivals)},
                {"群組": "競品組", "指標": "Top3 出現率",
                 "百分比": sum(m["top3_rate"] for m in ok_rivals.values()) / len(ok_rivals)},
            ]
        df_share = pd.DataFrame(rows)
        share_scale = max(float(df_share["百分比"].max()), 0.1)
        cls_of = {"本品牌": "", "競品組": "comp", "品類平均": "all"}
        share_blocks = ""
        for metric in ["Top1 份額", "Top3 出現率"]:
            lines = [
                (g, cls_of[g], float(df_share[(df_share["群組"] == g) & (df_share["指標"] == metric)]["百分比"].iloc[0]))
                for g in ["本品牌", "競品組", "品類平均"] if g in set(df_share["群組"])
            ]
            share_blocks += '<div class="gwrap">' + grouped_block(
                esc(metric), [(g, c, v / share_scale, f"{v:.1f}%") for g, c, v in lines]) + '</div>'
        share_note = ""
        if not rivals:
            share_note = '<p class="foot">尚未選擇競品組，圖中只有本品牌與品類平均。</p>'
        elif len(ok_rivals) < len(rivals):
            share_note = (f'<p class="foot">樣本不足未納入競品組平均：'
                          f'{esc("、".join(r for r in rivals if r not in ok_rivals))}</p>')
        html_out(sec_card(
            f"推薦份額：{my_brand} vs 競品組 vs 品類平均",
            key_html([("本品牌", "var(--accent)"), ("競品組", "var(--bar-comp)"), ("品類平均", "var(--bar-all)")])
            + f'<div class="cols">{share_blocks}</div>' + share_note,
            f"n={n_base}",
            "<b>怎麼讀：</b>三條一組。本品牌比另外兩條長，代表在推薦裡比對手更常被選中。"
            "Top1 是第一名占比，Top3 是進前三名的占比。排名含贊助加權。",
        ))

        # 本品牌 + 競品逐一列出（小樣本顯示『樣本不足』）
        detail_rows = []
        for b in [my_brand] + rivals:
            m = brand_metrics(rank_df, b, n_base)
            enough = m["n_hit"] >= min_n
            detail_rows.append({
                "品牌": b, "類型": "合作品牌" if b in sponsored_set else "一般品牌",
                "Top3 命中事件數 n": m["n_hit"],
                "Top1 份額": f"{m['top1_share']:.1f}%" if enough else "樣本不足",
                "Top3 出現率": f"{m['top3_rate']:.1f}%" if enough else "樣本不足",
            })
        with st.expander("查看原始統計數字"):
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)
            st.dataframe(df_share, use_container_width=True, hide_index=True)

        # ---- 份額趨勢 ----
        span_days = (filtered_df["created_at"].max() - filtered_df["created_at"].min()).days + 1
        weekly = span_days >= 14  # 資料不足 2 週時改用日
        unit = "週" if weekly else "日"
        period = period_labels(filtered_df["created_at"], weekly)
        period_of = period.to_dict()
        rank_p = rank_df.assign(period=rank_df["event_idx"].map(period_of))
        base_by_p = rank_p.groupby("period")["event_idx"].nunique()
        me_p = rank_p[rank_p["brand"] == my_brand]
        top3_by_p = me_p.groupby("period")["event_idx"].nunique()
        top1_by_p = me_p[me_p["best_rank"] == 1].groupby("period")["event_idx"].nunique()
        trend_rows, plot_rows, small_periods = [], [], []
        for p, base in base_by_p.sort_index().items():
            if base < min_n:
                small_periods.append(p)
                plot_rows.append({"期間": p, "n": int(base)})  # 其餘欄位留空 → 圖上在這個時段斷線
                continue
            row = {"期間": p, "n": int(base),
                   "本品牌 Top3 出現率": top3_by_p.get(p, 0) / base * 100,
                   "本品牌 Top1 份額": top1_by_p.get(p, 0) / base * 100}
            if ok_rivals:
                rivals_hit = [rank_p[(rank_p["brand"] == r) & (rank_p["period"] == p)]["event_idx"].nunique()
                              for r in ok_rivals]
                row["競品組平均 Top3 出現率"] = sum(h / base * 100 for h in rivals_hit) / len(rivals_hit)
            trend_rows.append(row)
            plot_rows.append(row)
        df_tr = pd.DataFrame(trend_rows)
        df_plot = pd.DataFrame(plot_rows)
        trend_how = (
            "<b>怎麼讀：</b>藍實線是本品牌 Top3 出現率，淺藍線是 Top1 份額，灰虛線是競品組平均。"
            f"斷掉的地方是該時段樣本數低於左側的「最小樣本數」。資料不足 2 週時改用日。排名含贊助加權。"
        )
        if df_tr.empty:
            html_out(sec_card("份額趨勢", hint_box(f"每個{unit}的事件數都低於最小樣本數 {min_n}，無法畫趨勢"),
                              f"n={n_base}", trend_how))
        else:
            html_out(sec_card(f"份額趨勢（以{unit}為單位）", "", f"n={n_base}", trend_how, open_=True))
            series_cols = [c for c in ["本品牌 Top3 出現率", "本品牌 Top1 份額", "競品組平均 Top3 出現率"]
                           if c in df_plot.columns]
            # 配色與線型對齊預覽：本品牌藍實線、競品組平均灰虛線
            series_style = {
                "本品牌 Top3 出現率": dict(color=COLOR_ME, width=2.6, dash="solid"),
                "本品牌 Top1 份額": dict(color=BLUE_LIGHT, width=2, dash="solid"),
                "競品組平均 Top3 出現率": dict(color=COLOR_RIVAL, width=2, dash="dash"),
            }
            fig = go.Figure()
            for col in series_cols:
                if len(df_tr) >= 2:  # 折線至少要 2 個資料點
                    fig.add_trace(go.Scatter(
                        x=df_plot["期間"], y=df_plot[col], name=col, mode="lines+markers",
                        connectgaps=False,  # 樣本不足的時段斷線
                        line=series_style[col],
                        hovertemplate="%{x}<br>%{y:.1f}%<extra>" + col + "</extra>",
                    ))
                else:  # 只有 1 個期間 → 改用長條圖（教訓：單點資料畫不出線 / 面積圖）
                    fig.add_trace(go.Bar(
                        x=df_plot["期間"], y=df_plot[col], name=col, marker_color=series_style[col]["color"],
                        hovertemplate="%{x}<br>%{y:.1f}%<extra>" + col + "</extra>",
                    ))
            fig.update_xaxes(type="category")
            fig.update_layout(yaxis_title="百分比（%）", xaxis_title="", barmode="group")
            show_chart(fig, "t1_share_trend", 340, card=True)
            st.caption(
                f"每個{unit}的分母＝當{unit}有品牌資料的事件數。"
                + (f"事件數低於 {min_n} 的{unit}未顯示：{'、'.join(small_periods)}" if small_periods else "")
            )
            with st.expander("查看原始統計數字"):
                st.dataframe(df_tr.round(1), use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# T2：受眾與需求（N3 受眾指數 / N4 需求對照 / N5 預算落點 / N8 來源對照）
# ------------------------------------------------------------
with tab_audience:
    if not my_brand:
        html_out(sec_card("受眾與需求", hint_box(NEED_BRAND_HINT)))
    elif not brand_ready:
        html_out(sec_card("受眾與需求", hint_box(
            f"{esc(my_brand)} 的樣本不足（n={my_metrics['n_hit']}，低於門檻 {min_n}），暫不顯示受眾與需求分析")))
    else:
        # ---- N3 受眾輪廓指數 ----
        age_order = ["18 歲以下", "19–25 歲", "26–35 歲", "36–45 歲", "46–55 歲", "56 歲以上"]
        audience_dims = [
            ("age_range", "年齡層"), ("occupation", "職業"), ("usage_scope", "使用情境定位"),
            ("os", "作業系統"), ("device_type", "裝置類型"),
        ]
        dim_blocks, raw_tables = "", []
        for col_name, label in audience_dims:
            df_idx, masked, n_filled = audience_index(filtered_df, my_df, col_name, min_n)
            rows_html = []
            if not df_idx.empty:
                if col_name == "age_range":
                    df_idx["類別"] = pd.Categorical(df_idx["類別"], categories=age_order, ordered=True)
                    df_idx = df_idx.sort_values("類別")
                else:
                    df_idx = df_idx.sort_values("指數", ascending=False)
                for _, r in df_idx.iterrows():
                    cls = "up" if r["指數"] >= 120 else ("low" if r["指數"] <= 80 else "mid")
                    rows_html.append(
                        f'<div class="row"><div class="lb">{esc(r["類別"])}</div>'
                        f'<div class="track"><div class="fill {cls}" style="width:{min(100.0, r["指數"] / 250 * 100):.1f}%"></div>'
                        f'<div class="mark" style="left:40%"></div></div>'
                        f'<div class="vl">{r["指數"]:.0f}（n={int(r["命中事件數"])}）</div></div>'
                    )
                raw_tables.append((label, df_idx))
            if masked:  # 樣本不足的類別：顯示遮蔽文字（n 為該類別在命中事件中的人數）
                masked_counts = my_df[col_name].astype(str).str.strip().value_counts()
                rows_html += [mask_row(str(m), int(masked_counts.get(m, 0)), min_n) for m in masked]
            if not rows_html:
                rows_html = ['<p class="mask">樣本不足，無法計算指數</p>']
            dim_blocks += (
                f'<div><h3 class="sub-h">{esc(label)}<span class="n-inline">n={n_filled}</span></h3>'
                f'{rows_block(rows_html) if rows_html[0].startswith("<div") else rows_html[0]}</div>'
            )
        html_out(sec_card(
            f"{my_brand} 的受眾輪廓指數", f'<div class="cols">{dim_blocks}</div>', f"命中事件 n={my_metrics['n_hit']}",
            "<b>怎麼讀：</b>虛線是 100，代表和整體一樣。藍色條超過 120 表示這群人特別會被推薦到本品牌；"
            "灰色（80 以下）表示較少。空白填答不計入，樣本不足的類別不顯示。排名含贊助加權。",
        ))
        with st.expander("查看原始統計數字"):
            for label, tbl in raw_tables:
                st.markdown(f"**{label}**")
                st.dataframe(tbl, use_container_width=True, hide_index=True)

        # ---- N4 功能與情境需求對照 ----
        rival_hit_idx = hit_event_index(rank_df, rivals) if rivals else set()
        rival_df = filtered_df.loc[filtered_df.index.isin(rival_hit_idx)]
        groups = {my_brand: my_df}
        if rivals:
            groups["競品組"] = rival_df
        groups["全體"] = filtered_df
        role_of = {my_brand: "本品牌"}

        need_blocks, need_tables, need_notes = "", [], []
        need_scale = 0.05
        need_data = []
        for col_name, label, top_k in [("features", "功能需求", 8), ("usage", "使用情境", 5)]:
            counter_all = count_multi_value_column(filtered_df, col_name)
            items = [k for k, _ in counter_all.most_common(top_k)]
            df_long, skipped = group_share_table(groups, col_name, items, min_n)
            need_data.append((col_name, label, top_k, items, df_long, skipped))
            if not df_long.empty:
                need_scale = max(need_scale, float(df_long["占比"].max()) / 100)
        for col_name, label, top_k, items, df_long, skipped in need_data:
            if df_long.empty:
                need_blocks += f'<div><h3 class="sub-h">{esc(label)}</h3>{hint_box("樣本不足，無法比較")}</div>'
            else:
                df_long["角色"] = df_long["角色"].map(lambda r: role_of.get(r, r))
                grp_html = ""
                for item in items:
                    lines = []
                    for role, cls in [("本品牌", ""), ("競品組", "comp"), ("全體", "all")]:
                        hit_rows = df_long[(df_long["項目"] == item) & (df_long["角色"] == role)]
                        if not hit_rows.empty:
                            v = float(hit_rows["占比"].iloc[0]) / 100
                            lines.append((role, cls, v / need_scale, f"{v * 100:.0f}%"))
                    grp_html += grouped_block(esc(item), lines)
                need_blocks += f'<div><h3 class="sub-h">{esc(label)}（全體前 {top_k} 名）</h3><div class="gwrap">{grp_html}</div></div>'
                need_tables.append(df_long.drop(columns=["角色"]).round(1))
            if skipped:
                need_notes.append(f"{label}樣本不足未顯示：{'、'.join(skipped)}")
        n_text = f"本品牌 n={my_metrics['n_hit']}"
        group_ns = []
        for gname, gdf in groups.items():
            group_ns.append(f"{role_of.get(gname, gname)} n={len(gdf)}")
        html_out(sec_card(
            "功能與情境需求對照",
            key_html([("本品牌", "var(--accent)"), ("競品組", "var(--bar-comp)"), ("全體", "var(--bar-all)")])
            + f'<div class="cols">{need_blocks}</div>'
            + f'<p class="foot">各組事件數：{esc("　".join(group_ns))}。多選題，占比不會加總成 100%；競品組＝任一競品進前3名的事件。'
            + (esc(" " + "；".join(need_notes)) if need_notes else "") + '</p>',
            n_text,
            "<b>怎麼讀：</b>每個功能有三條：被推薦到本品牌的人、被推薦到競品的人、全體使用者，各有多少比例提到它。"
            "藍條明顯比灰條長，代表那是本品牌的強項需求。",
        ))
        if need_tables:
            with st.expander("查看原始統計數字"):
                for tbl in need_tables:
                    st.dataframe(tbl, use_container_width=True, hide_index=True)

        # ---- N5 預算帶落點 ----
        hit_budget = my_df["budget_bucket"].astype(str)
        hit_budget = hit_budget[hit_budget != ""]
        all_budget = filtered_df["budget_bucket"].astype(str)
        all_budget = all_budget[all_budget != ""]
        budget_how = ("<b>怎麼讀：</b>看本品牌被推薦時，使用者的預算落在哪裡。標「機會區間」表示全體很多人在這個價格帶，"
                      "但本品牌很少被推薦。⚠️ 這是「被推薦時使用者填的預算」，不是品牌商品的實際售價；已排除跳過預算題的事件。")
        if len(hit_budget) < min_n or all_budget.empty:
            html_out(sec_card("預算帶落點", hint_box("預算樣本不足，無法比較"), f"本品牌 n={len(hit_budget)}", budget_how))
        else:
            hit_share = hit_budget.value_counts(normalize=True) * 100
            all_share = all_budget.value_counts(normalize=True) * 100
            df_b = pd.DataFrame([
                {"預算區間": b, "群組": g, "占比": s.get(b, 0.0)}
                for b in BUDGET_OPTIONS
                for g, s in [(f"{my_brand}（n={len(hit_budget)}）", hit_share),
                             (f"全體（n={len(all_budget)}）", all_share)]
            ])
            # 機會區間：全體需求高（>=15%），但本品牌占比比全體低 5 個百分點以上
            opportunity = [b for b in BUDGET_OPTIONS
                           if all_share.get(b, 0) >= 15 and all_share.get(b, 0) - hit_share.get(b, 0) >= 5]
            budget_scale = max(float(df_b["占比"].max()) / 100, 0.05)
            bud_html = ""
            for b in BUDGET_OPTIONS:
                label_html = esc(b) + ('<span class="opp">機會區間</span>' if b in opportunity else "")
                bud_html += grouped_block(label_html, [
                    ("本品牌", "", hit_share.get(b, 0.0) / 100 / budget_scale, f"{hit_share.get(b, 0.0):.0f}%"),
                    ("全體", "all", all_share.get(b, 0.0) / 100 / budget_scale, f"{all_share.get(b, 0.0):.0f}%"),
                ])
            html_out(sec_card(
                "預算帶落點",
                key_html([("本品牌", "var(--accent)"), ("全體", "var(--bar-all)")])
                + f'<div class="gwrap">{bud_html}</div>'
                + (f'<p class="foot">💡 機會區間：{esc("、".join(opportunity))}（使用者需求高，但較少推薦到 {esc(my_brand)}）</p>'
                   if opportunity else ""),
                f"本品牌 n={len(hit_budget)}　全體 n={len(all_budget)}", budget_how,
            ))
            with st.expander("查看原始統計數字"):
                st.dataframe(df_b.round(1), use_container_width=True, hide_index=True)

        # ---- N8 問卷與對話來源對照 ----
        src_rows, src_table = [], []
        for src in sorted(filtered_df["source"].unique()):
            sub_ids = filtered_df.index[filtered_df["source"] == src]
            sub_rank = rank_df[rank_df["event_idx"].isin(sub_ids)]
            n_src = int(sub_rank["event_idx"].nunique())
            src_name = {"filter": "問卷（filter）", "chat": "對話（chat）"}.get(src, src)
            if n_src < min_n:
                src_table.append([esc(src_name), str(n_src), '<span class="mask">樣本不足</span>', ""])
                continue
            m = brand_metrics(sub_rank, my_brand, n_src)
            src_table.append([esc(src_name), str(n_src), f"{m['top1_share']:.1f}%", f"{m['top3_rate']:.1f}%"])
            for metric_name, val in [("Top1 份額", m["top1_share"]), ("Top3 出現率", m["top3_rate"])]:
                src_rows.append({"來源": f"{src}（n={n_src}）", "指標": metric_name, "百分比": val})
        n8_body = html_table(["來源", "事件數 n", "Top1 份額", "Top3 出現率"], src_table, num_idx=(1, 2, 3)) \
            if src_table else hint_box("各來源的樣本都不足，無法比較")
        html_out(sec_card(
            "問卷與對話來源對照", n8_body, f"n={n_base}",
            "<b>怎麼讀：</b>同一個品牌在「問卷」和「對話」兩種情境下的表現是否不同。兩邊事件數常差很多，所以每組都標 n；"
            "分母＝該來源有品牌資料的事件數。左側取消勾選來源，這裡也會跟著少一組。",
        ))
        if src_rows:
            with st.expander("查看原始統計數字"):
                st.dataframe(pd.DataFrame(src_rows).round(1), use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# T3：競品對戰（N6）
# ------------------------------------------------------------
with tab_duel:
    if not my_brand:
        html_out(sec_card("競品對戰", hint_box(NEED_BRAND_HINT)))
    elif not rivals:
        html_out(sec_card("競品對戰", hint_box("請在左側「競品組」選擇至少一個競品")))
    else:
        duel_df = duel_table(rank_df, my_brand, rivals)
        duel_rows = []
        for _, r in duel_df.iterrows():
            name = esc(("★ " if r["競品"] in sponsored_set else "") + r["競品"])
            n_both = int(r["同時出現次數"])
            if n_both < min_n:
                duel_rows.append([name, str(n_both), "", f'<span class="mask">樣本不足（n={n_both} &lt; {min_n}）</span>'])
                continue
            w = float(r["勝率"])
            bar = (f'<div class="row" style="grid-template-columns:minmax(0,1fr) 60px"><div class="track">'
                   f'<div class="fill {"" if w >= 50 else "low"}" style="width:{w:.1f}%"></div>'
                   f'<div class="mark" style="left:50%"></div></div><div class="vl" style="min-width:0">{w:.1f}%</div></div>')
            duel_rows.append([name, str(n_both), str(int(r["本品牌勝場"])), bar])
        duel_how = (
            "<b>怎麼讀：</b>只看「兩個品牌同一次推薦都進前 3 名」的事件，比誰排在前面。虛線是 50%：超過代表本品牌多半贏、"
            "沒到代表多半輸。同事件同品牌重複出現時取最佳名次。排名含贊助加權，所以合作品牌的勝率有一部分來自加權。"
        )
        plot_df = duel_df[duel_df["同時出現次數"] >= min_n]
        duel_foot = ""
        if not plot_df.empty:
            loses = plot_df[plot_df["勝率"] < 50].sort_values("勝率")
            if not loses.empty:
                worst = loses.iloc[0]
                duel_foot = (f'<p class="foot">⚠️ 目前最需要留意的對手：{esc(worst["競品"])}'
                             f'（勝率 {worst["勝率"]:.0f}%，n={int(worst["同時出現次數"])}）</p>')
        html_out(sec_card(
            f"{my_brand} 的競品對戰",
            html_table(["競品", "同時進前 3 名（n）", "本品牌勝場", f"{my_brand} 排在前面的比例"], duel_rows, num_idx=(1, 2))
            + duel_foot,
            f"n={int(duel_df['同時出現次數'].sum())}", duel_how,
        ))
        with st.expander("查看原始統計數字"):
            st.dataframe(duel_df.round(1), use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# T4：贊助成效（N10）— 只有選了合作品牌才會有這個分頁
# ------------------------------------------------------------
if tab_sponsor is not None:
    with tab_sponsor:
        spon_rows = []
        for b in brand_event_counts.index:
            m = brand_metrics(rank_df, b, n_base)
            spon_rows.append({
                "品牌": b, "類型": "合作品牌" if b in sponsored_set else "一般品牌",
                "Top3 事件數": m["n_hit"], "Top1 次數": m["top1"],
                "Top3 出現率(%)": round(m["top3_rate"], 1), "Top1 份額(%)": round(m["top1_share"], 1),
                "曝光占比(%)": round(m["n_hit"] / total_brand_appear * 100, 1) if total_brand_appear else 0,
            })
        df_spon = pd.DataFrame(spon_rows)
        if df_spon.empty or my_metrics["n_hit"] < min_n:
            html_out(sec_card("贊助成效", hint_box(
                f"{esc(my_brand)} 的樣本不足（n={my_metrics['n_hit']}，低於門檻 {min_n}）")))
        else:
            mine = df_spon[df_spon["品牌"] == my_brand].iloc[0]
            non_sponsor = df_spon[(df_spon["類型"] == "一般品牌") & (df_spon["Top3 事件數"] >= min_n)]
            non_avg = non_sponsor["Top3 出現率(%)"].mean() if not non_sponsor.empty else float("nan")
            sp_items = [
                kpi_item(f"{my_brand} 曝光占比", f"{mine['曝光占比(%)']:.1f}%", "占全部品牌曝光"),
                kpi_item("Top1 次數", f"{int(mine['Top1 次數'])}", f"份額 {mine['Top1 份額(%)']:.1f}%"),
                kpi_item("Top3 出現率", f"{mine['Top3 出現率(%)']:.1f}%", f"{int(mine['Top3 事件數'])} 個事件"),
            ]
            if non_avg == non_avg:  # 非 NaN
                gap = mine["Top3 出現率(%)"] - non_avg
                sp_items.append(kpi_item("對比一般品牌平均", f"{gap:+.1f} 個百分點", f"一般品牌平均 {non_avg:.1f}%",
                                         tone="up" if gap >= 0 else "down"))
            else:
                sp_items.append(kpi_item("對比一般品牌平均", "—", "一般品牌樣本不足"))
            html_out('<section class="kpis">' + "".join(sp_items) + '</section>')

            max_exp = max(float(df_spon["曝光占比(%)"].max()), 0.1)
            exp_rows = []
            for _, r in df_spon.iterrows():
                nm = ("★ " if r["品牌"] in sponsored_set else "") + r["品牌"]
                if r["Top3 事件數"] < min_n:
                    exp_rows.append(mask_row(nm, int(r["Top3 事件數"]), min_n))
                else:
                    exp_rows.append(bar_row(
                        nm, r["曝光占比(%)"] / max_exp, f'{r["曝光占比(%)"]:.1f}%（{int(r["Top3 事件數"])}）',
                        "gold" if r["品牌"] in sponsored_set else "", sel=(r["品牌"] == my_brand)))
            html_out(sec_card(
                "合作品牌曝光占比",
                rows_block(exp_rows)
                + f'<p class="foot">合作品牌（{esc("、".join(sorted(sponsored_set)))}）合計曝光占比 {sponsored_ratio:.1f}%。'
                  "曝光占比＝該品牌進前3名的事件數 ÷ 全部品牌進前3名的事件數總和。本頁排名含贊助加權，合作品牌在推薦分數上有加分，並非純自然排名。</p>",
                f"n={n_base}",
                "<b>怎麼讀：</b>所有「前 3 名名額」裡，各品牌拿走多少比例；金色是合作品牌，藍字是你選的品牌。給合作品牌看的簡報，數字含贊助加權這一點必須講清楚。",
            ))
            with st.expander("查看原始統計數字"):
                st.dataframe(df_spon, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# T5：品類總覽（既有圖表當基準 + 職業分布）
# ------------------------------------------------------------
with tab_category:
    n_all = len(filtered_df)
    html_out(sec_card(
        "使用情境分布", count_bars_html(usage_counter), f"n={n_all}",
        "<b>怎麼讀：</b>多選題，一個事件可能提到多個情境，所以比例加總會超過 100%。以下整個頁面是整個品類（不分品牌）的基準分布。"))
    html_out(sec_card("熱門功能需求排行", count_bars_html(feature_counter), f"n={n_all}",
                      "<b>怎麼讀：</b>各功能被提及的次數，多選題。"))
    html_out(sec_card(
        "預算區間分布（不含跳過預算題者）",
        count_bars_html(budget_counter, order=BUDGET_OPTIONS), f"n={sum(budget_counter.values())}"))
    html_out(
        '<div class="cols">'
        + sec_card("裝置類型偏好", donut_html(device_counter), f"n={sum(device_counter.values())}")
        + sec_card("作業系統偏好", donut_html(os_counter), f"n={sum(os_counter.values())}")
        + sec_card("使用情境定位", donut_html(usage_scope_counter) if usage_scope_counter
                   else '<p class="mask">目前篩選範圍內，這一題都沒有人填答</p>',
                   f"n={sum(usage_scope_counter.values())}", "個人使用 / 家庭共用 / 送禮")
        + '</div>'
    )
    age_order_t5 = ["18 歲以下", "19–25 歲", "26–35 歲", "36–45 歲", "46–55 歲", "56 歲以上"]
    html_out(sec_card("年齡層分布", count_bars_html(age_counter, order=age_order_t5), f"n={sum(age_counter.values())}"))
    html_out(sec_card(
        "職業分布（已歸類）", count_bars_html(occupation_counter), f"n={sum(occupation_counter.values())}",
        "<b>怎麼讀：</b>職業是使用者自由輸入，已用關鍵字歸成大類；受眾指數的分母就是這裡的分布。"))
    html_out(sec_card("來源平台曝光次數", count_bars_html(platform_counter), f"n={sum(platform_counter.values())}"))

    html_out(sec_card(
        f"每日查詢趨勢（{start_date} ～ {end_date}）", "", f"n={n_all}",
        "<b>怎麼讀：</b>每天有多少次推薦事件。", open_=True))
    # 把日期轉成純文字字串，並強制用類別軸（category）而非連續時間軸（date），
    # 避免資料只落在單一天時，Plotly 自動把刻度細分到毫秒等級
    df_trend_display = df_trend.copy()
    df_trend_display["date"] = df_trend_display["date"].astype(str)
    fig_trend = px.bar(df_trend_display, x="date", y="count", text="count")
    fig_trend.update_traces(marker_color=BLUE, textposition="outside")
    fig_trend.update_xaxes(type="category")
    fig_trend.update_layout(xaxis_title="", yaxis_title="事件數")
    show_chart(fig_trend, "t5_trend", 320, card=True)

    df_usage = counter_to_df(usage_counter, "使用情境")
    df_features = counter_to_df(feature_counter, "功能")
    df_budget = counter_to_df(budget_counter, "預算區間", "人數")
    df_age = counter_to_df(age_counter, "年齡層")
    df_platform = counter_to_df(platform_counter, "平台")
    with st.expander("查看原始統計數字"):
        st.dataframe(df_usage, use_container_width=True, hide_index=True)
        st.dataframe(df_features, use_container_width=True, hide_index=True)
        st.dataframe(df_budget, use_container_width=True, hide_index=True)
        st.dataframe(df_age, use_container_width=True, hide_index=True)
        if occupation_counter:
            st.dataframe(counter_to_df(occupation_counter, "職業"), use_container_width=True, hide_index=True)
        st.dataframe(df_platform, use_container_width=True, hide_index=True)
        st.dataframe(df_trend, use_container_width=True, hide_index=True)

# ============================================================
# 資料品質檢查（文件第 8 章 Q1～Q3）— 對「全部事件」檢查，不受側邊欄篩選影響
# ------------------------------------------------------------
# 這一區專門回答「動工前要先查」的問題，之後接真實資料時打開看一次即可：
#   Q1 品牌名稱是否一致（同一品牌有幾種寫法、被怎麼合併）
#   Q2 缺品牌的商品是否讓 Top1 失真（前3名是否常少於3個品牌）
#   Q3 真實事件量夠不夠做品牌分析
# ============================================================
st.write("")
with st.expander("🔍 資料品質檢查（品牌名稱 / Top1 失真 / 事件量）"):
    st.caption(
        "目前資料來源：" + ("🧪 假資料（mock_data.py）" if USE_MOCK_DATA else "🌐 後端1 /analytics/events")
        + f"　｜　共 {len(events_df)} 筆事件"
    )

    # ---- Q1 品牌名稱一致性 ----
    st.markdown("**Q1　品牌名稱是否一致**")
    q1_rows = [
        {"原始寫法": raw, "出現次數": cnt, "標準名稱": brand_mapping[raw] or "（排除）", "處理方式": brand_method[raw]}
        for raw, cnt in brand_raw_counts.items()
    ]
    # 指定欄位名稱：即使事件裡完全沒有品牌資料（q1_rows 為空）也不會 KeyError
    df_q1 = pd.DataFrame(q1_rows, columns=["原始寫法", "出現次數", "標準名稱", "處理方式"])
    df_q1 = df_q1.sort_values(["標準名稱", "出現次數"], ascending=[True, False])
    n_raw, n_std = len(df_q1), df_q1.loc[df_q1["標準名稱"] != "（排除）", "標準名稱"].nunique()
    merged = df_q1[df_q1["標準名稱"] != "（排除）"].groupby("標準名稱")["原始寫法"].nunique()
    multi = merged[merged > 1].index.tolist()
    q1c = st.columns(3)
    q1c[0].metric("原始寫法數", n_raw)
    q1c[1].metric("合併後品牌數", n_std)
    q1c[2].metric("有多種寫法的品牌", len(multi))
    if multi:
        st.warning(
            "發現同一品牌有多種寫法，已由 BRAND_LABEL_MAP / 自動合併歸戶："
            + "；".join(f"{m}（{'、'.join(df_q1[df_q1['標準名稱'] == m]['原始寫法'])}）" for m in multi[:12])
        )
    elif df_q1.empty:
        st.warning("事件中完全沒有品牌資料（top_brands 全為空），請確認後端2是否有把推薦結果的品牌寫進事件。")
    else:
        st.success("所有品牌名稱寫法一致，不需要額外對照。")
    excluded = df_q1[df_q1["處理方式"] == "排除（非品牌）"]
    if not excluded.empty:
        st.info("已排除的占位字串（不算品牌）：" + "、".join(f"{r.原始寫法}（{r.出現次數} 次）" for r in excluded.itertuples()))
    unmapped_new = df_q1[df_q1["處理方式"] == "原樣"]
    unmapped_new = unmapped_new[~unmapped_new["標準名稱"].isin(BRAND_LABEL_MAP.keys())]
    if not unmapped_new.empty:
        st.info("以下品牌不在對照表內，已維持原樣並自動加入側邊欄（若其實是別名請補進 BRAND_LABEL_MAP）："
                + "、".join(unmapped_new["標準名稱"].unique()[:30]))
    st.dataframe(df_q1.head(100), use_container_width=True, hide_index=True)

    # 職業歸類檢查
    raw_occ = events_df.loc[events_df["occupation_raw"] != "", ["occupation_raw", "occupation"]]
    if not raw_occ.empty:
        st.markdown("**職業（自由輸入）歸類結果**")
        df_occ_check = (
            raw_occ.value_counts().reset_index(name="出現次數")
            .rename(columns={"occupation_raw": "原始寫法", "occupation": "歸類"})
        )
        others = df_occ_check[df_occ_check["歸類"] == OCCUPATION_OTHER]
        st.caption(f"原始寫法 {len(df_occ_check)} 種；歸到「其他」{len(others)} 種"
                   + ("（若其中有常見職業，請補進 OCCUPATION_LABEL_MAP 關鍵字）" if len(others) else ""))
        st.dataframe(df_occ_check.head(60), use_container_width=True, hide_index=True)

    # ---- Q2 Top1 失真 ----
    st.markdown("**Q2　缺品牌商品是否讓 Top1 失真**")
    n_brand_pos = events_df["top_brands"].apply(lambda c: len(parse_brands(c)))  # 已排除 Other 後的品牌數
    has_dup = events_df["top_brands"].apply(lambda c: len(parse_brands(c)) != len(set(parse_brands(c))))
    q2c = st.columns(3)
    q2c[0].metric("前3名少於 3 個品牌的事件", f"{(n_brand_pos < 3).mean() * 100:.1f}%")
    q2c[1].metric("同品牌占多個名額的事件", f"{has_dup.mean() * 100:.1f}%")
    q2c[2].metric("完全沒有品牌資料的事件", f"{(n_brand_pos == 0).mean() * 100:.1f}%")
    if events_df["product_count"].notna().any():
        lost = ((events_df["product_count"] >= 3) & (n_brand_pos < 3)).mean() * 100
        st.caption(f"product_count ≥ 3 但品牌數 < 3 的事件占 {lost:.1f}%　"
                   "（越高代表越多商品缺品牌欄位被略過，Top1 越可能不是真正的第一名）")
    else:
        st.caption("事件資料沒有 product_count 欄位，無法交叉比對。")

    # ---- Q3 事件量 ----
    st.markdown("**Q3　事件量是否夠做品牌分析**")
    days_covered = (data_max_date - data_min_date).days + 1
    st.caption(f"共 {len(events_df)} 筆事件，涵蓋 {days_covered} 天"
               + ("；假資料為 600 筆。" if USE_MOCK_DATA else "；假資料為 600 筆，真實資料若遠少於此，"
                  "請調低『最小樣本數』並在簡報中說明樣本限制。"))

# ============================================================
# 頁尾備註
# ============================================================
st.write("")
st.caption(
    "本儀表板資料皆為去識別化統計結果，僅供內部與合作品牌參考，不代表個別使用者身份。"
    "樣本為 WearWise 使用者（以年輕族群為主、自選樣本），不代表台灣整體市場；"
    f"資料期間 {start_date} ～ {end_date}，n={len(filtered_df)}。所有品牌排名皆含贊助加權。"
)
