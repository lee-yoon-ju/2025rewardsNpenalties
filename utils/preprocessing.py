import re
import pandas as pd

def 정제_사유(텍스트):
    매핑표 = {
        "지각": "등교시간 지각",
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
    for 키, 표준 in 매핑표.items():
        if 키 in str(텍스트):
            return 표준
    return "기타"

def get_latest_scores(df):
    df = df.dropna(subset=["합산점수", "학번", "날짜"])
    df["합산점수"] = pd.to_numeric(df["합산점수"], errors="coerce")
    df = df.sort_values("날짜").groupby("학번", as_index=False).tail(1)
    df["학번"] = df["학번"].astype(str).str.zfill(5)
    df["학년"] = df["학번"].str[0]
    return df
