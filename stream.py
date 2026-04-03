import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(layout="wide", page_title="BTC 1m Label Viewer")

@st.cache_data # 데이터 로딩 속도 최적화
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

st.title("📈 BTC 1분봉 라벨링 정밀 검수 도구")
st.sidebar.header("🔍 데이터 필터 설정")

# 1. 데이터 불러오기
file_path = 'original_data/bitget_BTC_1m_2020_2026_06_labeled.csv'
try:
    data = load_data(file_path)
except FileNotFoundError:
    st.error(f"파일을 찾을 수 없습니다: {file_path}")
    st.stop()

# 2. 사이드바 컨트롤
# 날짜 선택
min_date = data['timestamp'].min().date()
max_date = data['timestamp'].max().date()
target_date = st.sidebar.date_input("조회 날짜 선택", value=max_date, min_value=min_date, max_value=max_date)

# 시간 범위 선택 (슬라이더)
time_range = st.sidebar.slider("시간 범위 (Hours)", 0, 24, (0, 4))

# 데이터 필터링
start_dt = pd.Timestamp.combine(target_date, pd.Timestamp(f"{time_range[0]}:00:00").time())
end_dt = pd.Timestamp.combine(target_date, pd.Timestamp(f"{time_range[1]-1 if time_range[1] == 24 else time_range[1]}:59:59").time())

df_filtered = data[(data['timestamp'] >= start_dt) & (data['timestamp'] <= end_dt)].copy()

if df_filtered.empty:
    st.warning("선택한 구간에 데이터가 없습니다.")
else:
    # 3. 차트 생성
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_width=[0.2, 0.8])

    # 캔들스틱
    fig.add_trace(go.Candlestick(
        x=df_filtered['timestamp'],
        open=df_filtered['open'], high=df_filtered['high'], 
        low=df_filtered['low'], close=df_filtered['close'],
        name='Price'
    ), row=1, col=1)

    # Long 라벨 (초록색 화살표)
    longs = df_filtered[df_filtered['label'] == 1]
    fig.add_trace(go.Scatter(
        x=longs['timestamp'], y=longs['low'] * 0.998,
        mode='markers', marker=dict(symbol='triangle-up', size=15, color='#00ff00'),
        name='Long Entry'
    ), row=1, col=1)

    # Short 라벨 (빨간색 화살표)
    shorts = df_filtered[df_filtered['label'] == 2]
    fig.add_trace(go.Scatter(
        x=shorts['timestamp'], y=shorts['high'] * 1.002,
        mode='markers', marker=dict(symbol='triangle-down', size=15, color='#ff0000'),
        name='Short Entry'
    ), row=1, col=1)

    # 거래량
    fig.add_trace(go.Bar(
        x=df_filtered['timestamp'], y=df_filtered['volume'], 
        marker_color='rgba(150, 150, 150, 0.5)', name='Volume'
    ), row=2, col=1)

    # 레이아웃 커스텀
    fig.update_layout(
        height=800,
        template='plotly_dark',
        xaxis_rangeslider_visible=False, # 메인 차트 가독성을 위해 하단 슬라이더 제거
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. 통계 정보 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("총 캔들 수", f"{len(df_filtered)} 개")
    col2.metric("Long 타점", f"{len(longs)} 개")
    col3.metric("Short 타점", f"{len(shorts)} 개")