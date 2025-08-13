from geopy.geocoders import Nominatim
import pandas as pd
import time

# 주소 리스트
addresses = [
    "대구광역시 수성구 매호동 29-1번지",
    "대구광역시 동구 지묘동 731번지",
    "대구광역시 동구 중대동 328번지",
    "대구광역시 북구 침산동 산15-1",
    "대구광역시 북구 노곡,조야,서변동 일원",
    "대구광역시 북구 산격동 744-5",
    "대구광역시 북구 침산동,산격동 일원",
    "대구광역시 달성군 구지면 508",
    "대구광역시 달성군 구지면 징리, 오설리",
    "대구광역시 달성군 다사읍 서재리 693-1",
    "대구광역시 달성군 옥포면 기세리 옥연지",
    "대구광역시 달성군 하빈면 봉촌리 일대",
    "대구광역시 달성군 현풍면 오산리 32",
    "대구광역시 달성군 현풍면 성하리 445",
    "대구광역시 달성군 다사읍 서재리 741"
]

geolocator = Nominatim(user_agent="daegu_map")
lats, lons = [], []

for addr in addresses:
    try:
        location = geolocator.geocode(addr)
        if location:
            lats.append(location.latitude)
            lons.append(location.longitude)
        else:
            lats.append(None)
            lons.append(None)
        time.sleep(1)  # 과도한 요청 방지
    except:
        lats.append(None)
        lons.append(None)

# DataFrame으로 정리
df = pd.DataFrame({
    '주소': addresses,
    '위도': lats,
    '경도': lons
})

print(df)

import folium

# 대구 중심 좌표
daegu_center = [35.8714, 128.6014]

m = folium.Map(location=daegu_center, zoom_start=11)

