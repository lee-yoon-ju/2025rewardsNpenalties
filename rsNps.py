import streamlit as st
import pandas as pd
import plotly.express as px
import platform

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="2025년 서울고등학교 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# ✅ 파일 불러오기
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# ✅ 날짜 및 기준일 처리
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
기준일 = df["날짜"].max()
st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")

# ✅ 학번 → 학년 추출
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]

# ✅ 점수 및 상벌점 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# ✅ 분석 대상 키워드 목록
valid_keywords = [
    "교복 전체 미착용", "교복 일부를 갖추어 입지 않은 경우", "슬리퍼 등하교", "후문하차",
    "급식 관련 기초 질서를 지키지 않은 경우", "등교시간(07시50분) 지각", "수업태도가 불량한 경우",
    "공공질서를 위반하는 경우", "PM(개인이동형장치) 등하교", "교내에서 비품 및 공공기물 훼손(파손)",
    "교사의 정당한 지도에 불응", "교사에 예의를 갖추지 않은 언행", "명의도용",
    "교내외 학생 출입금지 구역 출입", "휴대폰 미제출", "자전거 하차 후 끌고 들어가지 않고 타고 가는 경우",
    "디텐션불참", "디텐션반성문미제출", "학교의 명예", "학습태도", "교육활동 도우미",
    "귀중품을 습득", "과벌점 사회봉사", "과벌점 교내봉사",
    "디텐션반성문제출", "디텐션1번 참여", "디텐션2번 참여", "디텐션3번 참여"
]

# ✅ '상벌점 내역' 열 자동 탐색
target_cols = [col for col in df.columns if "상벌점 내역" in col]
if target_cols:
    df["상벌점 목록"] = df[target_cols[0]]
else:
    st.error("⚠️ '상벌점 내역' 열을 찾을 수 없습니다.")

# ✅ 유효한 행만 필터링
df = df[df["상벌점 목록"].apply(lambda x: any(k in str(x) for k in valid_keywords))]

# ✅ 사유 요약 함수
def 요약사유(text):
    for kw in valid_keywords:
        if kw in str(text):
            return kw
    return "기타"

df["사유요약"] = df["상벌점 목록"].apply(요약사유)

# ✅ 사유 통합 함수 (5% 이하 → 기타)
def 통합사유빈도(df_group):
    counts = df_group["사유요약"].value_counts()
    total = counts.sum()
    result = counts[counts / total > 0.05]
    기타 = counts[counts / total <= 0.05].sum()
    if 기타 > 0:
        result["기타"] = 기타
    return result.reset_index().rename(columns={"index": "사유", "사유요약": "건수"})

# ✅ 학년 선택
st.subheader("학년별 상점 / 벌점 분포")
학년목록 = sorted(df["학년"].dropna().unique())
선택학년 = st.selectbox("학년을 선택하세요", options=학년목록)

# ✅ 상점 / 벌점 데이터 분리
df_학년 = df[df["학년"] == 선택학년]
df_상점 = df_학년[df_학년["구분"] == "상점"]
df_벌점 = df_학년[df_학년["구분"] == "벌점"]

# ✅ 사유 요약 및 기타 통합
df_상점_counts = 통합사유빈도(df_상점)
df_벌점_counts = 통합사유빈도(df_벌점)

# ✅ 그래프 나란히 출력
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**🎖️ {선택학년}학년 상점 분포 (총 {df_상점['사유요약'].count()}건)**")
    if df_상점_counts.empty:
        st.info("상점 데이터가 없습니다.")
    else:
        fig = px.pie(df_상점_counts, names="사유", values="건수", hole=0.3)
        fig.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"**⚠️ {선택학년}학년 벌점 분포 (총 {df_벌점['사유요약'].count()}건)**")
    if df_벌점_counts.empty:
        st.info("벌점 데이터가 없습니다.")
    else:
        fig = px.pie(df_벌점_counts, names="사유", values="건수", hole=0.3)
        fig.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig, use_container_width=True)
