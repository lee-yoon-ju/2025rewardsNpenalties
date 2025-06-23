import streamlit as st
import pandas as pd
import plotly.express as px

# 📄 페이지 설정
st.set_page_config(page_title="2025년 서울고 상벌점 현황", layout="wide")
st.title("2025년 서울고등학교 상벌점 현황")

# 📁 엑셀 파일 로딩
file_path = "상벌점 목록.xlsx"
df = pd.read_excel(file_path)

# 📅 날짜 처리
df["날짜"] = pd.to_datetime(df["날짜"], format="%Y.%m.%d", errors="coerce")
기준일 = df["날짜"].max()
시작일 = df["날짜"].min()

if pd.isna(기준일):
    st.warning("⚠️ 날짜 변환에 실패했습니다.")
else:
    st.markdown(f"**기준일**: {기준일.strftime('%Y년 %m월 %d일')}")
    st.markdown(f"**반영 기간**: {시작일.strftime('%Y년 %m월 %d일')} ~ {기준일.strftime('%Y년 %m월 %d일')}")

# 🧑‍🎓 학번 → 학년
df["학번"] = df["학번"].astype(str).str.zfill(5)
df["학년"] = df["학번"].str[0]

# 🎖️ 점수 및 구분
df["점수"] = pd.to_numeric(df["점수"], errors="coerce")
df["구분"] = df["점수"].apply(lambda x: "상점" if x > 0 else "벌점" if x < 0 else "기타")

# ✅ 상벌점 사유 처리
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

target_col = next((col for col in df.columns if "상벌점 내역" in col), None)
if target_col:
    df["상벌점 목록"] = df[target_col]
else:
    st.error("⚠️ '상벌점 내역' 열이 없습니다.")

df = df[df["상벌점 목록"].apply(lambda x: any(k in str(x) for k in valid_keywords))]

def 요약사유(text):
    for kw in valid_keywords:
        if kw in str(text):
            return kw
    return "기타"

df["사유요약"] = df["상벌점 목록"].apply(요약사유)

# ✅ 상/벌점 분리
df_상점 = df[df["구분"] == "상점"]
df_벌점 = df[df["구분"] == "벌점"]

# ✅ 사유 통합 함수
def 통합사유(df_group):
    counts = df_group["사유요약"].value_counts()
    total = counts.sum()
    주요 = counts[counts / total > 0.05]
    기타 = counts[counts / total <= 0.05].sum()
    if 기타 > 0:
        주요["기타"] = 기타
    return 주요.reset_index().rename(columns={"index": "사유", 0: "건수"})

# 🎯 학년 선택
st.subheader("학년별 상점 / 벌점 분포")
학년_목록 = sorted(df["학년"].dropna().unique())
선택학년 = st.selectbox("학년을 선택하세요", options=학년_목록)

# 🔍 학년별 필터링
df_상점_학년 = df_상점[df_상점["학년"] == 선택학년]
df_벌점_학년 = df_벌점[df_벌점["학년"] == 선택학년]
df_상점_counts = 통합사유(df_상점_학년)
df_벌점_counts = 통합사유(df_벌점_학년)

# 🍩 상점/벌점 원그래프
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
    first_day = pd.Timestamp(year=year, month=month, day=1)
    week_number = ((dt - first_day).days // 7) + 1
    return f"{year}-{month:02d}-{week_number}주"

# 📊 주차별 벌점 추이
if not df_벌점_학년.empty:
    df_벌점_학년 = df_벌점_학년.copy()
    df_벌점_학년["주차"] = df_벌점_학년["날짜"].apply(get_week_label)

    start_date = pd.to_datetime("2025-03-01")
    all_weeks = pd.date_range(start=start_date, end=기준일, freq="W-SUN")
    all_week_labels = [get_week_label(d) for d in all_weeks]

    벌점_카운트 = df_벌점_학년["주차"].value_counts().reindex(all_week_labels, fill_value=0).sort_index()
    df_벌점_주별 = pd.DataFrame({"주차": all_week_labels, "건수": 벌점_카운트.values})

    st.markdown(f"**📊 {선택학년}학년 주별 벌점 추이**")
    fig_bar = px.bar(df_벌점_주별, x="주차", y="건수",
                     labels={"주차": "주차", "건수": "벌점 건수"})
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info(f"{선택학년}학년에는 벌점 데이터가 없습니다.")

# 📅 요일별 벌점 건수
if not df_벌점_학년.empty:
    st.markdown(f"**📅 {선택학년}학년 요일별 벌점 건수**")
    df_벌점_학년["요일"] = df_벌점_학년["날짜"].dt.day_name()
    df_벌점_학년 = df_벌점_학년[df_벌점_학년["요일"].isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])]
    요일순서 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        요일별_벌점 = df_벌점_학년["요일"].value_counts().reindex(요일순서, fill_value=0)
    최다요일 = 요일별_벌점.idxmax()

    df_요일 = pd.DataFrame({
        "요일": 요일별_벌점.index,
        "벌점건수": 요일별_벌점.values
    })
    df_요일["색상"] = df_요일["요일"].apply(lambda x: "red" if x == 최다요일 else "lightskyblue")

    fig_day = px.bar(
        df_요일,
        x="요일",
        y="벌점건수",
        color="색상",
        color_discrete_map="identity",
        labels={"요일": "Weekday", "벌점건수": "벌점 건수"},
        title=f"{선택학년}학년 요일별 벌점 발생 건수"
    )
    fig_day.update_layout(showlegend=False)
    st.plotly_chart(fig_day, use_container_width=True)
