"""Dashboard BI views."""
import altair as alt
import pandas as pd
import streamlit as st

BLUE='#2F80FF'; GREEN='#0FB77A'; TEXT='#11233D'; GRID='#E6EEF8'


def theme():
    st.markdown("""<style>
    .stApp{background:#F7FAFE;color:#11233D}
    [data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #DCE7F5}
    [data-testid="stSidebar"] *{color:#11233D!important}
    .block-container{max-width:1520px;padding-top:1.1rem}
    [data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#DCE7F5!important;border-radius:12px!important;background:#fff}
    [data-testid="stMetric"]{background:#fff;border:1px solid #DCE7F5;border-radius:10px;padding:14px 16px}
    [data-testid="stMetricValue"]{color:#11233D;font-weight:900}
    </style>""", unsafe_allow_html=True)


def draw(chart):
    st.altair_chart(chart.configure(background='#FFFFFF').configure_view(stroke=None)
      .configure_axis(labelColor='#5E7897',titleColor='#5E7897',gridColor=GRID,labelFontSize=10,titleFontSize=10)
      .configure_legend(labelColor='#587290',titleColor='#587290',labelFontSize=10), use_container_width=True)


def company_panel(stock, report):
    f=(report or {}).get('financial') or {}
    name=stock.get('name','-'); code=(report or {}).get('code', stock.get('code',''))
    st.markdown(f'<div class="company-head"><div><span class="company-name">{name}</span><span class="company-code">{code}</span></div><span class="badge-outline">조회 필요</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="company-sub">주요 실적 <small>(2026년 상반기 누적, 연결 기준)</small></div>',unsafe_allow_html=True)
    if f:
        rg=(f['revenue']/f['prior_revenue']-1)*100 if f.get('prior_revenue') else None
        og=(f['operating_profit']/f['prior_operating_profit']-1)*100 if f.get('prior_operating_profit') else None
        st.markdown(f'''<div class="kpi-grid"><div class="kpi"><div class="kpi-label">매출</div><div class="kpi-value">{f['revenue']:.2f}조원</div><div class="kpi-up">▲ {rg:,.2f}% <span style="color:#7891AF;font-weight:700">(전년동기 대비)</span></div></div><div class="kpi"><div class="kpi-label">영업이익</div><div class="kpi-value">{f['operating_profit']:.2f}조원</div><div class="kpi-up">▲ {og:,.2f}% <span style="color:#7891AF;font-weight:700">(전년동기 대비)</span></div></div></div>''',unsafe_allow_html=True)
        df=pd.DataFrame([{'구분':'2025.H1','매출':f['prior_revenue'],'영업이익':f['prior_operating_profit']},{'구분':'2026.H1','매출':f['revenue'],'영업이익':f['operating_profit']}])
        long=df.melt('구분',var_name='항목',value_name='값')
        st.markdown('<div class="company-sub" style="margin-top:10px">최근 실적 추이 <small>(연결 기준)</small></div>',unsafe_allow_html=True)
        chart=alt.Chart(long).mark_line(point=True,strokeWidth=2).encode(x=alt.X('구분:N',title=None),y=alt.Y('값:Q',title='조원'),color=alt.Color('항목:N',scale=alt.Scale(range=[BLUE,GREEN])),tooltip=['구분','항목',alt.Tooltip('값:Q',format=',.2f')]).properties(height=160)
        draw(chart)
    else:
        st.info('공식 실적 조사 필요')


def overview(details, snapshot):
    st.markdown('<div class="section-heading"><div class="mark">↗</div><div><h2>관심종목 상세보기</h2><p>최신 공식 자료 기반의 기업 실적과 주요 정보를 한눈에 확인하세요.</p></div></div>',unsafe_allow_html=True)
    cols=st.columns(2,gap='small')
    for col,(_,item) in zip(cols,list(details.items())[:2]):
        stock,report,_,_=item
        with col:
            with st.container(border=True):
                company_panel(stock,report)


def detail(r):
    f=r.get('financial') or {}
    business=r.get('business') or r.get('summary')
    left,right=st.columns([1.15,1],gap='small')
    with left,st.container(border=True):
        st.subheader('주요 사업 영역')
        if business: st.write(business['text'])
        else: st.info('사업 내용 조사 필요')
    with right,st.container(border=True):
        st.subheader('경쟁사 비교')
        peers=r.get('peers')
        if peers and peers.get('rows'):
            rows=[]
            for x in peers['rows']:
                rows.append({'기업':x['name'],'영업이익(조원)':x['operating_profit']/10000})
            st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
            if f and f.get('revenue'):
                st.caption(f"선택 기업 영업이익률 {f['operating_profit']/f['revenue']*100:.1f}%")
        else: st.info('비교 가능한 공식 자료 필요')


def peers_chart(peers):
    df=pd.DataFrame(peers['rows']).rename(columns={'name':'기업','operating_profit':'영업이익'})
    draw(alt.Chart(df).mark_bar(color=BLUE,cornerRadiusEnd=4).encode(x=alt.X('영업이익:Q',title=peers['unit']),y=alt.Y('기업:N',sort='-x',title=None),tooltip=['기업',alt.Tooltip('영업이익:Q',format=',.1f')]).properties(height=180))
