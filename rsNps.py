import streamlit as st
import pandas as pd
import plotly.express as px

# 📌 페이지 설정
st.set_page_config(page_title="2025년 서울고 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# 📂 파일 불러오기
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# 📅 날짜 변환
df["날짜"] = pd.to_datetime(df["날짜"], format="%Y.%m.%d", errors="coerce")
시작일 = df["날짜"].min()
기준일 = df["날짜"].max()

if pd.isna(기준일) or pd.isna(시작일):
    st.warning("⚠️ 날짜 열 변환에 실패했습니다.")
else:
    st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")
    st.markdown(f"**반영 기간**: {시작일.strftime('%Y년 %m월 %d일')} ~ {기준일.strftime('%Y년 %m월 %d일')}")

# 🧑‍🎓 학년 추출
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]

# 🎖️ 점수 처리
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# 🔍 '상벌점 내역' 열 감지
target_col = next((col for col in df.columns if "상벌점 내역" in col), None)
if target_col:
    df["상벌점 목록"] = df[target_col]
else:
    st.error("⚠️ '상벌점 내역' 열을 찾을 수 없습니다.")

# 🎯 유효 키워드 및 사유 요약
valid_keywords = ["지각", "복장", "휴대폰", "디텐션", "파손", "예의", "PM", "도우미", "사회봉사", "교내봉사", "수업태도", "출입", "귀중품", "후문하차", "슬리퍼"]
df = df[df["상벌점 목록"].apply(lambda x: any(k in str(x) for k in valid_keywords))]

def 요약사유(text):
    for kw in valid_keywords:
        if kw in str(text):
            return kw
    return "기타"

df["사유요약"] = df["상벌점 목록"].apply(요약사유)

# 🎯 상점 / 벌점 분리
df_상점 = df[df["구분"] == "상점"]
df_벌점 = df[df["구분"] == "벌점"]

# 🧮 기타 통합
def 통합사유(df_group):
    counts = df_group["사유요약"].value_counts()
    total = counts.sum()
    주요 = counts[counts / total > 0.05]
    기타 = counts[counts / total <= 0.05].sum()
    if 기타 > 0:
        주요["기타"] = 기타
    return 주요.reset_index().rename(columns={"index": "사유", 0: "건수"})

# 🔽 학년 선택
st.subheader("학년별 상점 / 벌점 분포")
학년_목록 = sorted(df["학년"].dropna().unique())
선택학년 = st.selectbox("학년을 선택하세요", options=학년_목록)

df_상점_학년 = df_상점[df_상점["학년"] == 선택학년]
df_벌점_학년 = df_벌점[df_벌점["학년"] == 선택학년]

df_상점_counts = 통합사유(df_상점_학년)
df_벌점_counts = 통합사유(df_벌점_학년)

# 🍩 원그래프 (수직 배치)
st.markdown(f"**🎖️ {선택학년}학년 상점 분포 (총 {len(df_상점_학년)}건)**")
if df_상점_counts.empty:
    st.info("상점 데이터가 없습니다.")
else:
    fig = px.pie(df_상점_counts, names="사유", values="건수", hole=0.3)
    fig.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig, use_container_width=True)

st.markdown(f"**⚠️ {선택학년}학년 벌점 분포 (총 {len(df_벌점_학년)}건)**")
if df_벌점_counts.empty:
    st.info("벌점 데이터가 없습니다.")
else:
    fig = px.pie(df_벌점_counts, names="사유", values="건수", hole=0.3)
    fig.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig, use_container_width=True)

# 📆 주차 라벨 함수
def get_week_label(dt):
    year = dt.year
    month = dt.month
    first_day = pd.Timestamp(year, month, 1)
    week_number = ((dt - first_day).days // 7) + 1
    return f"{year}-{month:02d}-{week_number}주"

# 📊 주별 벌점 추이 (막대그래프)
if not df_벌점_학년.empty:
    df_벌점_학년 = df_벌점_학년.copy()
    df_벌점_학년["주차"] = df_벌점_학년["날짜"].apply(get_week_label)

    all_weeks = pd.date_range(start=시작일, end=기준일, freq="W-SUN")
    all_week_labels = [get_week_label(d) for d in all_weeks]

    벌점_카운트 = df_벌점_학년["주차"].value_counts().reindex(all_week_labels, fill_value=0).sort_index()
    df_벌점_주별 = pd.DataFrame({"주차": all_week_labels, "건수": 벌점_카운트.values})

    st.markdown(f"**📊 {선택학년}학년 주별 벌점 건수**")
    fig = px.bar(df_벌점_주별, x="주차", y="건수",
                 labels={"주차": "주차", "건수": "벌점 건수"})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"{선택학년}학년에는 벌점 데이터가 없습니다.")

# 📚 합산점수 구간별 분포 (학년 기준 + 색상)
st.markdown(f"**📚 {선택학년}학년 최신 합산점수 구간별 학생 수 분포**")

합산점수_col = df.columns[8]
df_학년별 = df[df["학년"] == 선택학년]
df_합산 = df_학년별.dropna(subset=[합산점수_col, "이름", "날짜"])
df_합산 = df_합산.sort_values("날짜").groupby("이름", as_index=False).tail(1)
df_합산["점수"] = pd.to_numeric(df_합산[합산점수_col], errors="coerce").fillna(0).astype(int)

def make_custom_bin(score):
    if score <= -20:
        return "≤-20"
    elif -19 <= score <= -15:
        return "-19~-15"
    elif -14 <= score <= -10:
        return "-14~-10"
    elif -9 <= score <= -5:
        return "-9~-5"
    elif -4 <= score <= 0:
        return "-4~0"
    else:
        bin_start = ((score - 1) // 5) * 5 + 1
        bin_end = bin_start + 4
        return
