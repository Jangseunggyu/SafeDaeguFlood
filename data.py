import pandas as pd
df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\국토교통부_저층주거 침수피해 시각화_20221201.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df['시도명'].unique()


df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\행정안전부_인명피해 우려지역 현황_20240731.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df.loc[df['시도'] == '대구광역시']


df = pd.read_csv("C:\\Users\\USER\\Desktop\cvs\\인천광역시 남동구_침수위험지역현황_20240729.csv",encoding='euc-kr', sep=None, engine='python')

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\daegu_region.csv",encoding='euc-kr', sep=None, engine='python')

df.head()


df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\대구광역시_소방 긴급구조 기상정보.csv",encoding='euc-kr', sep=None, engine='python')
df[df['제목'].str.contains("호우",na=False)]

[df['제목'] == '호우주의보 발표']

df['발표일시'].sort_values(ascending=False)



df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시_서구_하수시설 정비 계획_20240718.csv",encoding='euc-kr', sep=None, engine='python')
df.info()
df.head()

df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\대구광역시 북구_소하천_20240725.csv",encoding='949', sep=None, engine='python')
df
df.head()
df['종점위치'].unique()

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시 달성군_배수펌프장_20240829.csv",encoding='949', sep=None, engine='python')
df.head()
df.loc[df['설치연도']=='1986']

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시_빗물펌프장 현황_20250409.csv",encoding='949', sep=None, engine='python')

df = pd.read_csv("C:\\Users\\USER\\Desktop\대구\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv",encoding='euc-kr', sep=None, engine='python')

df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",encoding='euc-kr', sep=None, engine='python')
df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",encoding='euc-kr', sep=None, engine='python')
df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_북구_재해위험지구_20200211.csv",encoding='euc-kr', sep=None, engine='python')
df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv",encoding='euc-kr', sep=None, engine='python')


import pandas as pd
import folium
from geopy.geocoders import Nominatim
import time

# === 1. CSV 합치기 ===
files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_북구_재해위험지구_20200211.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]

dfs = []
for file in files:
    df = pd.read_csv(file, encoding="cp949")
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# === 2. 침수위험 필터링 ===
# 위험유형 컬럼명이 다르면 여기서 print(data.columns)로 확인 후 수정
flood_data = data[data['재해위험유형'].str.contains('침수', na=False)].copy()

# === 3. 주소 → 좌표 변환 ===
geolocator = Nominatim(user_agent="daegu_flood_mapping")
latitudes = []
longitudes = []

for addr in flood_data['재해위험지역상세주소']:
    try:
        location = geolocator.geocode(f"대구광역시 {addr}")
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except:
        latitudes.append(None)
        longitudes.append(None)
    time.sleep(1)  # 과도한 요청 방지

flood_data['위도'] = latitudes
flood_data['경도'] = longitudes

# === 4. folium 지도 생성 ===
flood_data_geo = flood_data.dropna(subset=['위도', '경도'])
m = folium.Map(location=[35.8714, 128.6014], zoom_start=11)

for _, row in flood_data_geo.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"{row['재해위험지구명']}<br>{row['재해위험지역상세주소']}<br>{row['재해위험지역']}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# 저장
m.save("daegu_flood_risk_map.html")
print("✅ 지도 저장 완료: daegu_flood_risk_map.html")


##################################################################################################

import pandas as pd
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import time

# === 1. CSV 합치기 ===
files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_북구_재해위험지구_20200211.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]

dfs = []
for file in files:
    df = pd.read_csv(file, encoding="cp949")
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# === 2. 침수위험 필터링 ===
flood_data = data[data['재해위험유형'].str.contains('침수', na=False)].copy()

# === 3. 주소 → 좌표 변환 ===
geolocator = Nominatim(user_agent="daegu_flood_mapping")
latitudes = []
longitudes = []

for addr in flood_data['재해위험지역상세주소']:
    try:
        location = geolocator.geocode(f"대구광역시 {addr}")
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except:
        latitudes.append(None)
        longitudes.append(None)
    time.sleep(1)  # 요청 제한을 위해 1초 쉬기

flood_data['위도'] = latitudes
flood_data['경도'] = longitudes

# === 4. 위도/경도 있는 데이터만 추출 ===
flood_data_geo = flood_data.dropna(subset=['위도', '경도'])

# === 5. folium 히트맵 생성 ===
m = folium.Map(location=[35.8714, 128.6014], zoom_start=11)

# 히트맵에 필요한 좌표 리스트 만들기
heat_data = [[row['위도'], row['경도']] for idx, row in flood_data_geo.iterrows()]

