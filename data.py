import pandas as pd
df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\국토교통부_저층주거 침수피해 시각화_20221201.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df['시도명'].unique()


df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\행정안전부_인명피해 우려지역 현황_20240731.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df.loc[df['시도'] == '대구광역시']


df = pd.read_csv("C:\\Users\\USER\\Desktop\cvs\\인천광역시 남동구_침수위험지역현황_20240729.csv",encoding='euc-kr', sep=None, engine='python')

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

