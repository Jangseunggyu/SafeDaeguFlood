
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from scipy.stats import uniform
from scipy.stats import norm
from scipy.stats import binom
import scipy.stats as sp
from scipy.stats import t
import scipy.stats as stats
from scipy import stats

import math
from collections import Counter
from scipy.integrate import quad
from scipy.stats import uniform, norm, binom, poisson, expon, gamma, t, chi2, f, beta
from scipy.stats import bernoulli
from scipy.stats import ttest_rel

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json 
import folium

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

import math
import pandas as pd
from pathlib import Path

from faicons import icon_svg

# Import data from shared.py
from shared import app_dir
from shared import rain, rainy_season_dong, rainy_risk_dong
from shared import dens, age_dong, fore_dong
from shared import dens_sel, age_sel, fore_sel
from shared import w_density, w_children, w_elderly, w_foreign, pop
from shared import geo, geo2, geo_merged
from shared import pump_df, oldest_pump, pump_details
from shared import elevation

from shared import geo_merged

import io
from shiny import App, ui, render, reactive
from shiny.express import output, input, render, ui
from shiny.ui import page_navbar, nav_panel
from functools import partial


from shinywidgets import render_widget
import ipyleaflet as ipyl

# import streamlit as st

from folium.plugins import MarkerCluster
#############################



# 대시보드 타이틀
ui.page_opts(title="대구광역시 내 침수 위험 지역 도출", fillable=True)



