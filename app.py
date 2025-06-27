import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import 정제_사유, get_latest_scores

# --- 파일 경로 설정
파일경로 = "data/상벌점 목록.xlsx"
날짜열 = "날짜"  # K열: 정확히 '날짜'라는 열 이름이 1행에 있어야 함

# --- 데이터 불러오기 및 전처리
df = pd.read_excel(파일경로)
df.columns = df.columns.str.strip()

# 날짜 변환
df[날짜열] = pd.to_datetime(df[날짜열], format="%Y.%m.%d", errors="coerce")
df = df.dropna(subset=[날짜열])

# 반영기간 계산
시작일 = df[날짜열].min()
종료일 = df[날짜열].max()
반영기간 = f"반영기간 : {시작일:%Y년 %m월 %d일} ~ {종료일:%Y년 %m월 %d일}"

# 학번 구조 분해
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]
df["반"] = df["학번"].str[1:3]
df["번호"] = df["학번"].str[3:5]

# 점수 처리
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# 상벌점 내역 열 자동 탐색 및 사유 요약 처리
상벌점열 = [col for col in df.columns if "상벌점" in col][0]
df["사유요약"] = df[상벌점열].apply(정제_사유)

# 요일 추출
df["요일"] = df[날짜열].dt.day_name()

# --- Streamlit UI 구성
st.set_page_config(page_title="2025년 서울고 벌점 통계", layout="wide")
st.title("📊 2025년 서울고 벌점 통계")
st.markdown(f"**{반영기간}**")

# --- 시각화 1: 벌점 사유 분포 (Pie)
벌점사유 = df[df["구분"] == "벌점"]["사유요약"].value_counts()
fig1 = px.pie(
    names=벌점사유.index,
    values=벌점사유.values,
    hole=0.4,
    title="❌ 전체 벌점 사유 비율"
)
st.plotly_chart(fig1, use_container_width=True)

# --- 시각화 2: 요일별 벌점 분포 (Bar)
요일순 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
요일벌점 = df[df["구분"] == "벌점"]["요일"].value_counts().reindex(요일순, fill_value=0)
fig2 = px.bar(
    x=요일벌점.index,
    y=요일벌점.values,
    title="📅 요일별 벌점 발생 건수",
    labels={"x": "요일", "y": "건수"},
    color=요일벌점.index,
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig2, use_container_width=True)

# --- 시각화 3: 합산점수 구간별 학생 수 (Histogram)
df_합산 = get_latest_scores(df)
bins = [-100, -20, -10, 0, 10, 100]
labels = ["⚠ -20↓", "-19~-11", "-10~-1", "0~10", "11↑"]
df_합산["점수구간"] = pd.cut(df_합산["합산점수"], bins=bins, labels=labels)

fig3 = px.histogram(
    df_합산,
    x="점수구간",
    color="점수구간",
    text_auto=True,
    title="🧮 합산점수 구간별 학생 수",
    color_discrete_sequence=px.colors.sequential.Blues
)
st.plotly_chart(fig3, use_container_width=True)

# --- 원본 데이터 보기
with st.expander("📋 전체 데이터 보기"):
    st.dataframe(df.reset_index(drop=True))
