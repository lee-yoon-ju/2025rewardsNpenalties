import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# ✅ 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux 또는 기타
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="2025년 서울고등학교 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# ✅ 파일 불러오기
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# ✅ 날짜 정리 및 기준일 표시
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
기준일 = df["날짜"].max()
st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")

# ✅ 학년 추출
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]

# ✅ 점수 처리 및 구분 생성
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# ✅ 필터링 키워드 목록
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

# ✅ '상벌점 내역'이 포함된 열 자동 추출
target_cols = [col for col in df.columns if "상벌점 내역" in col]
if target_cols:
    df["상벌점 목록"] = df[target_cols[0]]
else:
    st.error("⚠️ '상벌점 내역'이라는 문구가 포함된 열을 찾을 수 없습니다.")

# ✅ 유효 키워드 포함된 항목만 필터링
df = df[df["상벌점 목록"].apply(lambda x: any(k in str(x) for k in valid_keywords))]

# ✅ 사유 표준화 함수
def 표준화된_사유(text):
    for kw in valid_keywords:
        if kw in str(text):
            return kw
    return "기타"

# ✅ 상점 / 벌점 분리 및 사유 요약
df_상점 = df[df["구분"] == "상점"].copy()
df_상점["사유요약"] = df_상점["상벌점 목록"].apply(표준화된_사유)

df_벌점 = df[df["구분"] == "벌점"].copy()
df_벌점["사유요약"] = df_벌점["상벌점 목록"].apply(표준화된_사유)

# ✅ 학년 선택
st.subheader("학년별 상점 / 벌점 분포")
학년_리스트 = sorted(df["학년"].dropna().unique())
선택된_학년 = st.selectbox("학년을 선택하세요", options=학년_리스트)

# ✅ 선택 학년 필터링
df_상점_학년 = df_상점[df_상점["학년"] == 선택된_학년]
df_벌점_학년 = df_벌점[df_벌점["학년"] == 선택된_학년]

counts_상점 = df_상점_학년["사유요약"].value_counts()
counts_벌점 = df_벌점_학년["사유요약"].value_counts()

# ✅ 라벨: 횟수 (비율%)
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f"{count} ({pct:.1f}%)"
    return my_autopct

# ✅ 두 그래프 나란히 출력
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**🎖️ {선택된_학년}학년 상점 분포 (총 {counts_상점.sum()}건)**")
    if counts_상점.empty:
        st.info("상점 데이터가 없습니다.")
    else:
        fig, ax = plt.subplots()
        ax.pie(counts_상점, labels=counts_상점.index, autopct=make_autopct(counts_상점.values), startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

with col2:
    st.markdown(f"**⚠️ {선택된_학년}학년 벌점 분포 (총 {counts_벌점.sum()}건)**")
    if counts_벌점.empty:
        st.info("벌점 데이터가 없습니다.")
    else:
        fig, ax = plt.subplots()
        ax.pie(counts_벌점, labels=counts_벌점.index, autopct=make_autopct(counts_벌점.values), startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