# 6개 탭 구성
with ui.navset_pill(id="tab"):


    with ui.nav_panel("결론: 리스크 스코어 -> 종류 선택, 가중치 슬라이드"):
        "가중치 -> 종합점수 -> 지도 시각화 + 검증(2016-2025 실제 사고 지역 읍동면 출력)"
                    
        with ui.layout_columns():
            with ui.card():
                ui.card_header("가중치 슬라이더")

                # 1. 슬라이더 정의 (0 ~ 10 사이 가중치 부여 가능)
                # --- 날씨 요인 ---
                ui.h5("🌧️ 날씨 요인")
                ui.input_slider("w_rain", "강수량 리스크", min=0, max=10, value=5)

                # --- 지리적 요인 ---
                ui.h5("🗺️ 지리적 요인")
                ui.input_slider("w_pump", "빗물펌프장 리스크", min=0, max=10, value=5)
                ui.input_slider("w_lowland", "저지대 리스크", min=0, max=10, value=5)  # 새 추가

                # --- 인구 요인 ---
                ui.h5("👥 인구 요인")
                ui.input_slider("w_dens", "총 인구밀도", min=0, max=10, value=5)
                ui.input_slider("w_child", "어린이 인구밀도", min=0, max=10, value=5)
                ui.input_slider("w_old", "고령자 인구밀도", min=0, max=10, value=5)
                ui.input_slider("w_foreign", "외국인 인구밀도", min=0, max=10, value=5)

            with ui.card():
                ui.card_header("리스크 스코어 지도")

                @render.ui
                def risk_map():
                    # ---- 데이터 준비 ----
                    df = pd.DataFrame()
                    df["읍면동"] = rainy_risk_dong["읍면동"]

                    df["rain"] = rainy_risk_dong["RiskScore_norm"]
                    df["pump"] = oldest_pump["risk_score_norm"]
                    df["lowland"] = elevation["elevation_diff_norm"]  # 새로 추가
                    df["dens"] = dens["인구밀도_norm"]
                    df["child"] = age_dong["어린이 인구밀도_norm"]
                    df["old"] = age_dong["고령자 인구밀도_norm"]
                    df["foreign"] = fore_dong["외국인 인구밀도_norm"]

                    df = df.fillna(0)

                    # ---- 가중치 반영 ----
                    df["risk_score"] = (
                        df["rain"] * (input.w_rain() or 0)
                        + df["pump"] * (input.w_pump() or 0)
                        + df["lowland"] * (input.w_lowland() or 0)  # 새로 포함
                        + df["dens"] * (input.w_dens() or 0)
                        + df["child"] * (input.w_child() or 0)
                        + df["old"] * (input.w_old() or 0)
                        + df["foreign"] * (input.w_foreign() or 0)
                    )

                    # ---- 지도 시각화 ----
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)
                    merged = geo_merged.merge(df, left_on="읍면동", right_on="읍면동", how="left")

                    vmin = merged["risk_score"].min()
                    vmax = merged["risk_score"].max()
                    if vmin == vmax:
                        vmin, vmax = 0, 1

                    colormap = folium.LinearColormap(
                        colors=["#f7fbff", "#6baed6", "#08306b"],
                        vmin=vmin,
                        vmax=vmax,
                        caption="종합 리스크 스코어"
                    )

                    folium.GeoJson(
                        merged.to_json(),
                        style_function=lambda feature: {
                            "fillColor": colormap(feature["properties"]["risk_score"]) if feature["properties"]["risk_score"] is not None else "transparent",
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=folium.GeoJsonTooltip(
                            fields=["읍면동", "risk_score"],
                            aliases=["읍면동", "리스크 스코어"],
                            localize=True
                        )
                    ).add_to(m)

                    colormap.add_to(m)
                    return ui.HTML(m._repr_html_())

                @render.plot
                def risk_top10_plot():
                    merged = geo_merged.copy()
                    merged = merged.merge(rainy_risk_dong[['읍면동', 'RiskScore_norm']], on='읍면동', how='left')
                    merged = merged.merge(oldest_pump[['읍면동', 'risk_score_norm']], on='읍면동', how='left')
                    merged = merged.merge(elevation[['읍면동', 'elevation_diff_norm']], on='읍면동', how='left')  # 추가
                    merged = merged.merge(dens[['읍면동', '인구밀도_norm']], on='읍면동', how='left')
                    merged = merged.merge(age_dong[['읍면동', '어린이 인구밀도_norm', '고령자 인구밀도_norm']], on='읍면동', how='left')
                    merged = merged.merge(fore_dong[['읍면동', '외국인 인구밀도_norm']], on='읍면동', how='left')

                    merged["종합리스크"] = (
                        input.w_rain() * merged["RiskScore_norm"] +
                        input.w_pump() * merged["risk_score_norm"] +
                        input.w_lowland() * merged["elevation_diff_norm"] +  # 새로 포함
                        input.w_dens() * merged["인구밀도_norm"] +
                        input.w_child() * merged["어린이 인구밀도_norm"] +
                        input.w_old() * merged["고령자 인구밀도_norm"] +
                        input.w_foreign() * merged["외국인 인구밀도_norm"]
                    )

                    top10 = merged[['읍면동', '종합리스크']].sort_values(by="종합리스크", ascending=False).head(10)

                    fig, ax = plt.subplots(figsize=(8,6))
                    ax.barh(top10['읍면동'], top10['종합리스크'], color='tomato')
                    ax.set_xlabel("종합 위험 점수")
                    ax.set_ylabel("읍면동")
                    ax.set_title("고위험 Top 10 읍면동")
                    ax.invert_yaxis()
                    ax.grid(axis='x', linestyle='--', alpha=0.7)

                    return fig




    with ui.nav_panel("서론"):
        with ui.layout_columns():

            with ui.card():
                ui.card_header("뉴스")
                ui.p("이곳에 뉴스 관련 내용을 추가합니다.")

            with ui.card():
                ui.card_header("주제선정배경")
                ui.p("이곳에 주제 선정 배경 관련 내용을 추가합니다.")




    with ui.nav_panel("날씨"):
        with ui.layout_columns():

            with ui.card():
                ui.card_header("대구시 장마기간")
                ui.p("기간, 실제 비온날, 강수량")

            with ui.card():
                ui.card_header("행정구별 장마기간 내 강수량")

                # 1. 연도 선택 (Single Select)
                ui.input_select(
                    "year_type", "연도 선택",
                    choices=[str(y) for y in range(2016, 2026)],
                    selected="2024"
                )

                # 2. 지도 출력
                @render.ui
                def rain_map_widget():
                    selected_year = input.year_type()  # 선택 연도

                    # 대구시 중심 지도
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)

                    # 연도 데이터 필터링
                    rainy_season_dong['년도'] = pd.to_datetime(rainy_season_dong['기간시작']).dt.year.astype(str)
                    df = rainy_season_dong[rainy_season_dong['년도'] == selected_year][['구군', '합계강수량']]

                    if df.empty:
                        return ui.HTML(m._repr_html_())

                    # 구군별 합계 강수량 집계
                    df_grouped = df.groupby('구군', as_index=False).sum()

                    # geo_merged와 구군 매칭
                    merged = pd.merge(df_grouped, geo_merged, left_on='구군', right_on='sggnm', how='inner')
                    merged = merged[merged.geometry.notnull()]

                    if merged.empty:
                        return ui.HTML(m._repr_html_())

                    # 컬러맵 설정
                    min_val = merged['합계강수량'].min()
                    max_val = merged['합계강수량'].max()
                    if min_val == max_val:
                        min_val = 0
                        max_val = max_val * 1.1

                    colormap = folium.LinearColormap(
                        colors=['lightblue', 'blue', 'darkblue'],
                        vmin=min_val, vmax=max_val,
                        caption=f"{selected_year} 장마기간 합계강수량 (mm)"
                    )

                    # GeoJson으로 구군 단위 지도 표시
                    for _, row in merged.iterrows():
                        geo_json = folium.GeoJson(
                            row.geometry.__geo_interface__,
                            style_function=lambda feature, val=row['합계강수량']: {
                                "fillColor": colormap(val),
                                "color": "black",   # 구군 경계 검정색
                                "weight": 1,
                                "fillOpacity": 0.7,
                            },
                            tooltip=folium.Tooltip(f"{row['sggnm']}: {row['합계강수량']} mm")
                        )
                        geo_json.add_to(m)

                    colormap.add_to(m)
                    return ui.HTML(m._repr_html_())



    with ui.nav_panel("지리"):
        with ui.layout_columns():
            with ui.card():
                ui.card_header("빗물펌프장 위치")
                

                @render.ui
                def pump_map_widget():
                    # 대구시 중심 지도
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)

                    # 행정동 경계 표시
                    folium.GeoJson(
                        geo_merged.to_json(),
                        style_function=lambda feature: {
                            "fillColor": "transparent",
                            "color": "black",
                            "weight": 1
                        }
                    ).add_to(m)

                    # 빗물펌프장 위치 표시
                    for idx, row in pump_df.iterrows():
                        # 설치년도 NaN 처리 및 소숫점 버림
                        if pd.isna(row['설치년도']):
                            year_str = "알수없음"
                        else:
                            year_str = str(int(row['설치년도']))

                        folium.Marker(
                            location=[row['위도 (Latitude)'], row['경도 (Longitude)']],
                            tooltip=f"{row['펌프장명']} ({year_str})",
                            icon=folium.Icon(color='blue', icon='tint', prefix='fa')
                        ).add_to(m)

                    return ui.HTML(m._repr_html_())


                # 행정구 선택
                ui.input_select(
                    "pump_region", "행정구 선택",
                    choices=["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군", "군위군"],
                    selected="중구"
                )

                @render.data_frame
                def pump_table():
                    selected_region = input.pump_region()

                    # pump_df['위치 (주소)']에서 행정구 추출
                    # 주소에 포함된 행정구 명칭이 있는지 확인
                    mask = pump_df['위치 (주소)'].str.contains(selected_region, na=False)

                    # 필터링된 데이터
                    df_filtered = pump_df.loc[mask, ['펌프장명', '위치 (주소)', '설치년도']].copy()

                    # 설치년도 NaN 및 소숫점 처리
                    df_filtered['설치년도'] = df_filtered['설치년도'].apply(
                        lambda x: int(x) if pd.notna(x) else None
                    )

                    return render.DataGrid(df_filtered, height="400px")



            with ui.card():
                ui.card_header("저지대 지역")

                @render.ui
                def lowland_map():
                    # geo_merged: 지도 데이터 (GeoJSON)
                    # elevation: ['읍면동','elevation','neighbor_avg','elevation_diff']
                    
                    # 지도 생성 (대구 중심)
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)

                    # 지도용 데이터에 고도 정보 병합
                    geo_merged_elev = geo_merged.copy()
                    geo_merged_elev = geo_merged_elev.merge(elevation[['읍면동','elevation_diff']],
                                                            left_on='읍면동', right_on='읍면동',
                                                            how='left')

                    # 색상 함수 정의
                    def get_color(elevation_diff):
                        """고도차에 따른 색상 반환"""
                        if elevation_diff is None:
                            return '#d3d3d3'  # 값 없는 경우 회색
                        elif elevation_diff < -15:
                            return '#8B0000'      # 다크레드
                        elif elevation_diff < -10:
                            return '#DC143C'      # 크림슨
                        elif elevation_diff < -5:
                            return '#FF0000'      # 레드
                        elif elevation_diff < 0:
                            return '#FF6347'      # 토마토
                        elif elevation_diff < 5:
                            return '#87CEEB'      # 스카이블루
                        elif elevation_diff < 10:
                            return '#4169E1'      # 로열블루
                        else:
                            return '#00008B'      # 다크블루

                    # GeoJson 레이어 추가
                    folium.GeoJson(
                        geo_merged_elev.to_json(),
                        style_function=lambda feature: {
                            "fillColor": get_color(feature['properties'].get('elevation_diff')),
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=folium.GeoJsonTooltip(
                            fields=['읍면동', 'elevation_diff'],
                            aliases=['읍면동', '고도차(m)'],
                            localize=True
                        )
                    ).add_to(m)

                    return ui.HTML(m._repr_html_())




    with ui.nav_panel("인구"):
        with ui.layout_columns():
            with ui.card():
                ui.card_header("대구광역시 인구 구성"),
                
                # 1. 인구 종류 선택 (Single Select)
                ui.input_select(
                    "pop_type", "분류 선택",
                    choices=[
                        "총 인구",      # dens['인구(명)']
                        "어린이 인구",      # age_sel['어린이수']
                        "고령자 인구",      # age_sel['고령자수']
                        "외국인 인구"       # fore_sel['외국인 인구(명)']
                    ],
                    selected="총 인구"
                ),
                
                # 2. 행정구 선택 (Checkbox Group)
                ui.input_checkbox_group(
                    "region", "행정구 선택",
                    choices=["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군", "군위군"],
                    selected=["중구"]
                ),
                
                # 3. 지도 출력
                @render.ui
                def map_widget():
                    selected_regions = input.region()
                    pop_choice = input.pop_type()
                    
                    # 기본 지도
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)
                    
                    if selected_regions:
                        # 선택한 인구 데이터 프레임 준비
                        if pop_choice == "총 인구":
                            df = dens[["행정구", "읍면동", "인구(명)"]]
                        elif pop_choice == "어린이 인구":
                            df = age_sel[["행정구", "읍면동", "어린이수"]].rename(columns={"어린이수":"인구(명)"})
                        elif pop_choice == "고령자 인구":
                            df = age_sel[["행정구", "읍면동", "고령자수"]].rename(columns={"고령자수":"인구(명)"})
                        elif pop_choice == "외국인 인구":
                            df = fore_sel[["행정구", "읍면동", "외국인 인구(명)"]].rename(columns={"외국인 인구(명)":"인구(명)"})
                        
                        df = df[df["행정구"].isin(selected_regions)]
                        
                        # GeoDataFrame 병합
                        merged = pd.merge(df, geo_merged, on="읍면동", how="inner")
                        merged = merged[merged.geometry.notnull()]  # NaN geometry 제거
                        
                        # 인구 수에 따라 색상 결정 (컬러맵 사용)
                        import branca.colormap as cm
                        min_val = merged["인구(명)"].min()
                        max_val = merged["인구(명)"].max()
                        colormap = cm.linear.YlOrRd_09.scale(min_val, max_val)
                        colormap.caption = f"{pop_choice} 수"
                        colormap.add_to(m)
                        
                        # 각 읍면동을 검정 테두리, 인구 수 기반 색상으로 표시
                        for idx, row in merged.iterrows():
                            geo_json = folium.GeoJson(
                                row.geometry,
                                style_function=lambda feature, value=row['인구(명)']: {
                                    'fillColor': colormap(value),
                                    'color': 'black',      # 검정 경계
                                    'weight': 1,
                                    'fillOpacity': 0.7,
                                },
                                tooltip=f"{row['읍면동']}: {row['인구(명)']}명"
                            )
                            geo_json.add_to(m)
                    
                    # Folium 지도 HTML로 변환 후 UI 삽입
                    return ui.HTML(m._repr_html_())

            with ui.card():
                ui.card_header("행정구 내 등록 인구수")

                # 1. 행정구 선택 (Single Select)
                ui.input_select(
                    "selected_district", "1단계: 행정구 선택",
                    choices=["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군", "군위군"],
                    selected="중구"
                )

                # 2. 인구/분류 선택 (Single Select)
                ui.input_select(
                    "selected_category", "2단계: 분류 선택",
                    choices=["총 인구", "어린이 인구", "고령자 인구", "외국인 인구"],
                    selected="총 인구"
                )


                # 3. 그래프 출력
                @render.plot
                def population_bar_chart():
                    selected_district = input.selected_district()
                    selected_category = input.selected_category()

                    # 선택한 행정구 필터링
                    df = pop[pop['행정구'] == selected_district].copy()

                    # 분류에 따른 컬럼 매핑
                    category_map = {
                        "총 인구": "인구(명)",
                        "어린이 인구": "어린이수",
                        "고령자 인구": "고령자수",
                        "외국인 인구": "외국인 인구(명)"
                    }
                    value_col = category_map[selected_category]

                    # 읍면동 기준으로 정렬
                    df_sorted = df.sort_values(by=value_col, ascending=True)

                    # 전체 행정구 기준 평균값 계산
                    overall_mean = pop[value_col].mean()

                    # 가로 막대 그래프
                    fig, ax = plt.subplots(figsize=(8,6))
                    ax.barh(df_sorted['읍면동'], df_sorted[value_col], color='skyblue', edgecolor='black')
                    
                    # 전체 평균선 추가
                    ax.axvline(overall_mean, color='red', linestyle='--', linewidth=1, label=f'{selected_category} 전체 평균')

                    # 레이블 및 제목
                    ax.set_xlabel(selected_category)
                    ax.set_ylabel('읍면동')
                    ax.set_title(f"{selected_district} - {selected_category}")
                    ax.grid(axis='x', linestyle='--', alpha=0.7)

                    # 범례를 항상 우측 하단으로 고정
                    ax.legend(loc="lower right")

                    plt.tight_layout()
                    return fig



    with ui.nav_panel("결론:히스토그램"):
        "위험도 점수 히스토그램"



    # with ui.nav_menu("Other links"):
    #     with ui.nav_panel("D"):
    #         "Page D content"

    #     "----"
    #     "Description:"
    #     with ui.nav_control():
    #         ui.a("Shiny", href="https://shiny.posit.co", target="_blank")



