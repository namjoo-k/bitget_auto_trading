import ccxt
import pandas as pd
import time
import os
from datetime import datetime

def fetch_1m_data(symbol='BTC/USDT:USDT'):
    bitget = ccxt.bitget({'enableRateLimit': True})
    tf = '1m'
    
    # 2020년 1월 1일 시작점
    since = bitget.parse8601('2020-01-01T00:00:00Z')
    all_ohlcv = []
    
    # 1분봉은 데이터가 무거우므로 200개씩 안전하게 호출
    SAFE_LIMIT = 200 

    print(f"\n" + "="*50)
    print(f">>> [{tf}] 1분봉 최종 수집 시작 (2020-01-01 ~ 현재)")
    print("주의: 약 328만 행의 대용량 데이터입니다. 수 시간이 소요될 수 있습니다.")

    while True:
        try:
            ohlcv = bitget.fetch_ohlcv(symbol, timeframe=tf, since=since, limit=SAFE_LIMIT)
            
            if not ohlcv or len(ohlcv) == 0:
                # 데이터 공백 시 1분(60,000ms) 점프하며 탐색
                since += 60 * 1000
                if since > bitget.milliseconds(): break
                continue

            all_ohlcv.extend(ohlcv)
            
            # 마지막 데이터 타임스탬프 + 1ms로 다음 시작점 설정
            last_ts = ohlcv[-1][0]
            since = last_ts + 1
            
            # 진행률 확인을 위해 1,000행마다 로그 출력
            if len(all_ohlcv) % 1000 == 0:
                current_dt = datetime.fromtimestamp(last_ts / 1000).strftime('%Y-%m-%d %H:%M')
                print(f"[{tf}] 수집 중: {current_dt} | 누적: {len(all_ohlcv)}행", end='\r')
            
            # 실시간 시점 도달 체크 (5분 전까지 오면 종료)
            if last_ts >= bitget.milliseconds() - (5 * 60 * 1000):
                break
            
            time.sleep(0.05) # 1분봉은 요청 횟수가 많으므로 딜레이 최적화

        except Exception as e:
            print(f"\n[오류] {e}. 5초 후 재시도...")
            time.sleep(5)
            continue

    # 데이터 정제 및 저장
    if all_ohlcv:
        print(f"\n데이터 정제 중... (약 {len(all_ohlcv)} 행)")
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop_duplicates('timestamp').sort_values('timestamp')
        
        if not os.path.exists('data'): os.makedirs('data')
        file_name = f"data/bitget_BTC_{tf}_2020_2026.csv"
        
        # 용량이 크므로 일반 csv 저장 시 시간이 걸릴 수 있음
        df.to_csv(file_name, index=False)
        
        print(f"\n\n>>> [{tf}] 수집 완료!")
        print(f"최종 저장 경로: {file_name}")
        print(f"총 데이터 수: {len(df)} 행")
    else:
        print("\n데이터를 가져오지 못했습니다.")

if __name__ == "__main__":
    fetch_1m_data()