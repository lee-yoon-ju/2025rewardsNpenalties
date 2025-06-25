import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="2025년 서울고 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# 파일 불러오기
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# 날짜 처리
df["날짜"] = pd.to_datetime(df["날짜"], format="%Y.%m.%d", errors="coerce")
기준일 = df["날짜"].max()
시작일 = df["날짜"].min()  # ✅ 이 줄을 추가하세요

if pd.isna(기준일):
    st.warning("⚠️ 날짜 변환에 실패했습니다.")
else:
    st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")
    st.markdown(f"**반영 기간**: {시작일.strftime('%Y년 %m월 %d일')} ~ {기준일.strftime('%Y년 %m월 %d일')}")  # ✅ 이 줄 추가
