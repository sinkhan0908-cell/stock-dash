from __future__ import annotations

import html
import streamlit as st

NAV_ITEMS = [
    ("홈", "⌂"),
    ("관심종목", "☆"),
    ("리서치", "▤"),
    ("포트폴리오", "▦"),
    ("설정", "⚙"),
]


def apply_theme():
    st.markdown("""
<style>
:root{
  --bg:#F7FAFE;--surface:#FFFFFF;--line:#DCE7F5;--line2:#EAF1F8;
  --text:#11233D;--muted:#6C84A3;--blue:#2F80FF;--blue2:#EAF3FF;
  --green:#0FB77A;--red:#FF365D;--soft:#F8FBFF;
}
html,body,[class*="css"]{font-family:Pretendard,"Noto Sans KR","Apple SD Gothic Neo",sans-serif}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1520px;padding-top:1.1rem;padding-bottom:3rem}
header[data-testid="stHeader"]{background:rgba(247,250,254,.9);backdrop-filter:blur(10px)}
section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
section[data-testid="stSidebar"]>div{padding-top:.7rem}
[data-testid="stSidebar"] .stRadio>label{display:none}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{gap:.28rem}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{
 border-radius:10px;padding:.6rem .7rem;color:#18304D;transition:.15s}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover{background:#F4F8FD}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked){
 background:#EAF3FF;color:#1769E8;font-weight:800}
h1,h2,h3,h4{color:var(--text);letter-spacing:-.035em}
p,li{line-height:1.55}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line)!important;border-radius:14px!important;background:#fff;box-shadow:0 6px 18px rgba(31,91,153,.045)}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
[data-testid="stMetricLabel"]{color:#55708E}
[data-testid="stMetricValue"]{color:var(--text);font-weight:800}
.stButton>button,.stFormSubmitButton>button{border-radius:9px;min-height:2.5rem;font-weight:800}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--blue);border-color:var(--blue)}
.stTabs [data-baseweb="tab"]{border-radius:9px;padding:8px 12px}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{border-radius:9px!important}
.planx-brand{display:flex;align-items:center;gap:10px;margin:6px 0 18px}
.planx-brand-mark{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#2F80FF,#5AA4FF);color:#fff;font-size:20px;font-weight:900}
.planx-brand-title{font-size:19px;font-weight:900;letter-spacing:-.03em}
.planx-brand-sub{font-size:10px;color:#6990C2;margin-top:2px}
.sidebar-watch-title{display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:800;color:#18304D;margin:22px 0 8px}
.sidebar-add{color:#2F80FF}
.planx-hero{display:none}
.market-header{margin:0 0 16px}
.market-toolbar{display:flex;justify-content:flex-end;gap:12px;align-items:center;margin-bottom:10px;font-size:11px;color:#58779E}
.live-pill{border:1px solid #CFE1F8;background:#F5FAFF;border-radius:999px;padding:6px 10px;color:#2B65A9;font-weight:700}
.market-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.market-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:0 6px 18px rgba(31,91,153,.04)}
.market-card-head{display:flex;justify-content:space-between;align-items:center}
.market-title{font-size:15px;font-weight:900}.market-title small{font-size:10px;color:#718BAA;font-weight:700;margin-left:5px}
.market-badge{font-size:10px;border-radius:999px;padding:5px 9px;background:#FFF0F4;color:#FF365D;font-weight:800}
.market-main{display:flex;align-items:flex-end;gap:10px;margin-top:8px}
.market-value{font-size:29px;font-weight:900;letter-spacing:-.04em}
.market-change{font-size:12px;color:#FF365D;font-weight:800}
.market-stats{display:flex;gap:16px;margin-top:12px;font-size:10px;color:#7891AF}
.market-stats b{color:#38506B}
.section-heading{display:flex;align-items:flex-start;gap:8px;margin:10px 0 10px}
.section-heading .mark{color:#2F80FF;font-size:18px;font-weight:900}
.section-heading h2{font-size:21px;margin:0}
.section-heading p{font-size:11px;color:#718BAA;margin:2px 0 0}
.company-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 14px 12px;box-shadow:0 6px 18px rgba(31,91,153,.035);height:100%}
.company-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.company-name{font-size:17px;font-weight:900;color:#11233D}.company-code{font-size:11px;color:#6D86A6;margin-left:8px}
.badge-outline{font-size:10px;color:#2F80FF;border:1px solid #CFE0F6;border-radius:999px;padding:4px 8px;font-weight:800}
.company-sub{font-size:13px;font-weight:900;margin-bottom:8px}.company-sub small{font-size:10px;color:#6C84A3;font-weight:700}
.kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.kpi{background:#fff;border:1px solid #DFE9F5;border-radius:10px;padding:12px}
.kpi-label{font-size:11px;font-weight:800;color:#324C6A}.kpi-value{font-size:21px;font-weight:900;margin-top:2px}.kpi-up{font-size:11px;color:#0FB77A;font-weight:900;margin-top:3px}
.info-grid{display:grid;grid-template-columns:1.2fr .9fr .95fr;gap:12px;margin-top:12px}
.info-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}
.info-card h3{font-size:14px;margin:0 0 10px}.info-card p,.info-card li{font-size:11px;color:#536F91}
.bottom-note{margin-top:12px;border:1px solid #DDEAF7;border-radius:10px;background:#F8FBFF;padding:10px 12px;font-size:10px;color:#607B9B}
@media(max-width:900px){.market-grid,.kpi-grid,.info-grid{grid-template-columns:1fr}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)


def market_header():
    st.markdown("""
<div class="market-header">
  <div class="market-toolbar"><span>📅 2026-09-18 (금)</span><span class="live-pill">실시간 시황 ●</span></div>
  <div class="market-grid">
    <div class="market-card">
      <div class="market-card-head"><div class="market-title">코스닥 <small>(KOSDAQ)</small></div><span class="market-badge">연결 대기</span></div>
      <div class="market-main"><div class="market-value">—</div><div class="market-change">실시간 데이터 미연결</div></div>
      <div class="market-stats"><span>시가 <b>—</b></span><span>고가 <b>—</b></span><span>저가 <b>—</b></span></div>
    </div>
    <div class="market-card">
      <div class="market-card-head"><div class="market-title">나스닥 <small>(NASDAQ)</small></div><span class="market-badge">연결 대기</span></div>
      <div class="market-main"><div class="market-value">—</div><div class="market-change">실시간 데이터 미연결</div></div>
      <div class="market-stats"><span>시가 <b>—</b></span><span>고가 <b>—</b></span><span>저가 <b>—</b></span></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


def brand():
    st.markdown("""
<div class="planx-brand"><div class="planx-brand-mark">M</div><div><div class="planx-brand-title">Stock Dash</div><div class="planx-brand-sub">Better Data, Better Decisions</div></div></div>
""", unsafe_allow_html=True)


def hero(title: str, subtitle: str, eyebrow: str = ""):
    st.markdown(f'<div class="planx-hero"><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>', unsafe_allow_html=True)


def card(title: str, value: str, note: str = "", status: str = ""):
    st.markdown(f'<div class="info-card"><h3>{html.escape(title)}</h3><div style="font-size:22px;font-weight:900">{html.escape(value)}</div><p>{html.escape(note)}</p></div>', unsafe_allow_html=True)


def empty_state(title: str, message: str):
    st.markdown(f'<div class="bottom-note"><b>{html.escape(title)}</b><br>{html.escape(message)}</div>', unsafe_allow_html=True)


def source_badge(label: str, state: str = "wait"):
    st.markdown(f'<span class="badge-outline">{html.escape(label)}</span>', unsafe_allow_html=True)
