import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import 정제_사유, get_latest_scores

# --- 파일 경로
파일경로 = "data/상벌점 목록.xlsx"

# --- 데이터 로딩
df = pd.read_excel(파일경로)

# --- 열 이름 전처리 및 식별
df.columns = df.columns.str.strip()
상벌점열 = [col for col in df.columns if "상벌점" in col][0]
날짜열 = [col for col in df.columns if "날짜" in col][0]

# --- 날짜 처리
df[날짜열] = pd.to_datetime(df[날짜열], format="%Y.%m.%d", errors="coerce")
df = df.dropna(subset=[날짜열])

# --- 반영기간 추출
시작일 = df[날짜열].min()
종료일 = df[날짜열].max()
반영기간 = f"반영기간 : {시작일:%Y년 %m월 %d일} ~ {종료일:%Y년 %m월 %d일}"

# --- 학번 처리
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]
df["반"] = df["학번"].str[1:3]
df["번호"] = df["학번"].str[3:5]

# --- 점수 및 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# --- 사유 정제
df["사유요약"] = df[상벌점열].apply(정제_사유)

# --- 요일
df["요일"] = df[날짜열].dt.day_name()

# --- Streamlit 화면 구성
st.set_page_config("2025년 서울고 벌점 통계", layout="wide")
st.title("📊 2025년 서울고 벌점 통계")
st.markdown(f"**{반영기간}**")

# --- 학년 선택
학년목록 = sorted(df["학년"].unique())
선택학년 = st.selectbox("분석할 학년을 선택하세요", options=학년목록)

df_선택 = df[df["학년"] == 선택학년]

# --- Pie Chart: 벌점 사유 분포
벌점사유 = df_선택[df_선택["구분"] == "벌점"]["사유요약"].value_counts()
fig1 = px.pie(
    names=벌점사유.index,
    values=벌점사유.values,
    hole=0.4,
    title="❌ 벌점 사유 비율"
)
st.plotly_chart(fig1, use_container_width=True)

# --- Bar Chart: 요일별 벌점
요일순서 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
요일벌점 = df_선택[df_선택["구분"] == "벌점"]["요일"].value_counts().reindex(요일순서, fill_value=0)

fig2 = px.bar(
    x=요일벌점.index,
    y=요일벌점.values,
    title="📅 요일별 벌점 건수",
    labels={"x": "요일", "y": "건수"},
    color=요일벌점.index,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig2, use_container_width=True)

# --- Histogram: 학번별 최신 합산점수 분포
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

# --- 원본 데이터 보기
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(df_선택.reset_index(drop=True))
