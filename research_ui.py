import hashlib
from datetime import date
import pandas as pd
import streamlit as st

from ui_v2 import market_header
from automatic import brief
from bi_view import theme, overview, detail, peers_chart
from chat_research import published, parse_bundle, trends, growth, request_text


def render_research(store, state, sample_mode):
    theme()
    market_header()

    research=published()
    for r in state.get('chat_research',[]):
        if r['code'] not in research or r['as_of']>=research[r['code']]['as_of']:
            research[r['code']]=r

    stocks={s['code']:s for s in state.get('stocks',[])}
    for p in st.session_state.get('account_snapshot',{}).get('positions',[]):
        stocks[p['code']]={**stocks.get(p['code'],{}),'code':p['code'],'name':p['name']}

    if not stocks:
        st.markdown('<div class="section-heading"><div class="mark">↗</div><div><h2>관심종목 상세보기</h2><p>관심종목을 추가하면 공식 자료 기반 카드가 표시됩니다.</p></div></div>',unsafe_allow_html=True)
        with st.expander('＋ 관심종목 추가',expanded=True):
            with st.form('research_manual'):
                name=st.text_input('종목명',placeholder='예: 삼성전자')
                code=st.text_input('종목코드',max_chars=6,placeholder='예: 005930')
                if st.form_submit_button('추가',type='primary') and name.strip():
                    identity=code or 'pending-'+hashlib.sha256(name.strip().casefold().encode()).hexdigest()[:16]
                    store.save_stock({'code':identity,'name':name.strip(),'kind':'관심'})
                    st.rerun()
        return

    details={}
    for key,stock in stocks.items():
        r=research.get(key)
        if not r and key.startswith('pending-'):
            m=[v for v in research.values() if v['name'].strip().casefold()==stock['name'].strip().casefold()]
            if len(m)==1:r=m[0]
        r=r or {}
        trend,frame=trends(r.get('prices'),r.get('as_of',date.today().isoformat()))
        details[key]=(stock,r,trend,frame)

    overview(details,st.session_state.get('account_snapshot'))

    st.markdown('<div class="info-grid">',unsafe_allow_html=True)
    col1,col2,col3=st.columns([1.1,1,1],gap='small')

    reports=[r for _,r,_,_ in details.values() if r]
    with col1:
        with st.container(border=True):
            st.subheader('누적 실적')
            bars=[]
            for stock,r,_,_ in details.values():
                f=r.get('financial') or {}
                if f:
                    bars.append({'기업':stock['name'],'2026년 상반기':f['revenue'],'2025년 상반기':f['prior_revenue']})
            if bars:
                df=pd.DataFrame(bars).melt('기업',var_name='기간',value_name='매출')
                st.bar_chart(df,x='기업',y='매출',color='기간',use_container_width=True)
            else: st.info('실적 자료 조사 필요')
    with col2:
        with st.container(border=True):
            st.subheader('핵심 이슈 및 전망')
            for r in reports[:2]:
                st.markdown(f"**{r['name']}**")
                st.write((r.get('summary') or {}).get('text','자료 조사 필요'))
    with col3:
        with st.container(border=True):
            st.subheader('출처 및 기준일')
            for r in reports[:2]:
                st.markdown(f"**{r['name']}**")
                st.caption(f"조사 기준일 {r.get('as_of','-')}")
                if r.get('financial'): st.caption('실적 · '+r['financial']['source'])

    st.markdown('</div>',unsafe_allow_html=True)

    with st.expander('기업별 상세 분석'):
        selected=st.selectbox('자세히 볼 종목',list(details),format_func=lambda k:stocks[k]['name'],key='research_selected')
        stock,r,trend,frame=details[selected]
        if r:
            detail(r)
            tabs=st.tabs(['실적','주가 흐름','가격과 확인 사항'])
            with tabs[0]:
                f=r.get('financial')
                if f:
                    st.dataframe([{'항목':'매출','이번 누적':f['revenue'],'전년 누적':f['prior_revenue'],'변화':growth(f['revenue'],f['prior_revenue'])},{'항목':'영업이익','이번 누적':f['operating_profit'],'전년 누적':f['prior_operating_profit'],'변화':growth(f['operating_profit'],f['prior_operating_profit'])}],hide_index=True,use_container_width=True)
                    if r.get('peers'): peers_chart(r['peers'])
            with tabs[1]:
                flow=r.get('flow')
                if flow and flow.get('foreign') is not None:
                    a,b=st.columns(2);a.metric('외국인 순매수',f"{flow['foreign']:+,.0f}");b.metric('기관 순매수',f"{flow['institution']:+,.0f}")
                else: st.info('외국인·기관 수급 조사 필요')
                a,b=st.columns(2);a.metric('일봉 추세',trend['daily']);b.metric('완료 주봉 추세',trend['weekly'])
                if frame is not None: st.line_chart(frame.set_index('date')['close'])
            with tabs[2]:
                v=r.get('valuation')
                if v and v.get('base') is not None:
                    a,b,c=st.columns(3)
                    a.metric('낮은 참고가',f"{v['low']:,.0f}원");b.metric('기본 참고가',f"{v['base']:,.0f}원");c.metric('높은 참고가',f"{v['high']:,.0f}원")
                else: st.info('평가 가정과 가격 근거 조사 필요')
                for gap in r.get('data_gaps',[]): st.caption('확인 필요 · '+str(gap))

    with st.expander('＋ 종목 추가 / 조사 업데이트'):
        if not sample_mode:
            with st.form('research_manual'):
                name=st.text_input('종목명',placeholder='예: 삼성전자')
                code=st.text_input('종목코드',max_chars=6)
                if st.form_submit_button('내 목록에 추가') and name.strip():
                    identity=code or 'pending-'+hashlib.sha256(name.strip().casefold().encode()).hexdigest()[:16]
                    store.save_stock({'code':identity,'name':name.strip(),'kind':'관심'})
                    st.rerun()
        st.code(request_text(list(stocks.values())),language=None)
        upload=st.file_uploader('조사 JSON 가져오기 · 선택',type=['json'])
        if upload and st.button('조사 파일 검증·저장'):
            reports=parse_bundle(upload.getvalue())
            def save(data):
                merged={r['code']:r for r in data.get('chat_research',[])}
                for r in reports: merged[r['code']]=r
                data['chat_research']=list(merged.values())
            store.change(save); st.rerun()

    st.markdown('<div class="bottom-note">ⓘ 데이터 한계 및 추가 조사 필요 · 실시간 시황, 수급, 장기 가격 시계열은 연결된 공식 소스가 없으면 임의 수치를 표시하지 않습니다.</div>',unsafe_allow_html=True)
