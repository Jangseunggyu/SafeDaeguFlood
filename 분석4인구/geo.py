

import os, json
import pandas as pd
import plotly.express as px

import geopandas as gpd
import folium


with open('./data/hangjeongdong_대구광역시.geojson', 'r') as f:
    daegu_geo = json.load(f)


import geopandas as gpd
import folium
import json

# 1. GeoJSON 데이터 불러오기
geojson_data = { 
    'type': 'FeatureCollection',
    'name': 'temp',
    'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
    'features': daegu_geo  # 여기에 제공하신 GeoJSON 전체 붙여넣기
}

# 2. GeoDataFrame으로 변환
gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

# 좌표계 확인 및 설정 (필요시)
gdf = gdf.set_crs(epsg=4326)  # WGS84

# 3. folium 지도 생성 (대구 중심 좌표)
m = folium.Map(location=[35.8714, 128.6014], zoom_start=11)

# 4. GeoDataFrame을 지도에 추가
folium.GeoJson(
    gdf,
    name='대구 읍면동',
    tooltip=folium.GeoJsonTooltip(fields=['adm_nm'], aliases=['읍면동:'])
).add_to(m)

# 5. 지도 표시
m






# 1. GeoJSON 데이터 → GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
gdf = gdf.set_crs(epsg=4326)  # WGS84

# 2. 우선대응 필요 지역 DataFrame과 병합
# 'adm_nm'과 '읍면동' 이름 기준으로 병합
gdf = gdf.merge(priority_areas[['행정구','읍면동']], 
                left_on=['adm_nm'], 
                right_on=[priority_areas['행정구'] + ' ' + priority_areas['읍면동']], 
                how='left')

# 3. Folium 지도 생성
m = folium.Map(location=[35.8714, 128.6014], zoom_start=11)

# 4. 우선대응 필요 지역 색상 표시
def style_function(feature):
    if feature['properties']['행정구'] is not None:  # 병합된 경우
        return {'fillColor': 'red', 'color': 'red', 'weight':1, 'fillOpacity':0.5}
    else:
        return {'fillColor': 'gray', 'color': 'gray', 'weight':0.5, 'fillOpacity':0.1}

folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['adm_nm'], aliases=['읍면동'])
).add_to(m)

# 5. 지도 출력
m
