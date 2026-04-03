import ccxt
import pandas as pd
import time
import os
from datetime import datetime

def check_missing_15m_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    start_date = df['timestamp'].iloc[0]
    end_date = df['timestamp'].iloc[-1]
    
    # 15T (15분 간격) 기준 타임라인 생성
    expected_range = pd.date_range(start=start_date, end=end_date, freq='15T')
    
    actual_timestamps = set(df['timestamp'])
    missing = [ts for ts in expected_range if ts not in actual_timestamps]
    
    print(f"--- [15m] 검사 결과 ---")
    print(f"목표 행 수: {len(expected_range)}")
    print(f"실제 행 수: {len(df)}")
    print(f"누락된 행 수: {len(missing)}")
    
    if missing:
        print("누락 시점(상위 5개):", missing[:5])

def check_missing_5m_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    start_date = df['timestamp'].iloc[0]
    end_date = df['timestamp'].iloc[-1]
    
    # 5T (5분 간격) 기준 타임라인 생성
    expected_range = pd.date_range(start=start_date, end=end_date, freq='5min')
    
    actual_timestamps = set(df['timestamp'])
    missing = [ts for ts in expected_range if ts not in actual_timestamps]
    
    print(f"--- [5m] 검사 결과 ---")
    print(f"목표 행 수: {len(expected_range)}")
    print(f"실제 행 수: {len(df)}")
    print(f"누락된 행 수: {len(missing)}")
    
    if missing:
        print("누락 시점(상위 5개):", missing[:5])

def check_missing_1m_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    start_date = df['timestamp'].iloc[0]
    end_date = df['timestamp'].iloc[-1]
    
    # 1T (1분 간격) 기준 타임라인 생성
    expected_range = pd.date_range(start=start_date, end=end_date, freq='1min')
    
    actual_timestamps = set(df['timestamp'])
    missing = [ts for ts in expected_range if ts not in actual_timestamps]
    
    print(f"--- [1m] 최종 검사 결과 ---")
    print(f"이론상 목표 행 수: {len(expected_range)}")
    print(f"실제 수집된 행 수: {len(df)}")
    print(f"누락된 행 수: {len(missing)}")
    
    if missing:
        print("최초 누락 시점:", missing[0])
        
check_missing_1m_data('data/bitget_BTC_1m_2020_2026.csv')