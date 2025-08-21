from pathlib import Path
import pandas as pd
import geopandas as gpd
import folium

from sklearn.preprocessing import MinMaxScaler

# MinMax 스케일링 (0 ~ 10)
scaler = MinMaxScaler(feature_range=(0, 10))

# =========================================================
# 1. 앱 기준 디렉토리 설정
# =========================================================
app_dir = Path(__file__).parent

# =========================================================
# 2. 날씨 요인
# =========================================================
# 대구시 장마 기간 및 기간 내 총 강수량(2016 ~ 2024), 강수일수 확인용
rain = pd.read_csv(app_dir / 'rain.csv')


# 행정구별 장마 기간 내 강수량 분석 
# rainy_season_gu = pd.read_csv(app_dir / '행정구별 강수량.csv')
rainy_season_dong = pd.read_csv(app_dir / '장마기간 행정구별 강수량_행정동추가.csv')


# 행정구별 장마 기간 내 강수량 분석 (2016~2024: 6월 1일 ~ 9월 30일, 2025: 6월 1일 ~ 8월 18일)
# # 리스크 스코어
# rainy_risk_gu = pd.read_csv(app_dir / '대구 행정구별 강수량 스코어_0601_0930.csv')
# 행정구 내 읍면동 삽입
rainy_risk_dong = pd.read_csv(app_dir / '읍면동 강수량 리스크 스코어_0601_0930.csv')
rainy_risk_dong["RiskScore_norm"] = scaler.fit_transform(
    rainy_risk_dong[["RiskScore"]]
).round(2)


# =========================================================
# 3. 인구 요인
# =========================================================

# (1) 전체 인구밀도
# 읍면동 단위 인구 및 인구밀도
dens = pd.read_csv(app_dir / '읍면동 전체 인구밀도.csv')
dens['행정구'].unique()


dens["인구밀도_norm"] = scaler.fit_transform(
    dens[["인구밀도"]]
).round(2)


# (2) 어린이 인구밀도
# (3) 고령자 인구밀도
age_dong = pd.read_csv(app_dir / '어린이 고령자 읍면동 인구밀도.csv')

age_dong["어린이 인구밀도_norm"] = scaler.fit_transform(
    age_dong[["어린이_인구밀도"]]
).round(2)

age_dong["고령자 인구밀도_norm"] = scaler.fit_transform(
    age_dong[["고령자_인구밀도"]]
).round(2)

# (4) 외국인 인구밀도
fore_dong = pd.read_csv(app_dir / '읍면동 외국인 인구.csv')

fore_dong["외국인 인구밀도_norm"] = scaler.fit_transform(
    fore_dong[["외국인 인구밀도"]]
).round(2)


# 1. 필요한 열만 선택
dens_sel = dens[['행정구', '읍면동', '면적(㎢)', '인구(명)', '인구밀도']]
age_sel = age_dong[['행정구', '읍면동', '어린이수', '어린이_인구밀도', '고령자수', '고령자_인구밀도']]
fore_sel = fore_dong[['행정구', '읍면동', '외국인 인구(명)', '외국인 인구밀도']]


# 2. 읍면동 기준으로 순차 병합
pop = (
    dens_sel
    .merge(age_sel, on="읍면동", how="left")
    .merge(fore_sel, on="읍면동", how="left")
)
pop.info()

# 위험도 계산
w_density, w_children, w_elderly, w_foreign = 0.25, 0.25, 0.25, 0.25
pop["종합위험도"] = (
    w_density * pop["인구밀도"]
    + w_children * pop["어린이_인구밀도"]
    + w_elderly * pop["고령자_인구밀도"]
    + w_foreign * pop["외국인 인구밀도"]
).round(2)

# =========================================================
# 4. 지리 요인
# =========================================================

# 지도 전처리
geo = gpd.read_file(app_dir / "hangjeongdong_대구광역시.geojson")
geo2 = gpd.read_file(app_dir / "hangjeongdong_경상북도.geojson")


# 군위 데이터 추출
geo1 = geo2[geo2['adm_nm'].str.contains('경상북도 군위', na=False)].copy()


# 대구 + 군위 합치기
geo_merged = pd.concat([geo, geo1], ignore_index=True)
geo_merged = gpd.GeoDataFrame(geo_merged, crs=geo.crs)


# 불필요한 앞뒤 공백 제거
geo_merged['adm_nm'] = geo_merged['adm_nm'].str.strip()


# GeoJSON의 '경상북도 군위군'을 '군위군'으로 변경 (대구 편입 반영)

geo_merged['adm_nm'] = geo_merged['adm_nm'].str.replace('경상북도 군위군', '대구광역시 군위군', regex=False)

# 읍면동 정보 추가
geo_merged['읍면동'] = geo_merged['adm_nm'].apply(lambda x: x.split()[-1])

# 전처리 완료
# geo_merged
geo_merged.dtypes






# 빗물펌프장 정보 : 설치년도, 위도, 경도
pump_df = pd.read_csv(app_dir / '빗물펌프장final.csv', sep=',')


# 빗물펌프장 설치년도에 따른 리스크 스코어
oldest_pump = pd.read_csv(app_dir / '펌프 리스크 스코어.csv', sep=',')
oldest_pump['읍면동'] = oldest_pump['adm_nm'].apply(lambda x: x.split()[-1])



oldest_pump["risk_score_norm"] = scaler.fit_transform(
    oldest_pump[["risk_score"]]
).round(2)

# 읍면동 펌프장 리스트
pump_details = pd.read_csv(app_dir / '읍면동 펌프장 리스트.csv', sep=',')
pump_details['읍면동'] = pump_details['adm_nm'].apply(lambda x: x.split()[-1])




# 고도
elevation = pd.read_csv(app_dir / 'elevation_analysis_simple.csv')

# elevation(고도), neighbor_avg(주변고도), elevation_diff(주변대비 고도 차이값)


# 주변보다 낮은 고도 읍면동
elevation[elevation['elevation_diff'] < 0][['dong_name','elevation','neighbor_avg','elevation_diff']]

elevation = elevation.rename(columns={'dong_name': '읍면동'})

elevation["elevation_diff_norm"] = scaler.fit_transform(
    elevation[["elevation_diff"]]
).round(2)

# # 'full_name'에서 구 정보 추출하여 '행정구' 열 생성
elevation['행정구'] = elevation['full_name'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else None)


