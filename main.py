import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    """CSV 데이터를 불러오고 기본 전처리를 수행합니다."""
    df = pd.read_csv(url)

    # genre 열에 세로막대(|) 기호로 여러 장르가 적혀 있으면 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # openDt(개봉일, 여덟 자리 숫자)를 날짜 형식으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


def insight_box(default_text: str = ""):
    """그래프 아래에 '이 그래프로 알 수 있는 것' 한 문장을 적는 자리를 만듭니다."""
    st.text_input(
        "💡 이 그래프로 알 수 있는 것",
        value=default_text,
        placeholder="이 그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    )


# ----------------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 데이터를 "
    "다양한 그래프로 살펴봅니다."
)

df = load_data(DATA_URL)

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# 구역 1. 장르별 영화 편수 - 도넛 그래프
# ----------------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
    .rename(columns={"count": "편수", "genre": "장르"})
)
# pandas 버전에 따라 value_counts().reset_index()의 열 이름이 다를 수 있어 보정
if "장르" not in genre_counts.columns:
    genre_counts.columns = ["장르", "편수"]

fig_genre = px.pie(
    genre_counts,
    names="장르",
    values="편수",
    hole=0.5,
    title="장르별 영화 편수",
)
fig_genre.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(legend_title_text="장르")

st.plotly_chart(fig_genre, use_container_width=True)
insight_box()

st.divider()

# ----------------------------------------------------------------------------
# (다음 그래프는 이 아래에 같은 방식으로 구역을 추가하면 됩니다)
# 예: st.header("2. ...") -> 그래프 그리기 -> insight_box() -> st.divider()
# ----------------------------------------------------------------------------