# 히트맵 추가
HeatMap(heat_data, radius=15, blur=10).add_to(m)

# === 6. 저장 ===
m.save("daegu_flood_heatmap.html")
print("✅ 히트맵 저장 완료: daegu_flood_heatmap.html")

#####################################################################################

import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import time

# === 1. CSV 합치기 ===
files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_북구_재해위험지구_20200211.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]

dfs = []
for file in files:
    df = pd.read_csv(file, encoding="cp949")
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# === 2. 침수위험 필터링 ===
flood_data = data[data['재해위험유형'].str.contains('침수', na=False)].copy()

# === 3. 주소 → 좌표 변환 ===
geolocator = Nominatim(user_agent="daegu_flood_mapping")
latitudes = []
longitudes = []

for addr in flood_data['재해위험지역상세주소']:
    try:
        location = geolocator.geocode(f"대구광역시 {addr}")
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except:
        latitudes.append(None)
        longitudes.append(None)
    time.sleep(1)  # 요청 제한 고려

flood_data['위도'] = latitudes
flood_data['경도'] = longitudes

# === 4. 위도/경도 있는 데이터만 필터링 ===
flood_data_geo = flood_data.dropna(subset=['위도', '경도'])

# === 5. 2D 히스토그램(헥스빈) 시각화 ===
plt.figure(figsize=(10, 8))
plt.hexbin(
    flood_data_geo['경도'],
    flood_data_geo['위도'],
    gridsize=50,
    cmap='Reds',
    mincnt=1
)
plt.colorbar(label='침수위험지역 개수')
plt.title("대구 침수위험지역 2D 분포 (Hexbin)")
plt.xlabel("경도")
plt.ylabel("위도")
plt.grid(True)
plt.show()

############################################################################################

import pandas as pd
import folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time

# ===== 1. CSV 불러오기 =====
# 침수위험지역
flood_files = [
    r"C:\\Users\\USER\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    r"C:\\Users\\USER\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_북구_재해위험지구_20200211.csv",
    r"C:\\Users\\USER\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    r"C:\\Users\\USER\Desktop\\SafeDaeguFlood\\재해위험지역\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]
dfs = [pd.read_csv(f, encoding="cp949") for f in flood_files]
flood_data = pd.concat(dfs, ignore_index=True)

# 침수위험만 필터
flood_data = flood_data[flood_data['재해위험유형'].str.contains('침수', na=False)].copy()

# ===== 2. 배수펌프장 데이터 =====
pump_files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 중구 배수펌프장정보_20201013.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_빗물펌프장 현황_20250409.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_서구_배수펌프장 현황_20250716.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 달성군_배수펌프장_20240829.csv"
]
pump_dfs = [pd.read_csv(f, encoding="cp949") for f in pump_files]
pump_data = pd.concat(pump_dfs, ignore_index=True)

# ===== 3. 주소 → 좌표 변환 =====
geolocator = Nominatim(user_agent="daegu_flood_pump")

def geocode_address(addr):
    try:
        location = geolocator.geocode(f"대구광역시 {addr}")
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

# 위험지역 좌표
flood_data[['위도', '경도']] = flood_data['재해위험지역상세주소'].apply(
    lambda x: pd.Series(geocode_address(x))
)

# 펌프장 좌표 (컬럼명 맞춰야 함)
pump_address_col = [col for col in pump_data.columns if '주소' in col][0]
pump_data[['위도', '경도']] = pump_data[pump_address_col].apply(
    lambda x: pd.Series(geocode_address(x))
)

# ===== 4. 거리 계산 =====
def find_nearest_pump(lat, lon, pump_df):
    if pd.isna(lat) or pd.isna(lon):
        return None, None
    min_dist = float('inf')
    nearest_name = None
    for _, row in pump_df.dropna(subset=['위도','경도']).iterrows():
        dist = geodesic((lat, lon), (row['위도'], row['경도'])).km
        if dist < min_dist:
            min_dist = dist
            nearest_name = row.get('펌프장명', '이름없음')
    return nearest_name, min_dist

nearest_names = []
nearest_dists = []
for _, row in flood_data.iterrows():
    name, dist = find_nearest_pump(row['위도'], row['경도'], pump_data)
    nearest_names.append(name)
    nearest_dists.append(dist)

flood_data['가장가까운펌프장'] = nearest_names
flood_data['펌프장거리_km'] = nearest_dists

