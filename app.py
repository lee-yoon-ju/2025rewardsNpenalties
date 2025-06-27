import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import 정제_사유, get_latest_scores

# --- 데이터 로딩
df = pd.read_excel("data/상벌점 목록.xlsx")

# 날짜 처리
df["날짜"] = pd.to_datetime(df["날짜"], format="%Y.%m.%d", errors="coerce")

# 학번 분해
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]
df["반"] = df["학번"].str[1:3]

# 점수 처리 및 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# 사유 요약
df["사유요약"] = df["상벌점 내역"].apply(정제_사유)

# 🔹 주차 / 요일 / 학년 선택
학년옵션 = sorted(df["학년"].unique())
선택학년 = st.selectbox("📚 분석할 학년 선택", options=학년옵션)

# --- 📊 사유별 분포
df_선택 = df[df["학년"] == 선택학년]
벌점분포 = df_선택[df_선택["구분"] == "벌점"]["사유요약"].value_counts()

fig1 = px.pie(names=벌점분포.index, values=벌점분포.values, hole=0.4, title="벌점 사유 분포")
st.plotly_chart(fig1)

# --- 📅 요일 분석
df_선택["요일"] = df_선택["날짜"].dt.day_name()
요일_벌점 = df_선택[df_선택["구분"] == "벌점"]["요일"].value_counts().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], fill_value=0
)
최다 = 요일_벌점.idxmax()
색상 = ["red" if d == 최다 else "skyblue" for d in 요일_벌점.index]

fig2 = px.bar(x=요일_벌점.index, y=요일_벌점.values, color=색상,
              color_discrete_map="identity",
              title="📅 요일별 벌점 건수")
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2)

# --- 📈 합산점수 추출
df_합산 = get_latest_scores(df)
df_학년 = df_합산[df_합산["학년"] == 선택학년]

bins = [-100, -20, -10, 0, 10, 100]
labels = ["⚠ -20↓", "-19~-11", "-10~-1", "0~10", "11↑"]
df_학년["점수구간"] = pd.cut(df_학년["합산점수"], bins=bins, labels=labels)

fig3 = px.histogram(df_학년, x="점수구간", color="점수구간",
                    title="🧮 합산점수 구간별 학생 수")
st.plotly_chart(fig3)
