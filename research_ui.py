import hashlib
from datetime import date
import pandas as pd
import streamlit as st

from ui_v2 import market_header
from automatic import brief
from bi_view import theme, overview, detail, peers_chart
from chat_research import published, parse_bundle, trends, growth, request_text
from providers import DataError, Official


def _quote_number(value):
    try:
        return float(str(value).replace(',', ''))
    except (TypeError, ValueError):
        return None


def _quote_from_row(code, name, price, price_date, row):
    """Normalize the official daily quote without inventing unavailable fields."""
    change=_quote_number(row.get('vs'))
    rate=_quote_number(row.get('fltRt'))
    return {
        'code':code,
        'name':name,
        'price':price,
        'date':price_date,
        'change':change,
        'rate':rate,
        'open':_quote_number(row.get('mkp')),
        'high':_quote_number(row.get('hipr')),
        'low':_quote_number(row.get('lopr')),
        'volume':_quote_number(row.get('trqu')),
    }


def _display_quote_date(value):
    text=str(value or '-')
    return f'{text[:4]}-{text[4:6]}-{text[6:8]}' if len(text)==8 and text.isdigit() else text


@st.cache_data(ttl=300, show_spinner=False)
def _official_quotes(codes):
    provider=Official()
    quotes={}
    errors={}
    today=date.today()
    for code in codes:
        try:
            price,price_date,name=provider.price(code,today)
            row=provider.price_rows.get((code,today.isoformat()),{})
            quotes[code]=_quote_from_row(code,name,price,price_date,row)
        except DataError as error:
            errors[code]=str(error)
    return quotes,errors


def render_quotes(stocks):
    valid=[code for code in stocks if len(code)==6 and code.isdigit()]
    st.markdown('<div class="section-heading"><div class="mark">₩</div><div><h2>현재 주식 시세</h2><p>금융위원회 주식시세정보의 최근 거래일 종가입니다.</p></div></div>',unsafe_allow_html=True)
    if not valid:
        st.info('6자리 종목코드를 확인하면 공식 시세가 표시됩니다.')
        return
    quotes,errors=_official_quotes(tuple(valid))
    cols=st.columns(min(2,len(valid)),gap='small')
    for index,code in enumerate(valid):
        stock=stocks[code]
        with cols[index % len(cols)]:
            with st.container(border=True):
                q=quotes.get(code)
                st.markdown(f"**{stock['name']}** · `{code}`")
                if not q:
                    report=stock.get('report') or {}
                    snapshot=stock.get('price_snapshot')
                    if not snapshot and report.get('price'):
                        snapshot={'price':report['price'],'date':report.get('price_date')}
                    if snapshot and snapshot.get('price'):
                        st.metric('저장된 기준 종가',f"{snapshot['price']:,.0f}원")
                        st.caption('기준일 '+_display_quote_date(snapshot.get('date'))+' · 새 시세 조회 실패')
                    else:
                        st.info('시세 조회 필요')
                    if errors.get(code): st.caption(errors[code])
                    continue
                delta=None if q['change'] is None else f"{q['change']:+,.0f}원"
                if q['rate'] is not None:
                    delta=(delta+' · ' if delta else '')+f"{q['rate']:+.2f}%"
                st.metric('최근 종가',f"{q['price']:,.0f}원",delta=delta)
                items=[]
                for label,key in [('시가','open'),('고가','high'),('저가','low')]:
                    if q[key] is not None: items.append(f"{label} {q[key]:,.0f}원")
                if items: st.caption(' · '.join(items))
                volume=f" · 거래량 {q['volume']:,.0f}주" if q['volume'] is not None else ''
                st.caption(f"기준일 {_display_quote_date(q['date'])}{volume} · 실시간 체결가 아님")
    if st.button('시세 새로고침',key='refresh_official_quotes'):
        _official_quotes.clear()
        st.rerun()


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

    render_quotes(stocks)

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