# ===== 5. 커버리지 분석 =====
coverage_threshold = 1.0  # km
outside_coverage = flood_data[flood_data['펌프장거리_km'] > coverage_threshold]
print(f"📌 펌프장 {coverage_threshold}km 밖 위험지역 수: {len(outside_coverage)}")
print(f"📌 전체 대비 비율: {len(outside_coverage) / len(flood_data) * 100:.2f}%")

# ===== 6. 지도 시각화 =====
m = folium.Map(location=[35.8714, 128.6014], zoom_start=11)

# 위험지역 (빨간색)
for _, row in flood_data.dropna(subset=['위도', '경도']).iterrows():
    folium.CircleMarker(
        location=[row['위도'], row['경도']],
        radius=5,
        color='red',
        fill=True,
        fill_opacity=0.7,
        popup=f"위험지역: {row['재해위험지구명']}<br>가까운펌프장: {row['가장가까운펌프장']} ({row['펌프장거리_km']:.2f}km)"
    ).add_to(m)

# 펌프장 (파란색)
for _, row in pump_data.dropna(subset=['위도', '경도']).iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        icon=folium.Icon(color='blue', icon='tint'),
        popup=f"펌프장: {row.get('펌프장명', '이름없음')}"
    ).add_to(m)

m.save("daegu_flood_pump_coverage.html")
print("✅ 지도 저장 완료: daegu_flood_pump_coverage.html")

##########################################################################################################
import pandas as pd
import requests
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import seaborn as sns

# ===== 1. 카카오 API 설정 =====
KAKAO_API_KEY = "카카오_API_KEY"  # 발급받은 키 입력
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

def kakao_geocode(addr):
    try:
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        params = {"query": addr}
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        documents = res.json().get('documents', [])
        if documents:
            lat = float(documents[0]['y'])
            lon = float(documents[0]['x'])
            return lat, lon
    except:
        return None, None
    return None, None

# ===== 2. 침수위험지역 CSV 불러오기 =====
flood_files = [
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_북구_재해위험지구_20200211.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]
dfs = [pd.read_csv(f, encoding="cp949") for f in flood_files]
flood_data = pd.concat(dfs, ignore_index=True)
flood_data = flood_data[flood_data['재해위험유형'].str.contains('침수', na=False)].copy()

# 좌표 변환
flood_data[['위도', '경도']] = flood_data['재해위험지역상세주소'].apply(
    lambda x: pd.Series(kakao_geocode(f"대구광역시 {x}"))
)

# ===== 3. 펌프장 CSV 불러오기 =====
pump_files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 중구 배수펌프장정보_20201013.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_빗물펌프장 현황_20250409.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_서구_배수펌프장 현황_20250716.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 달성군_배수펌프장_20240829.csv"
]
pump_dfs = [pd.read_csv(f, encoding="cp949") for f in pump_files]
pump_data = pd.concat(pump_dfs, ignore_index=True)

# 주소 컬럼 찾기
addr_col = [col for col in pump_data.columns if '주소' in col][0]
pump_data[['위도', '경도']] = pump_data[addr_col].apply(
    lambda x: pd.Series(kakao_geocode(f"대구광역시 {x}"))
)

# ===== 4. 가장 가까운 펌프장 거리 계산 =====
def find_nearest_pump(lat, lon, pump_df):
    if pd.isna(lat) or pd.isna(lon):
        return None
    min_dist = float('inf')
    for _, row in pump_df.dropna(subset=['위도','경도']).iterrows():
        dist = geodesic((lat, lon), (row['위도'], row['경도'])).km
        if dist < min_dist:
            min_dist = dist
    return min_dist

flood_data['펌프장거리_km'] = flood_data.apply(
    lambda row: find_nearest_pump(row['위도'], row['경도'], pump_data), axis=1
)

# ===== 5. 분석용 컬럼 (구 이름 추출) =====
flood_data['구'] = flood_data['재해위험지역'].str.split().str[1]
pump_data['구'] = pump_data[addr_col].str.split().str[1]

# ===== 6. 그래프 =====
plt.rc('font', family='Malgun Gothic')  # 한글폰트 설정
sns.set(style="whitegrid")

# (1) 구별 위험지역 수 vs 펌프장 수
gu_stats = pd.merge(
    flood_data['구'].value_counts().reset_index().rename(columns={'index':'구', '구':'위험지역_수'}),
    pump_data['구'].value_counts().reset_index().rename(columns={'index':'구', '구':'펌프장_수'}),
    on='구', how='outer'
).fillna(0)

