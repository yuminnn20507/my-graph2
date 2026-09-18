import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# 제목
# =========================================================
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("영화의 장르와 관객 수 사이의 분포와 관계를 살펴봅니다.")


# =========================================================
# 데이터 불러오기
# =========================================================
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 개봉일
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 장르가 여러 개이면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 비어 있는 장르 처리
    df.loc[
        df["genre"].isin(["", "nan", "None"]),
        "genre"
    ] = "미상"

    return df


df = load_data()


# =========================================================
# 그래프 1
# 장르별 영화 수 - 도넛 차트
# =========================================================
st.header("📊 그래프 1. 장르별 영화 수")

genre_counts = df["genre"].value_counts()

fig1 = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts.index,
            values=genre_counts.values,
            hole=0.55,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "영화 편수: %{value}편<br>"
                "비율: %{percent}"
                "<extra></extra>"
            )
        )
    ]
)

fig1.update_layout(
    title="장르별 영화 분포",
    margin=dict(t=60, l=20, r=20, b=20)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")


# =========================================================
# 그래프 2
# 장르 → 영화 트리맵
# =========================================================
st.divider()

st.header("🌳 그래프 2. 장르별 영화와 총 관객 수")

st.write(
    "각 장르 안에 영화가 들어 있으며, "
    "칸의 크기는 총 관객 수를 나타냅니다."
)


# ---------------------------------------------------------
# 트리맵용 데이터 만들기
# ---------------------------------------------------------

# 총 관객이 없는 영화는 제외
treemap_df = df.dropna(
    subset=["movieNm", "genre", "total_audi"]
).copy()

# 총 관객이 음수인 이상 데이터 제거
treemap_df = treemap_df[
    treemap_df["total_audi"] >= 0
].copy()


# 장르별 총 관객 수
genre_total = (
    treemap_df
    .groupby("genre", as_index=False)["total_audi"]
    .sum()
)


# 장르 노드
genre_labels = genre_total["genre"].tolist()
genre_parents = ["영화 전체"] * len(genre_labels)
genre_values = genre_total["total_audi"].tolist()


# 영화 노드
movie_labels = treemap_df["movieNm"].tolist()
movie_parents = treemap_df["genre"].tolist()
movie_values = treemap_df["total_audi"].tolist()


# 전체 데이터 합치기
labels = ["영화 전체"] + genre_labels + movie_labels
parents = [""] + genre_parents + movie_parents
values = [treemap_df["total_audi"].sum()] + genre_values + movie_values


# ---------------------------------------------------------
# 트리맵 그리기
# ---------------------------------------------------------
fig2 = go.Figure(
    go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",

        # 영화명과 총 관객을 마우스 오버로 표시
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        ),

        # 화면 안에는 영화명을 표시
        textinfo="label",

        # 너무 작은 칸의 글자는 자동으로 숨김
        insidetextfont=dict(size=13),

        # 트리맵의 가장 바깥 영역
        root_color="lightgray"
    )
)


fig2.update_layout(
    title="장르 안에 들어 있는 영화와 총 관객 수",
    margin=dict(t=60, l=10, r=10, b=10),
    height=750
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


# ---------------------------------------------------------
# 그래프 2 해석 공간
# ---------------------------------------------------------
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")


# =========================================================
# 그래프 3
# 앞으로 추가할 그래프
# =========================================================

st.divider()

st.header("📈 그래프 3")
st.write("다음 그래프를 여기에 추가합니다.")

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")
