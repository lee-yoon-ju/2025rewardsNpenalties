import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="2025년 서울고등학교 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# 파일 불러오기
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# 날짜 변환 및 기준일 추출
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
기준일 = df["날짜"].max()
st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")

# 학번 → 학년 추출
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]

# 점수 정리 및 상벌점 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# 상벌점에 해당하는 키워드 목록
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

# '상벌점 내역'이 포함된 열 이름 자동 탐색
target_cols = [col for col in df.columns if "상벌점 내역" in col]
if target_cols:
    df["상벌점 목록"] = df[target_cols[0]]
else:
    st.error("⚠️ '상벌점 내역'이 포함된 열을 찾을 수 없습니다.")

# 유효 키워드가 포함된 행만 필터링
df = df[df["상벌점 목록"].apply(lambda x: any(k in str(x) for k in valid_keywords))]

# 상점만 추출
df_상점 = df[df["구분"] == "상점"].copy()

# 표준화된 사유 생성
def 표준화된_사유(text):
    for kw in valid_keywords:
        if kw in str(text):
            return kw
    return "기타"

df_상점["사유요약"] = df_상점["상벌점 목록"].apply(표준화된_사유)

# 학년별 원그래프 시각화
st.subheader("학년별 상점 분포 (원그래프)")

for 학년 in sorted(df_상점["학년"].unique()):
    df_학년 = df_상점[df_상점["학년"] == 학년]
    counts = df_학년["사유요약"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"{학년}학년 상점 분포")
    ax.axis("equal")
    st.pyplot(fig)