gu_stats.plot(x='구', kind='bar', figsize=(10,6))
plt.title("구별 침수위험지역 수 vs 펌프장 수")
plt.ylabel("개수")
plt.xticks(rotation=45)
plt.show()

# (2) 펌프장 거리 분포
plt.figure(figsize=(8,5))
sns.histplot(flood_data['펌프장거리_km'].dropna(), bins=20, kde=True, color='orange')
plt.title("침수위험지역-펌프장 거리 분포")
plt.xlabel("거리 (km)")
plt.ylabel("위험지역 수")
plt.show()

# (3) 구별 평균 펌프장 거리 히트맵
avg_dist_by_gu = flood_data.groupby('구')['펌프장거리_km'].mean().reset_index()
plt.figure(figsize=(8,5))
sns.heatmap(avg_dist_by_gu.pivot_table(index='구', values='펌프장거리_km'),
            annot=True, cmap='Reds', fmt=".2f")
plt.title("구별 평균 펌프장 거리(km)")
plt.show()

# ===== 7. 사각지대 분석 =====
threshold = 1.0  # km
outside_coverage = flood_data[flood_data['펌프장거리_km'] > threshold]
print(f"📌 펌프장 {threshold}km 밖 위험지역 수: {len(outside_coverage)}")
print(f"📌 전체 대비 비율: {len(outside_coverage) / len(flood_data) * 100:.2f}%")


##################################################################################################################3

import pandas as pd

# ==============================
# 1. 데이터 불러오기
# ==============================

# 침수위험지역 CSV들
flood_files = [
    "C:/Users/USER/Desktop/SafeDaeguFlood/재해위험지역/대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    "C:/Users/USER/Desktop/SafeDaeguFlood/재해위험지역/대구광역시_북구_재해위험지구_20200211.csv",
    "C:/Users/USER/Desktop/SafeDaeguFlood/재해위험지역/대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    "C:/Users/USER/Desktop/SafeDaeguFlood/재해위험지역/대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]

flood_dfs = [pd.read_csv(f, encoding="cp949") for f in flood_files]
flood_data = pd.concat(flood_dfs, ignore_index=True)

# 펌프장 CSV들
pump_files = [
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 중구 배수펌프장정보_20201013.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_빗물펌프장 현황_20250409.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_서구_배수펌프장 현황_20250716.csv",
    "C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시 달성군_배수펌프장_20240829.csv"
]
pump_dfs = [pd.read_csv(f, encoding="cp949") for f in pump_files]
pump_data = pd.concat(pump_dfs, ignore_index=True)

# 인구밀도
pop_density = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\분석4인구\\4_취약계층(1)인구밀도\\(1)인구밀도.csv", encoding="utf-8-sig")

# 연령별 인구 (고령인구 비율 계산)
age_df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\분석4인구\\4_취약계층(2)어린이노인\\(1)동·읍·면_연령별_주민등록인구_내국인_전체연령_20250812133656.csv")

# ==============================
# 2. 전처리
# ==============================

# 구 이름만 추출
flood_data['구'] = flood_data['재해위험지역'].str.extract(r'대구광역시\s*(\S+)')
pump_data['구'] = pump_data['주소'].str.extract(r'대구광역시\s*(\S+)')
pop_density['구'] = pop_density['행정구'].str.replace(' ', '')

# 고령인구 비율 계산
age_df['구'] = age_df['행정구역'].str.extract(r'대구광역시\s*(\S+)')
age_grouped = age_df.groupby('구').agg({'65세이상':'sum','총인구':'sum'}).reset_index()
age_grouped['고령인구비율'] = age_grouped['65세이상'] / age_grouped['총인구'] * 100

# ==============================
# 3. 구별 통계
# ==============================

flood_count = flood_data.groupby('구').size().reset_index(name='침수위험지역수')
pump_count = pump_data.groupby('구').size().reset_index(name='펌프장수')

df = flood_count.merge(pump_count, on='구', how='outer').fillna(0)
df = df.merge(pop_density[['구','인구밀도']], on='구', how='left')
df = df.merge(age_grouped[['구','고령인구비율']], on='구', how='left')

# ==============================
# 4. 점수 계산
# ==============================

def normalize(series, reverse=False):
    if reverse:  # 값이 작을수록 점수 높음
        return (series.max() - series) / (series.max() - series.min()) * 100
    else:
        return (series - series.min()) / (series.max() - series.min()) * 100

df['위험지역점수'] = normalize(df['침수위험지역수'])
df['펌프장부족점수'] = normalize(df['펌프장수'], reverse=True)
df['인구밀도점수'] = normalize(df['인구밀도'])
df['고령인구점수'] = normalize(df['고령인구비율'])

