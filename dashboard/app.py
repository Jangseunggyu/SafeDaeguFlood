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

from shared import geo_merged  # (중복 import 허용)

import io
from shiny import App, ui, render, reactive
from shiny.express import output, input, render, ui
from shiny.ui import page_navbar, nav_panel
from functools import partial

from shinywidgets import render_widget
import ipyleaflet as ipyl
from folium.plugins import MarkerCluster
from shiny.express import ui as xui


# =========================
# 0) 읍면동 정규화 유틸 & 하이라이트 목록 (상단 선언)
# =========================
def norm_dong(name: str) -> str:
    """읍면동 이름 표준화: 공백 제거, 구분자 통일(, . ･ ㆍ -> ·), 특수 케이스 매핑"""
    if pd.isna(name):
        return ""
    s = str(name).strip()
    s = s.replace(" ", "")
    s = s.replace("･", "·").replace(",", "·").replace(".", "·").replace("ㆍ", "·")
    mapping = {
        "두류1·2동": "두류1·2동",
        "두류1,2동": "두류1·2동",
        "두류1.2동": "두류1·2동",
        "신천1,2동": "신천1·2동",
        "신천1.2동": "신천1·2동",
    }
    return mapping.get(s, s)

# geo_merged에 병합 키 추가(앱 시작 시 1회)
geo_merged = geo_merged.copy()
geo_merged["dong_key"] = geo_merged["읍면동"].apply(norm_dong)

# 하이라이트할 읍면동 목록 (하천 인근으로 사용하는 리스트)
highlight_dong_list = [
    '신당동','다사읍','관문동','상중이동','비산7동','노원동','무태조야동','침산1동',
    '산격2동','검단동','불로·봉무동','북현2동','지저동','신암5동','효목1동','동촌동',
    '만촌1동','방촌동','고산2동','안심2동','안심1동','안심4동','고산3동','안심3동',
    '침산3동','산격1동','침산2동','산격4동','칠성동','대현동','신암2동','동인동',
    '신천1·2동','수성4가동','삼덕동','대봉1동','수성1가동','이천동','중동','봉덕2동',
    '상동','파동','가창면'
]
highlight_dong_df = pd.DataFrame(highlight_dong_list, columns=['읍면동'])
river_set_norm = set(highlight_dong_df["읍면동"].dropna().astype(str).apply(norm_dong))

# =========================
# 공용: HTML 범례 유틸
# =========================
def add_html_legend(m, title, items, position="bottomright"):
    """
    Folium 지도에 간단한 HTML 범례를 추가합니다.
    - items: [(label, color), ...]
    - position: 'bottomright' | 'bottomleft' | 'topright' | 'topleft'
    """
    vpos, hpos = ("bottom", "right")
    if position == "bottomleft": vpos, hpos = ("bottom", "left")
    elif position == "topright": vpos, hpos = ("top", "right")
    elif position == "topleft": vpos, hpos = ("top", "left")

    rows = ""
    for label, color in items:
        rows += (
            "<div style='display:flex;align-items:center;gap:8px;margin:2px 0;'>"
            f"<span style='display:inline-block;width:12px;height:12px;background:{color};"
            "border:1px solid #333;'></span>"
            f"<span style='font-size:12px;'>{label}</span>"
            "</div>"
        )

    html = (
        f"<div style='position: fixed; z-index: 9999; {vpos}: 28px; {hpos}: 28px;'>"
        "<div style='background: rgba(255,255,255,0.92); padding:10px 12px; "
        "box-shadow:0 2px 6px rgba(0,0,0,0.2); border-radius:8px; "
        "border:1px solid #e0e0e0; min-width: 160px;'>"
        f"<div style='font-weight:700; margin-bottom:6px; font-size:13px;'>{title}</div>"
        f"{rows}"
        "</div></div>"
    )
    m.get_root().html.add_child(folium.Element(html))

