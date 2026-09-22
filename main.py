import streamlit as st
import pandas as pd
import numpy as np
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
# 구역 2. 장르 안 영화별 총 관객 - 트리맵
# ----------------------------------------------------------------------------
st.header("2. 장르 안 영화별 총 관객 (트리맵)")

treemap_df = df.dropna(subset=["genre", "movieNm", "total_audi"])

fig_treemap = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화의 총 관객 트리맵",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10))

st.plotly_chart(fig_treemap, use_container_width=True)
insight_box()

st.divider()

# ----------------------------------------------------------------------------
# 구역 3. 총 관객 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("3. 총 관객(total_audi) 분포")

hist_df = df.dropna(subset=["total_audi"])

fig_hist = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={"total_audi": "총 관객(명)"},
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(yaxis_title="영화 수(편)")

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 영화가 많이 몰린 구간과, 총 관객이 가장 많은 영화를 계산해서 문구로 표시
counts, bin_edges = np.histogram(hist_df["total_audi"], bins=20)
top_bin_idx = counts.argmax()
bin_start, bin_end = bin_edges[top_bin_idx], bin_edges[top_bin_idx + 1]

top_movie_row = hist_df.loc[hist_df["total_audi"].idxmax()]

st.markdown(
    f"📌 대부분의 영화는 총 관객 **{bin_start:,.0f}명 ~ {bin_end:,.0f}명** 구간에 "
    f"가장 많이 몰려 있습니다(해당 구간 영화 수: **{counts[top_bin_idx]}편**). "
    f"가장 관객이 많은 영화는 **'{top_movie_row['movieNm']}'**"
    f"(총 관객 **{top_movie_row['total_audi']:,.0f}명**)입니다."
)

insight_box()

st.divider()

# ----------------------------------------------------------------------------
# 구역 4. 개봉일 스크린수 vs 총 관객 - 산점도
# ----------------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

scatter_df = df.dropna(subset=["first_scrn", "total_audi", "genre", "movieNm"])

fig_scatter = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객(명)", "genre": "장르"},
)
fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>스크린수: %{x:,.0f}개<br>총 관객: %{y:,.0f}명<extra></extra>",
)

st.plotly_chart(fig_scatter, use_container_width=True)
insight_box()

st.divider()

# ----------------------------------------------------------------------------
# (다음 그래프는 이 아래에 같은 방식으로 구역을 추가하면 됩니다)
# 예: st.header("5. ...") -> 그래프 그리기 -> insight_box() -> st.divider()
# ----------------------------------------------------------------------------
