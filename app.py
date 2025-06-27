import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import 정제_사유, get_latest_scores

# --- 파일 경로 및 열 이름
파일경로 = "data/상벌점 목록.xlsx"
날짜열 = "날짜"  # K열 이름 (1행에 "날짜"로 적혀 있음)

# --- 데이터 불러오기
df = pd.read_excel(파일경로)
df.columns = df.columns.str.strip()

# --- 날짜 변환
df[날짜열] = pd.to_datetime(df[날짜열], format="%Y.%m.%d", errors="coerce")
df = df.dropna(subset=[날짜열])
# 날짜열은 K열로 명확히 지정
날짜열 = "날짜"

# 날짜 변환 (yyyy.mm.dd 형식 → datetime)
df[날짜열] = pd.to_datetime(df[날짜열], format="%Y.%m.%d", errors="coerce")

# 날짜 누락 제거
df = df.dropna(subset=[날짜열])

# 반영기간 추출
시작일 = df[날짜열].min()
종료일 = df[날짜열].max()

# 대시보드 상단에 출력
st.title("📊 2025년 서울고 벌점 통계")
st.markdown(f"**반영기간 : {시작일:%Y년 %m월 %d일} ~ {종료일:%Y년 %m월 %d일}**")


# --- 학번 정리
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]
df["반"] = df["학번"].str[1:3]
df["번호"] = df["학번"].str[3:5]

# --- 점수 및 상벌점 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# --- 상벌점 내역 열 찾기 및 사유 요약
상벌점열 = [col for col in df.columns if "상벌점" in col][0]
df["사유요약"] = df[상벌점열].apply(정제_사유)

# --- 요일 컬럼 생성
df["요일"] = df[날짜열].dt.day_name()

# --- Streamlit 구성
st.set_page_config(page_title="2025년 서울고 벌점 통계", layout="wide")
st.title("📊 2025년 서울고 벌점 통계")
st.markdown(f"**{반영기간}**")

# --- 학년 선택 UI
학년옵션 = sorted(df["학년"].unique())
선택학년 = st.selectbox("분석할 학년을 선택하세요", options=학년옵션)
df_선택 = df[df["학년"] == 선택학년]

# --- 📊 벌점 사유 분포 (원형 그래프)
벌점분포 = df_선택[df_선택["구분"] == "벌점"]["사유요약"].value_counts()
fig1 = px.pie(names=벌점분포.index, values=벌점분포.values, hole=0.4, title="❌ 벌점 사유 분포")
st.plotly_chart(fig1, use_container_width=True)

# --- 📅 요일별 벌점 (막대 그래프)
요일순 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
요일벌점 = df_선택[df_선택["구분"] == "벌점"]["요일"].value_counts().reindex(요일순, fill_value=0)
fig2 = px.bar(
    x=요일벌점.index,
    y=요일벌점.values,
    title="📅 요일별 벌점 발생 건수",
    labels={"x": "요일", "y": "건수"},
    color=요일벌점.index,
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig2, use_container_width=True)

# --- 📈 합산점수 구간 분석 (히스토그램)
df_합산 = get_latest_scores(df)
df_학년 = df_합산[df_합산["학년"] == 선택학년]

bins = [-100, -20, -10, 0, 10, 100]
labels = ["⚠ -20↓", "-19~-11", "-10~-1", "0~10", "11↑"]
df_학년["점수구간"] = pd.cut(df_학년["합산점수"], bins=bins, labels=labels)

fig3 = px.histogram(
    df_학년,
    x="점수구간",
    color="점수구간",
    title="🧮 합산점수 구간별 학생 수",
    text_auto=True,
    color_discrete_sequence=px.colors.sequential.Blues
)
st.plotly_chart(fig3, use_container_width=True)

# --- 🔍 원본 데이터 보기
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(df_선택.reset_index(drop=True))
