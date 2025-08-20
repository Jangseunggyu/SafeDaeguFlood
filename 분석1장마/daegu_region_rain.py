import pandas as pd

df=pd.read_csv("daegu_rain10years.csv", encoding="cp949" )
print(df)

df.info()
df.describe()
df.shape

##

# -*- coding: utf-8 -*-
import math
import pandas as pd
from pathlib import Path

# =========================================================
# 0) 사용자 입력: 네가 가진 강수 CSV 경로 지정
#    (컬럼: 지점, 지점명, 일시, 일강수량(mm))
# =========================================================
YOUR_RAIN_CSV = "daegu_rain10years.csv"   # <-- 파일명/경로만 바꿔줘

# =========================================================
# 1) 관측소 좌표 CSV 직접 생성
#    - 845/846/860/828: 기상청 연보 표의 도·분 → 10진수 변환값
#    - 991/992: 법정리 대표 좌표(근접 대체값)
# =========================================================
stations = [
    # station_id, name, lat, lon, source_note
    (828, "달성",   35 + 41/60, 128 + 25/60, "KMA 연보(도분)"),
    (845, "대구북구",35 + 54/60, 128 + 35/60, "KMA 연보(도분)"),
    (846, "대구서구",35 + 51/60, 128 + 31/60, "KMA 연보(도분)"),
    (860, "신암",   35 + 53/60, 128 + 37/60, "KMA 연보(도분)"),
    # 아래 두 개는 설치 행정동 대표 좌표(근접치)
    (991, "옥포",   35.794916, 128.440565, "옥포읍 신당리 대표점(주소→좌표)"),
    (992, "하빈",   35.900780, 128.446059, "하빈면 현내리(면민운동장 좌표)"),
]
df_stn = pd.DataFrame(stations, columns=["지점","지점명","lat","lon","좌표출처"])
df_stn.to_csv("stations_daegu.csv", index=False, encoding="utf-8-sig")

# =========================================================
# 2) 대구 9개 구·군 중심 좌표 CSV 직접 생성 (공개 JSON의 대표점 사용)
# =========================================================
districts = [
    ("중구",   35.86678, 128.59538),
    ("동구",   35.88566, 128.63296),
    ("서구",   35.87465, 128.55109),
    ("남구",   35.84119, 128.58800),
    ("북구",   35.90000, 128.59175),
    ("수성구", 35.85905, 128.62625),
    ("달서구", 35.82569, 128.52403),
    ("달성군", 35.77467, 128.42955),
    ("군위군", 36.16995, 128.64705),  # 2023-07-01 대구 편입
]
df_ctr = pd.DataFrame(districts, columns=["구군","lat","lon"])
df_ctr.to_csv("daegu_district_centroids.csv", index=False, encoding="utf-8-sig")

# =========================================================
# 3) 강수 데이터 읽기
#    - 인코딩 이슈 있을 수 있어 cp949도 시도
# =========================================================
def read_csv_any(path):
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")

rain = read_csv_any(YOUR_RAIN_CSV).copy()
# 컬럼 표준화
rain = rain.rename(columns={"일강수량(mm)":"일강수량"})
rain["일시"] = pd.to_datetime(rain["일시"]).dt.date  # 날짜만

# =========================================================
# 4) Haversine 거리(km)
# =========================================================
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2*R*math.asin(math.sqrt(a))

# =========================================================
# 5) IDW 함수 (p=2, k-최근접 사용 권장)
# =========================================================
def idw_estimate(target_lat, target_lon, stations_df, values_series, p=2, k=4):
    # stations_df: (지점, lat, lon)
    # values_series: index=지점, value=해당 지점의 값
    rows = []
    for _, r in stations_df.iterrows():
        sid, slat, slon = r["지점"], r["lat"], r["lon"]
        val = values_series.get(sid, None)
        if pd.notnull(val):
            d = haversine_km(target_lat, target_lon, slat, slon)
            rows.append((sid, d, val))
    if not rows:
        return float("nan")

    # 0거리(같은 점) 보호
    rows = [(sid, max(d, 1e-6), val) for sid, d, val in rows]

    # k-최근접만 사용(너무 먼 지점 영향 제거)
    rows.sort(key=lambda x: x[1])
    rows = rows[:k]

    weights = [1/(d**p) for _, d, _ in rows]
    wsum = sum(weights)
    return sum(w*v for w, (_, _, v) in zip(weights, rows)) / wsum if wsum > 0 else float("nan")

# =========================================================
# 6) 날짜별로 관측소 값 → 각 구·군 IDW 추정
# =========================================================
# 관측소 좌표 테이블
stn_xy = df_stn[["지점","lat","lon"]].drop_duplicates().set_index("지점")

# 일자 × 지점 피벗 (값=일강수량)
pv = rain.pivot_table(index="일시", columns="지점", values="일강수량", aggfunc="mean")

# 결과 담을 리스트
out = []
for the_date, row in pv.iterrows():
    # row: index=지점, value=그 날 지점 값
    for _, g in df_ctr.iterrows():
        gname, glat, glon = g["구군"], g["lat"], g["lon"]
        est = idw_estimate(glat, glon, df_stn[["지점","lat","lon"]], row, p=2, k=4)
        out.append([the_date, gname, est])

df_out = pd.DataFrame(out, columns=["일시","구군","추정_일강수량(mm)"])
df_out = df_out.sort_values(["일시","구군"]).reset_index(drop=True)

# 저장
df_out.to_csv("daegu_district_rain_idw.csv", index=False, encoding="utf-8-sig")

# 미리보기(앞부분)
print(df_out)
print("\n== 파일 생성 완료 ==")
print(" - 관측소 좌표: stations_daegu.csv")
print(" - 구군 중심:   daegu_district_centroids.csv")
print(" - 결과:        daegu_district_rain_idw.csv")


df_out.groupby("구군")['추정_일강수량(mm)'].mean()
df_out.groupby("구군")['추정_일강수량(mm)'].describe()