# 가중치 적용
df['위험점수'] = (
    df['위험지역점수'] * 0.3 +
    df['펌프장부족점수'] * 0.2 +
    df['인구밀도점수'] * 0.3 +
    df['고령인구점수'] * 0.2
)

# ==============================
# 5. 저장
# ==============================
df = df[['구','침수위험지역수','펌프장수','인구밀도','고령인구비율','위험점수']]
df.to_csv("위험점수_기준표.csv", index=False, encoding="utf-8-sig")

print("✅ 위험 점수 표 저장 완료: 위험점수_기준표.csv")
print(df.sort_values('위험점수', ascending=False))
print(pop_density.columns)
print(age_df.columns)

df = pd.read_csv("C:\\Users\\USER\\Desktop\\SafeDaeguFlood\\배수펌프장\\대구광역시_빗물펌프장 현황_20250409.csv",encoding='949')

df.head()

################################################################################################################################
import pandas as pd
import glob

# 1️⃣ 배수펌프장 파일 불러오기
pump_files = [
    r"C:\Users\USER\Desktop\SafeDaeguFlood\배수펌프장\대구광역시_서구_배수펌프장 현황_20250716.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\배수펌프장\대구광역시_빗물펌프장 현황_20250409.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\배수펌프장\대구광역시 중구 배수펌프장정보_20201013.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\배수펌프장\대구광역시 달성군_배수펌프장_20240829.csv"
]

pump_list = []
for f in pump_files:
    df = pd.read_csv(f, encoding='cp949')  # 혹시 인코딩 문제 시 'euc-kr'도 가능
    df.columns = df.columns.str.strip()  # 공백 제거
    pump_list.append(df)

pump_df = pd.concat(pump_list, ignore_index=True)

# 배수펌프장 데이터 확인 후 '구' 컬럼과 '용량(HP)' 컬럼 추출
# 실제 컬럼명에 맞게 수정 필요
pump_df['구'] = pump_df['행정구역'].str.replace(' ', '')
pump_df['배수용량'] = pump_df['펌프']  # 컬럼명에 맞게 수정
pump_df_grouped = pump_df.groupby('구')['배수용량'].sum().reset_index()

# 2️⃣ 재해위험지역 파일 불러오기
hazard_files = [
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_북구_재해위험지구_20200211.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_동구_재해위험지구_20200423_1587606070033_618.csv",
    r"C:\Users\USER\Desktop\SafeDaeguFlood\재해위험지역\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv"
]

hazard_list = []
for f in hazard_files:
    df = pd.read_csv(f, encoding='cp949')
    df.columns = df.columns.str.strip()
    hazard_list.append(df)

hazard_df = pd.concat(hazard_list, ignore_index=True)

# '구' 컬럼과 '재해위험지역면적' 추출 (컬럼명 확인 필요)
hazard_df['구'] = hazard_df['행정구역(구)'].str.replace(' ', '')
hazard_df['재해위험지역면적'] = hazard_df['면적(㎡)']  # 컬럼명 확인 필요
hazard_df_grouped = hazard_df.groupby('구')['재해위험지역면적'].sum().reset_index()

# 3️⃣ 배수펌프장 + 재해위험지역 병합
df = pd.merge(hazard_df_grouped, pump_df_grouped, on='구', how='left')
df['용량_HP'] = df['용량_HP'].fillna(0)  # 펌프 없는 구는 0으로 처리

# 4️⃣ 점수 계산
# 위험면적 비율
df['위험면적비율'] = df['재해위험지역면적'] / df['재해위험지역면적'].sum()

# 펌프 용량 점수화 (용량 작을수록 점수 ↑)
max_capacity = df['용량_HP'].max()
df['펌프장점수'] = 1 - (df['용량_HP'] / max_capacity)

# 최종 침수취약점수 (가중치: 위험면적 0.7, 펌프용량 0.3)
df['침수취약점수'] = df['위험면적비율']*0.7 + df['펌프장점수']*0.3

# 등급 부여
def assign_grade(score):
    if score < 0.2:
        return 'A'
    elif score < 0.4:
        return 'B'
    elif score < 0.6:
        return 'C'
    elif score < 0.8:
        return 'D'
    else:
        return 'E'

df['위험등급'] = df['침수취약점수'].apply(assign_grade)

# 5️⃣ 결과 확인
print(df[['구','재해위험지역면적','용량_HP','침수취약점수','위험등급']])
