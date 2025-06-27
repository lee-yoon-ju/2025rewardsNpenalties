import pandas as pd

def 정제_사유(텍스트):
    """
    입력된 상벌점 내역 텍스트에서 핵심 키워드를 기준으로 표준화된 사유로 변환합니다.
    """
    매핑표 = {
        "지각": "등교시간 지각",
        "등교시간": "등교시간 지각",
        "교복 전체": "교복 전체 미착용",
        "교복 일부": "교복 일부를 갖추어 입지 않은 경우",
        "슬리퍼": "슬리퍼 등하교",
        "후문하차": "후문하차",
        "급식": "급식 관련 기초 질서 위반",
        "태도": "수업태도가 불량한 경우",
        "공공질서": "공공질서를 위반",
        "PM": "PM 등하교",
        "파손": "공공기물 훼손",
        "불응": "정당한 지도 불응",
        "예의": "예의 부족한 언행",
        "명의도용": "명의도용",
        "출입금지": "출입금지 구역 출입",
        "휴대폰": "수업 중 휴대폰 사용",
        "자전거": "자전거 타고 등교",
        "디텐션불참": "디텐션불참",
        "반성문": "디텐션반성문 미제출"
    }
    텍스트 = str(텍스트)
    for 키워드, 표준 in 매핑표.items():
        if 키워드 in 텍스트:
            return 표준
    return "기타"

def get_latest_scores(df):
    """
    학번별로 가장 최근 날짜의 합산점수를 추출합니다.
    """
    날짜열 = [col for col in df.columns if "날짜" in col][0]
    점수열 = [col for col in df.columns if "합산점수" in col][0]

    df = df.dropna(subset=[점수열, "학번", 날짜열]).copy()
    df[점수열] = pd.to_numeric(df[점수열], errors="coerce")
    df[날짜열] = pd.to_datetime(df[날짜열], format="%Y.%m.%d", errors="coerce")

    df = df.sort_values(날짜열).groupby("학번", as_index=False).tail(1)
    df["학번"] = df["학번"].astype(str).str.zfill(5)
    df["학년"] = df["학번"].str[0]
    df["합산점수"] = df[점수열].fillna(0).astype(int)

    return df
