import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def label_pivot_points_v2(file_path):
    # 1. 데이터 로드
    df = pd.read_csv(file_path)
    # 메모리 절약을 위해 필요한 컬럼만 추출하거나 float32 사용 권장 (320만 줄 대응)
    prices = df['close'].values
    labels = np.zeros(len(df), dtype=int) 
    
    # 설정값
    threshold = 0.006  # 0.6% 최소 변동폭
    reverse_limit = 0.01  # 1% 반대 방향 역행 시 무효화
    
    # 상태 변수
    last_pivot_price = prices[0]
    last_pivot_idx = 0
    trend = 0  # 1: 상승 중, -1: 하락 중
    
    print(f"0.6% 기준 라벨링 시작 (총 {len(prices)}행)...")

    for i in range(1, len(prices)):
        current_price = prices[i]
        # 기준점 대비 변동률 계산
        change = (current_price - last_pivot_price) / last_pivot_price
        
        # [조건 1] 반대 방향 1% 급변동 시 기준점 초기화 (비정상 장세 방어)
        if trend != 0 and np.sign(change) != trend and abs(change) >= reverse_limit:
            last_pivot_price = current_price
            last_pivot_idx = i
            trend = 0
            continue

        if trend == 0:
            if change >= threshold:
                trend = 1
                last_pivot_price = current_price
                last_pivot_idx = i
            elif change <= -threshold:
                trend = -1
                last_pivot_price = current_price
                last_pivot_idx = i
        
        elif trend == 1: # 상승 추세 중
            if current_price > last_pivot_price: # 신고가 갱신 시 기준점 이동
                last_pivot_price = current_price
                last_pivot_idx = i
            elif change <= -threshold: # 고점 대비 0.6% 하락 시 -> 이전 고점 라벨링
                labels[last_pivot_idx] = 2 # Short (고점)
                trend = -1
                last_pivot_price = current_price
                last_pivot_idx = i
                
        elif trend == -1: # 하락 추세 중
            if current_price < last_pivot_price: # 신저가 갱신 시 기준점 이동
                last_pivot_price = current_price
                last_pivot_idx = i
            elif change >= threshold: # 저점 대비 0.6% 반등 시 -> 이전 저점 라벨링
                labels[last_pivot_idx] = 1 # Long (저점)
                trend = 1
                last_pivot_price = current_price
                last_pivot_idx = i

    df['label'] = labels
    
    # 결과 요약
    l_count = (labels == 1).sum()
    s_count = (labels == 2).sum()
    print(f"\n[라벨링 결과]")
    print(f"- Long (저점): {l_count}개")
    print(f"- Short (고점): {s_count}개")
    print(f"- 전체 타점 수: {l_count + s_count}개")
    
    output_name = file_path.replace('.csv', '_06_labeled.csv')
    df.to_csv(output_name, index=False)
    return df

def analyze_label_distribution(file_path):
    # 1. 데이터 로드
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 라벨링된 데이터만 필터링 (0은 제외)
    labeled_df = df[df['label'] != 0].copy()
    labeled_df['year'] = labeled_df['timestamp'].dt.year
    labeled_df['month'] = labeled_df['timestamp'].dt.month
    labeled_df['hour'] = labeled_df['timestamp'].dt.hour
    labeled_df['year_month'] = labeled_df['timestamp'].dt.to_period('M')

    # 시각화 설정
    plt.figure(figsize=(18, 12))

    # (1) 연도별 타점 개수
    plt.subplot(2, 2, 1)
    sns.countplot(data=labeled_df, x='year', hue='label', palette='viridis')
    plt.title('Yearly Label Distribution')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # (2) 월별 추세 (시계열 흐름 확인)
    plt.subplot(2, 2, 2)
    labeled_df.groupby('year_month').size().plot(kind='line', marker='o', color='orange')
    plt.title('Monthly Label Count Trend (2020-2026)')
    plt.xticks(rotation=45)
    plt.grid(True)

    # (3) 시간대별(24H) 타점 분포 (어느 시간대에 기회가 많은가?)
    plt.subplot(2, 2, 3)
    sns.countplot(data=labeled_df, x='hour', hue='label', palette='magma')
    plt.title('Hourly Label Distribution (UTC)')
    plt.xlabel('Hour of Day')

    # (4) 라벨 간격(Interval) 분석 - 다음 타점까지 걸리는 시간
    plt.subplot(2, 2, 4)
    labeled_df['time_diff'] = labeled_df['timestamp'].diff().dt.total_seconds() / 3600 # 시간 단위
    sns.histplot(labeled_df['time_diff'].dropna(), bins=50, kde=True, color='purple')
    plt.title('Time Interval Between Labels (Hours)')
    plt.xlabel('Hours')
    plt.xlim(0, 48) # 48시간 이내만 집중 확인

    plt.tight_layout()
    plt.show()

    # 요약 통계 출력
    print("=== 타점 분포 요약 ===")
    print(f"총 타점 수: {len(labeled_df)}")
    print(f"Long(1) 개수: {len(labeled_df[labeled_df['label']==1])}")
    print(f"Short(2) 개수: {len(labeled_df[labeled_df['label']==2])}")
    print("\n[연도별 평균 타점]")
    print(labeled_df.groupby('year').size())


if __name__=="__main__":
    # 라벨링 실행
    # label_pivot_points_v2('data/bitget_BTC_1m_2020_2026.csv')
    
    # visualize 실행
    analyze_label_distribution('data/bitget_BTC_1m_2020_2026_06_labeled.csv')