# =========================
# 대시보드 타이틀
# =========================
ui.page_opts(title="대구광역시 내 침수 위험 지역 도출", fillable=True)

# =========================
# 6개 탭 구성
# =========================
with ui.navset_pill(id="tab"):

    # -----------------------------------
    # Tab 1: 결론/가중치 → 지도/검증
    # -----------------------------------
    with ui.nav_panel("침수 주의 지역 도출"):
        
        with ui.layout_columns(col_widths=(4, 6), gap="1.25rem", class_="align-items-center"):

            # (좌) 가중치 슬라이더
            with ui.card(class_="mx-auto h-100", style="min-width:260px; max-width:360px;"):
                ui.card_header("가중치 슬라이더")

                ui.input_action_button(
                    "btn3", "사용 방법", class_="btn-success",
                    style="font-size:13px; white-space:nowrap;"
                )

                @reactive.effect
                @reactive.event(input.btn3)
                def show_modal_btn3():
                    ui.modal_show(ui.modal(
                        ui.tags.img(src="howtouse.png", style="width:100%; height:auto;"),
                        title="",
                        easy_close=True,
                        footer=ui.modal_button("닫기"),
                        size="l"
                    ))

                # --- 날씨 요인 ---
                ui.h5("날씨 요인")
                ui.input_slider("w_rain", "강수량 리스크", min=0, max=10, value=9)

                # --- 지리적 요인 ---
                ui.h5("지리적 요인")
                ui.input_slider("w_pump", "빗물펌프장 리스크", min=0, max=10, value=6)
                ui.input_slider("w_lowland", "저지대 리스크", min=0, max=10, value=8)
                ui.input_slider("w_river", "하천 리스크", min=0, max=10, value=10)

                # --- 인구 요인 ---
                ui.h5("인구 요인")
                ui.input_slider("w_dens", "총 인구밀도", min=0, max=10, value=3)
                ui.input_slider("w_child", "어린이 인구밀도", min=0, max=10, value=2)
                ui.input_slider("w_old", "고령자 인구밀도", min=0, max=10, value=2)
                ui.input_slider("w_foreign", "외국인 인구밀도", min=0, max=10, value=1)

            # (우) 지도 + Top10 차트
            with ui.card():
                ui.card_header("리스크 스코어 지도")

                @render.ui
                def risk_map():
                    # ---- (A) 지도 기준 DF: geo_merged의 모든 동을 기준 ----
                    df = pd.DataFrame({"읍면동": geo_merged["읍면동"]})
                    df["dong_key"] = df["읍면동"].apply(norm_dong)

                    # ---- (B) 각 지표를 정규화 키로 병합 ----
                    def attach_metric(left, right, col_name):
                        tmp = right[["읍면동", col_name]].copy()
                        tmp["dong_key"] = tmp["읍면동"].apply(norm_dong)
                        return left.merge(tmp[["dong_key", col_name]], on="dong_key", how="left")

                    df = attach_metric(df, rainy_risk_dong, "RiskScore_norm")        # rain
                    df = attach_metric(df, oldest_pump,    "risk_score_norm")        # pump
                    df = attach_metric(df, elevation,      "elevation_diff_norm")    # lowland
                    df = attach_metric(df, dens,           "인구밀도_norm")          # dens

                    tmp_age = age_dong[["읍면동","어린이 인구밀도_norm","고령자 인구밀도_norm"]].copy()
                    tmp_age["dong_key"] = tmp_age["읍면동"].apply(norm_dong)
                    df = df.merge(
                        tmp_age[["dong_key","어린이 인구밀도_norm","고령자 인구밀도_norm"]],
                        on="dong_key", how="left"
                    )

                    df = attach_metric(df, fore_dong,      "외국인 인구밀도_norm")   # foreign

                    # 별칭 정리
                    df.rename(columns={
                        "RiskScore_norm": "rain",
                        "risk_score_norm": "pump",
                        "elevation_diff_norm": "lowland",
                        "인구밀도_norm": "dens",
                        "어린이 인구밀도_norm": "child",
                        "고령자 인구밀도_norm": "old",
                        "외국인 인구밀도_norm": "foreign",
                    }, inplace=True)

                    # ---- (C) 하천 리스크(포함=10, 미포함=0) ----
                    df["river"] = df["dong_key"].apply(lambda x: 10 if x in river_set_norm else 0)

                    # NaN -> 0
                    for c in ["rain","pump","lowland","dens","child","old","foreign"]:
                        if c in df.columns:
                            df[c] = df[c].fillna(0)

                    # ---- (D) 가중치 반영 ----
                    df["risk_score"] = (
                        df["rain"]      * (input.w_rain()    or 0)
                        + df["pump"]    * (input.w_pump()    or 0)
                        + df["lowland"] * (input.w_lowland() or 0)
                        + df["river"]   * (input.w_river()   or 0)
                        + df["dens"]    * (input.w_dens()    or 0)
                        + df["child"]   * (input.w_child()   or 0)
                        + df["old"]     * (input.w_old()     or 0)
                        + df["foreign"] * (input.w_foreign() or 0)
                    )

                    # ---- (E) 지도 시각화(키로 병합) ----
                    m = folium.Map(location=[35.87, 128.6], zoom_start=11)

                    merged = geo_merged.merge(
                        df[["dong_key","risk_score","river"]], on="dong_key", how="left"
                    )

                    vmin = merged["risk_score"].min()
                    vmax = merged["risk_score"].max()
                    if pd.isna(vmin) or pd.isna(vmax) or vmin == vmax:
                        vmin, vmax = 0, 1

                    colormap = folium.LinearColormap(
                        colors=["#f7fbff", "#6baed6", "#08306b"],
                        vmin=vmin, vmax=vmax, caption="종합 리스크 스코어"
                    )

                    # --------- ① 기본 리스크 스코어 색상 ---------
                    folium.GeoJson(
                        merged.to_json(),
                        style_function=lambda feature: {
                            "fillColor": colormap(feature["properties"].get("risk_score"))
                                        if feature["properties"].get("risk_score") is not None
                                        else "transparent",
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=folium.GeoJsonTooltip(
                            fields=["읍면동", "risk_score", "river"],
                            aliases=["읍면동", "리스크 스코어", "하천 리스크(0/10)"],
                            localize=True
                        )
                    ).add_to(m)

                    # --------- ② SVG 패턴 추가 (빗금) ---------
                    pattern = """
                    <svg height="0" width="0">
                    <defs>
                        <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="10" height="10">
                        <path d="M0,6 l6,-6
                                M-1,1 l2,-2
                                M5,7 l2,-2" 
                                style="stroke:red; stroke-width:1" />
                        </pattern>
                    </defs>
                    </svg>
                    """
                    m.get_root().html.add_child(folium.Element(pattern))

                    # --------- ③ 실제 침수 사고 지역 (빗금 처리) ---------
                    flood_areas = [
                        "이천동","신암동","칠성동","두산동","다사읍","현풍면","태전동","매호동",
                        "서호동","가창면","효령면","동촌동","관문동","두류동","죽전동","감삼동",
                        "유천동","삼국유사면","침산동","비산7동","신암2동"
                    ]

                    folium.GeoJson(
                        merged[merged["읍면동"].isin(flood_areas)].to_json(),
                        style_function=lambda feature: {
                            "fillColor": "url(#diagonalHatch)",  # 내부 빗금 채우기
                            "color": "red",                      # 경계선 빨강
                            "weight": 2,
                            "fillOpacity": 0.6
                        },
                        tooltip=folium.GeoJsonTooltip(
                            fields=["읍면동"],
                            aliases=["실제 침수 사고 지역"],
                            localize=True
                        )
                    ).add_to(m)

                    # --------- ④ 범례 추가 ---------
                    colormap.add_to(m)

                    legend_html = """
                    <div style="
                        position: fixed;
                        bottom: 0px; left: 0px; width: 200px; height: 80px;
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color:white; padding: 8px;">
                    <b>범례</b><br>
                    <span style="background:url(#diagonalHatch); color:red; font-weight:bold;">■■</span> 실제 침수 사고 지역
                    </div>
                    """
                    m.get_root().html.add_child(folium.Element(legend_html))

                    # --------- ⑤ UI 출력 ---------
                    return ui.HTML(m._repr_html_())

                @render.plot
                def risk_top10_plot():
                    # 지도와 동일 로직으로 스코어 계산(일관성)
                    base = pd.DataFrame({"읍면동": geo_merged["읍면동"]})
                    base["dong_key"] = base["읍면동"].apply(norm_dong)

                    def attach_metric(left, right, col_name):
                        tmp = right[["읍면동", col_name]].copy()
                        tmp["dong_key"] = tmp["읍면동"].apply(norm_dong)
                        return left.merge(tmp[["dong_key", col_name]], on="dong_key", how="left")

                    base = attach_metric(base, rainy_risk_dong, "RiskScore_norm")        # rain
                    base = attach_metric(base, oldest_pump,    "risk_score_norm")        # pump
                    base = attach_metric(base, elevation,      "elevation_diff_norm")    # lowland
                    base = attach_metric(base, dens,           "인구밀도_norm")          # dens

                    tmp_age = age_dong[["읍면동","어린이 인구밀도_norm","고령자 인구밀도_norm"]].copy()
                    tmp_age["dong_key"] = tmp_age["읍면동"].apply(norm_dong)
                    base = base.merge(
                        tmp_age[["dong_key","어린이 인구밀도_norm","고령자 인구밀도_norm"]],
                        on="dong_key", how="left"
                    )

                    base = attach_metric(base, fore_dong,      "외국인 인구밀도_norm")   # foreign

                    base.rename(columns={
                        "RiskScore_norm": "rain",
                        "risk_score_norm": "pump",
                        "elevation_diff_norm": "lowland",
                        "인구밀도_norm": "dens",
                        "어린이 인구밀도_norm": "child",
                        "고령자 인구밀도_norm": "old",
                        "외국인 인구밀도_norm": "foreign",
                    }, inplace=True)

                    base["river_risk"] = base["dong_key"].apply(lambda x: 10 if x in river_set_norm else 0)

                    for c in ["rain","pump","lowland","dens","child","old","foreign"]:
                        if c in base.columns:
                            base[c] = base[c].fillna(0)

                    base["종합리스크"] = (
                        (input.w_rain()    or 0) * base["rain"] +
                        (input.w_pump()    or 0) * base["pump"] +
                        (input.w_lowland() or 0) * base["lowland"] +
                        (input.w_river()   or 0) * base["river_risk"] +
                        (input.w_dens()    or 0) * base["dens"] +
                        (input.w_child()   or 0) * base["child"] +
                        (input.w_old()     or 0) * base["old"] +
                        (input.w_foreign() or 0) * base["foreign"]
                    )

                    top10 = base[['읍면동', '종합리스크']].dropna().sort_values(
                        by="종합리스크", ascending=False
                    ).head(10)

                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.barh(top10['읍면동'], top10['종합리스크'])
                    ax.set_xlabel("종합 위험 점수")
                    ax.set_ylabel("읍면동")
                    ax.set_title("고위험 Top 10 읍면동")
                    ax.invert_yaxis()
                    ax.grid(axis='x', linestyle='--', alpha=0.7)
                    return fig

    # -----------------------------------
    # Tab 2: 서론
    # -----------------------------------
    with ui.nav_panel("서론"):

        # ---------------- 첫 번째 카드 : 뉴스 3개 가로 배치 ----------------
        with ui.card():
            ui.card_header("최근 뉴스")

            with ui.layout_columns(col_widths=[4, 4, 4]):   # 3등분
                # 뉴스 1
                ui.tags.a(
                    ui.tags.img(
                        src="뉴스1.png",
                        style="width:100%; height:auto; margin-bottom:10px;"
                    ),
                    href="https://dgmbc.com/article/azqZOCv4cN?utm_",
                    target="_blank"
                )

                # 뉴스 2
                ui.tags.a(
                    ui.tags.img(
                        src="뉴스2.png",
                        style="width:100%; height:auto; margin-bottom:10px;"
                    ),
                    href="https://www.newsis.com/view/NISX20250717_0003256028?utm_",
                    target="_blank"
                )

                # 뉴스 3
                ui.tags.a(
                    ui.tags.img(
                        src="뉴스3.png",
                        style="width:100%; height:auto; margin-bottom:10px;"
                    ),
                    href="https://www.ynenews.kr/news/articleView.html?idxno=66722&utm_",
                    target="_blank"
                )


    # ---------------- 두 번째 카드 : 이미지 2개 가로 배치 ----------------
        with ui.card():
            ui.card_header("주제선정배경")

            with ui.layout_columns(col_widths=[6, 6]):   # 2등분
                # intro 1
                ui.tags.img(
                    src="intro1.png",
                    style="width:100%; height:auto; margin-bottom:10px;"
                )

                # intro 2
                ui.tags.img(
                    src="intro2.png",
                    style="width:100%; height:auto; margin-bottom:10px;"
                )

    # -----------------------------------
    # Tab 3: 날씨
    # -----------------------------------
    with ui.nav_panel("강수량 분석"):
        with ui.layout_columns():

            with ui.card():
                ui.card_header("대구시 장마기간에 의한 침수 위험도 분석")

                # plot 1
                ui.tags.img(
                    src="plot1.png",
                    style="width:100%; height:auto; margin-bottom:10px;"
                )

                # plot 2
                ui.tags.img(
                    src="plot2.png",
                    style="width:100%; height:auto; margin-bottom:10px;"
                )

                # plot 3
                ui.tags.img(
                    src="plot3.png",
                    style="width:100%; height:auto; margin-bottom:10px;"
                )




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
                    rainy_season_dong['년도'] = pd.to_datetime(
                        rainy_season_dong['기간시작']
                    ).dt.year.astype(str)
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
                                "color": "black",
                                "weight": 1,
                                "fillOpacity": 0.7,
                            },
                            tooltip=folium.Tooltip(f"{row['sggnm']}: {row['합계강수량']} mm")
                        )
                        geo_json.add_to(m)

                    colormap.add_to(m)
                    return ui.HTML(m._repr_html_())

    # -----------------------------------
    # Tab 4: 지리
    # -----------------------------------
    with ui.nav_panel("시설 및 지형 분석"):
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
                        if pd.isna(row['설치년도']):
                            year_str = "알수없음"
                        else:
                            year_str = str(int(row['설치년도']))

                        folium.Marker(
                            location=[row['위도 (Latitude)'], row['경도 (Longitude)']],
                            tooltip=f"{row['펌프장명']} ({year_str})",
                            icon=folium.Icon(color='blue', icon='tint', prefix='fa')
                        ).add_to(m)

                    # ★ 범례 추가
                    add_html_legend(
                        m, "범례",
                        items=[
                            ("행정경계(검정선)", "#000000"),
                            ("빗물펌프장(파란 핀)", "#2A81CB"),
                        ],
                        position="bottomright"
                    )

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
                    mask = pump_df['위치 (주소)'].str.contains(selected_region, na=False)

                    df_filtered = pump_df.loc[mask, ['펌프장명', '위치 (주소)', '설치년도']].copy()
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
                    elev_tmp = elevation[['읍면동','elevation_diff']].copy()
                    elev_tmp['dong_key'] = elev_tmp['읍면동'].apply(norm_dong)
                    geo_merged_elev = geo_merged_elev.merge(
                        elev_tmp[['dong_key','elevation_diff']], on='dong_key', how='left'
                    )

                    # 색상 함수 정의
                    def get_color(elevation_diff):
                        if elevation_diff is None or pd.isna(elevation_diff):
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

                    # ★ 범례 추가 (구간 설명)
                    lowland_items = [
                        ("< -15 (매우 낮음)", "#8B0000"),
                        ("-15 ~ -10", "#DC143C"),
                        ("-10 ~ -5", "#FF0000"),
                        ("-5 ~ 0", "#FF6347"),
                        ("0 ~ 5", "#87CEEB"),
                        ("5 ~ 10", "#4169E1"),
                        ("≥ 10 (높음)", "#00008B"),
                        ("값 없음", "#d3d3d3"),
                    ]
                    add_html_legend(m, "고도차(주변 대비, m)", lowland_items, position="bottomright")

                    return ui.HTML(m._repr_html_())

            with ui.card():
                ui.card_header("하천 인근 지역")

                @render.ui
                def river_near_map():
                    # 지도 생성 (대구 중심)
                    m = folium.Map(location=[35.87, 128.60], zoom_start=11, control_scale=True)

                    # 스타일 함수: 하이라이트 목록이면 빨강, 아니면 연회색
                    def style_fn(feature):
                        dong = feature["properties"].get("읍면동")
                        dong_key = norm_dong(dong)
                        if dong_key in river_set_norm:
                            return {
                                "fillColor": "#ff4d4f",
                                "color": "#b32025",
                                "weight": 1.2,
                                "fillOpacity": 0.6,
                            }
                        else:
                            return {
                                "fillColor": "#eeeeee",
                                "color": "#999999",
                                "weight": 0.8,
                                "fillOpacity": 0.25,
                            }

                    # GeoJSON 레이어 추가 (툴팁: 읍면동)
                    folium.GeoJson(
                        geo_merged.to_json(),
                        name="읍·면·동",
                        style_function=style_fn,
                        highlight_function=lambda f: {"weight": 2, "color": "#333333"},
                        tooltip=folium.GeoJsonTooltip(
                            fields=["읍면동"],
                            aliases=["읍·면·동"],
                            localize=True,
                        ),
                    ).add_to(m)

                    # ★ 범례 추가
                    add_html_legend(
                        m, "하천 인근 지역",
                        items=[
                            ("하천 인근 읍·면·동", "#ff4d4f"),
                            ("기타 지역", "#eeeeee"),
                        ],
                        position="bottomright"
                    )

                    folium.LayerControl(collapsed=False).add_to(m)
                    return ui.HTML(m._repr_html_())

    # -----------------------------------
    # Tab 5: 인구
    # -----------------------------------
    with ui.nav_panel("인구 분석"):
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
                ui.card_header("행정구 내 등록 인구 수")

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

                    df = pop[pop['행정구'] == selected_district].copy()

                    category_map = {
                        "총 인구": "인구(명)",
                        "어린이 인구": "어린이수",
                        "고령자 인구": "고령자수",
                        "외국인 인구": "외국인 인구(명)"
                    }
                    value_col = category_map[selected_category]

                    df_sorted = df.sort_values(by=value_col, ascending=True)
                    overall_mean = pop[value_col].mean()

                    fig, ax = plt.subplots(figsize=(8,6))
                    ax.barh(df_sorted['읍면동'], df_sorted[value_col], color='skyblue', edgecolor='black')
                    ax.axvline(overall_mean, color='red', linestyle='--', linewidth=1, label=f'{selected_category} 전체 평균')
                    ax.set_xlabel(selected_category)
                    ax.set_ylabel('읍면동')
                    ax.set_title(f"{selected_district} - {selected_category}")
                    ax.grid(axis='x', linestyle='--', alpha=0.7)
                    ax.legend(loc="lower right")
                    plt.tight_layout()
                    return fig