# 마커 추가
for idx, row in df.iterrows():
    if row['위도'] and row['경도']:
        folium.Marker(
            location=[row['위도'], row['경도']],
            popup=row['주소'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

# 지도 표시
m.save("daegu_flood_points.html")

###########################################################################
from geopy.geocoders import Nominatim
import pandas as pd
import folium
import time

# ==========================
# 1️⃣ 주소 리스트
# ==========================
addresses = [
    "대구광역시 수성구 매호동 29-1번지",
    "대구광역시 동구 지묘동 731번지",
    "대구광역시 동구 중대동 328번지",
    "대구광역시 북구 침산동 산15-1",
    "대구광역시 북구 노곡,조야,서변동 일원", #
    "대구광역시 북구 산격동 744-5", #
    "대구광역시 북구 침산동,산격동 일원", #
    "대구광역시 달성군 구지면 508", #
    "대구광역시 달성군 구지면 징리, 오설리", #
    "대구광역시 달성군 다사읍 서재리 693-1", #
    "대구광역시 달성군 옥포면 기세리 옥연지",
    "대구광역시 달성군 하빈면 봉촌리 일대", #
    "대구광역시 달성군 현풍면 오산리 32",
    "대구광역시 달성군 현풍면 성하리 445",
    "대구광역시 달성군 다사읍 서재리 741"
]

geolocator = Nominatim(user_agent="daegu_map")
lats, lons = [], []
fail_addresses = []

# ==========================
# 2️⃣ 자동 Geocoding
# ==========================
for addr in addresses:
    try:
        location = geolocator.geocode(addr)
        if location:
            lats.append(location.latitude)
            lons.append(location.longitude)
        else:
            lats.append(None)
            lons.append(None)
            fail_addresses.append(addr)
        time.sleep(1)
    except:
        lats.append(None)
        lons.append(None)
        fail_addresses.append(addr)

df = pd.DataFrame({
    '주소': addresses,
    '위도': lats,
    '경도': lons
})

# ==========================
# 3️⃣ 변환 실패 주소 중심 좌표 수동 지정
# ==========================
# 대략적인 중심 좌표 (Google Maps 기준)
manual_coords = {
    "대구광역시 북구 노곡,조야,서변동 일원": (35.904, 128.577),
    "대구광역시 북구 침산동,산격동 일원": (35.879, 128.610),
    "대구광역시 달성군 구지면 징리, 오설리": (35.853, 128.558),
    "대구광역시 달성군 하빈면 봉촌리 일대": (35.781, 128.473)
}

for addr, (lat, lon) in manual_coords.items():
    df.loc[df['주소'] == addr, '위도'] = lat
    df.loc[df['주소'] == addr, '경도'] = lon

# ==========================
# 4️⃣ Folium 지도 시각화
# ==========================
daegu_center = [35.8714, 128.6014]
m = folium.Map(location=daegu_center, zoom_start=11)

for idx, row in df.dropna(subset=['위도', '경도']).iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=row['주소'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

m.save("daegu_flood_points_all.html")
print("지도 생성 완료! -> daegu_flood_points_all.html")

#############################################################################
### 일단 여기가 2020년도에 침수위험지역 및 붕괴위험 지역 지도에 시각화

from geopy.geocoders import Nominatim
import pandas as pd
import folium
import time

# 주소 리스트
addresses = [
    "대구광역시 수성구 매호동 29-1번지",
    "대구광역시 동구 지묘동 731번지",
    "대구광역시 동구 중대동 328번지",
    "대구광역시 북구 침산동 산15-1",
    "대구광역시 북구 노곡,조야,서변동 일원",  # 정상 표시
    "대구광역시 북구 산격동 744-5",            # 정상 표시
    "대구광역시 북구 침산동,산격동 일원",       # 정상 표시
    "대구광역시 달성군 구지면 508",            # 정상 표시
    "대구광역시 달성군 구지면 징리, 오설리",   # 정상 표시
    "대구광역시 달성군 다사읍 서재리 693-1",   # 정상 표시
    "대구광역시 달성군 옥포면 기세리 옥연지",
    "대구광역시 달성군 하빈면 봉촌리 일대",
    "대구광역시 달성군 현풍면 오산리 32",
    "대구광역시 달성군 현풍면 성하리 445",
    "대구광역시 달성군 다사읍 서재리 741"
]

geolocator = Nominatim(user_agent="daegu_map")
lats, lons = [], []

# 자동 Geocoding
for addr in addresses:
    try:
        location = geolocator.geocode(addr)
        if location:
            lats.append(location.latitude)
            lons.append(location.longitude)
        else:
            lats.append(None)
            lons.append(None)
        time.sleep(1)
    except:
        lats.append(None)
        lons.append(None)

df = pd.DataFrame({
    '주소': addresses,
    '위도': lats,
    '경도': lons
})

# 자동 변환 실패한 주소 (# 없는 주소) 중심 좌표 수동 지정
manual_coords = {
    "대구광역시 수성구 매호동 29-1번지": (35.858, 128.637),
    "대구광역시 동구 지묘동 731번지": (35.887, 128.639),
    "대구광역시 동구 중대동 328번지": (35.871, 128.630),
    "대구광역시 북구 침산동 산15-1": (35.887, 128.618),
    "대구광역시 달성군 옥포면 기세리 옥연지": (35.820, 128.530),
    "대구광역시 달성군 하빈면 봉촌리 일대": (35.781, 128.473),
    "대구광역시 달성군 현풍면 오산리 32": (35.809, 128.563),
    "대구광역시 달성군 현풍면 성하리 445": (35.813, 128.565),
    "대구광역시 달성군 다사읍 서재리 741": (35.854, 128.534),
    "대구광역시 북구 노곡,조야,서변동 일원": (35.904, 128.577),
    "대구광역시 북구 침산동,산격동 일원": (35.879, 128.610),
    "대구광역시 달성군 구지면 징리, 오설리": (35.853, 128.558)    
}

# 수동 좌표 적용
for addr, (lat, lon) in manual_coords.items():
    df.loc[df['주소'] == addr, '위도'] = lat
    df.loc[df['주소'] == addr, '경도'] = lon

# Folium 지도 생성
daegu_center = [35.8714, 128.6014]
m = folium.Map(location=daegu_center, zoom_start=11)

for idx, row in df.dropna(subset=['위도', '경도']).iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=row['주소'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

m.save("daegu_flood_points_all_final.html")
print("지도 생성 완료! -> daegu_flood_points_all_final.html")
