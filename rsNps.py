import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="2025년 서울고등학교 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("상벌점 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    # 데이터 불러오기
    df = pd.read_excel(uploaded_file)

    # 날짜 정리 및 기준일 설정
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    기준일 = df["날짜"].max()
    st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")

    # 학번 자릿수 맞추고 학년 추출
    df["학번"] = df["학번"].astype(str).str.zfill(5)
    df["학년"] = df["학번"].str[0]

    # 점수 정수형으로 변환
    df["점수"] = pd.to_numeric(df["점수"], errors="coerce")

    # 유효 상벌점 항목 키워드 정의
    keywords = [
        "교복 전체 미착용", "교복 일부를 갖추어 입지 않은 경우", "슬리퍼 등하교", "후문하차",
        "급식 관련 기초 질서를 지키지 않은 경우", "등교시간(07시50분) 지각", "수업태도가 불량한 경우",
        "공공질서를 위반하는 경우", "PM(개인이동형장치) 등하교", "교내에서 비품 및 공공기물 훼손(파손)",
        "교사의 정당한 지도에 불응", "교사에 예의를 갖추지 않은 언행", "명의도용", "교내외 학생 출입금지 구역 출입",
        "휴대폰 미제출", "자전거 하차 후 끌고 들어가지 않고 타고 가는 경우", "디텐션불참", "디텐션반성문미제출",
        "학교의 명예를 크게 드높인 경우", "학습태도나 생활태도의 성실함이 타의 모범인 경우", "교육활동 도우미를 한 경우",
        "귀중품을 습득하여 신고를 했을 때", "과벌점 사회봉사 5시간 실시", "과벌점 사회봉사 3시간 실시",
        "과벌점 교내봉사 5시간 실시", "과벌점 교내봉사 3시간 실시", "디텐션반성문제출",
        "디텐션1번 참여", "디텐션2번 참여", "디텐션3번 참여"
    ]

    # 유효 항목만 필터링
    def is_valid(text):
        return any(keyword in str(text) for keyword in keywords)

    df = df[df["상벌점 내역"].apply(is_valid)]

    # 상벌점 구분
    df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

    # 상점만 추출
    df_상점 = df[df["구분"] == "상점"]

    # 상점 사유 요약
    def 추출사유(text):
        for kw in keywords:
            if kw in text:
                return kw
        return "기타"

    df_상점["사유요약"] = df_상점["상벌점 내역"].apply(추출사유)

    st.subheader("학년별 상점 분포 (원그래프)")

    # 학년별 원그래프 시각화
    for 학년 in sorted(df_상점["학년"].unique()):
        df_학년 = df_상점[df_상점["학년"] == 학년]
        counts = df_학년["사유요약"].value_counts()

        fig, ax = plt.subplots()
        ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"{학년}학년 상점 분포")
        ax.axis("equal")
        st.pyplot(fig)
