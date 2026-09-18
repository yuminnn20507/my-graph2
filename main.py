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
# 트리맵용 데이터
# ---------------------------------------------------------
treemap_df = df.dropna(
    subset=["movieNm", "genre", "total_audi"]
).copy()

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


# 전체 데이터
labels = ["영화 전체"] + genre_labels + movie_labels
parents = [""] + genre_parents + movie_parents
values = [
    treemap_df["total_audi"].sum()
] + genre_values + movie_values


# ---------------------------------------------------------
# 트리맵 그리기
# ---------------------------------------------------------
fig2 = go.Figure(
    go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",

        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        ),

        textinfo="label",
        insidetextfont=dict(size=13),
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
# 총 관객 수 히스토그램
# =========================================================
st.divider()

st.header("📊 그래프 3. 영화별 총 관객 수 분포")

st.write(
    "영화별 총 관객 수가 어느 구간에 많이 몰려 있는지 확인합니다."
)


# ---------------------------------------------------------
# 히스토그램용 데이터
# ---------------------------------------------------------
hist_df = df.dropna(
    subset=["movieNm", "total_audi"]
).copy()

hist_df = hist_df[
    hist_df["total_audi"] >= 0
].copy()


# ---------------------------------------------------------
# 관객 수 최솟값 / 최댓값
# ---------------------------------------------------------
min_audience = hist_df["total_audi"].min()
max_audience = hist_df["total_audi"].max()

bin_count = 10


if max_audience > min_audience:

    bin_width = (
        max_audience - min_audience
    ) / bin_count

    hist_df["관객구간"] = pd.cut(
        hist_df["total_audi"],
        bins=bin_count
    )

    bin_counts = (
        hist_df["관객구간"]
        .value_counts()
        .sort_index()
    )

    most_common_bin = bin_counts.idxmax()
    most_common_count = bin_counts.max()

else:
    bin_width = 1
    most_common_bin = None
    most_common_count = len(hist_df)


# ---------------------------------------------------------
# 히스토그램
# ---------------------------------------------------------
fig3 = go.Figure()

fig3.add_trace(
    go.Histogram(
        x=hist_df["total_audi"],
        xbins=dict(
            start=min_audience,
            end=max_audience,
            size=bin_width
        ),
        hovertemplate=(
            "총 관객 구간: %{x}<br>"
            "영화 수: %{y}편"
            "<extra></extra>"
        )
    )
)

fig3.update_layout(
    title="영화별 총 관객 수 분포",
    xaxis_title="총 관객 수",
    yaxis_title="영화 수",
    bargap=0.05,
    margin=dict(t=60, l=60, r=30, b=60),
    height=550
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# =========================================================
# 그래프 3 해석
# =========================================================
max_movie_row = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = max_movie_row["movieNm"]
max_movie_audience = int(max_movie_row["total_audi"])


st.markdown("### 💡 이 그래프로 알 수 있는 것")

if most_common_bin is not None:

    lower = most_common_bin.left
    upper = most_common_bin.right

    st.write(
        f"대부분의 영화는 **{lower:,.0f}명 ~ {upper:,.0f}명** "
        f"구간에 가장 많이 몰려 있으며, "
        f"이 구간에는 **{most_common_count}편**의 영화가 있습니다."
    )

else:

    st.write(
        "영화들의 총 관객 수가 같은 값으로 나타납니다."
    )


st.write(
    f"가장 관객이 많은 영화는 **{max_movie_name}**으로, "
    f"총 관객 수는 **{max_movie_audience:,}명**입니다."
)


# =========================================================
# 그래프 4
# 개봉일 스크린 수 ↔ 총 관객 수 산점도
# =========================================================
st.divider()

st.header("🔵 그래프 4. 개봉일 스크린 수와 총 관객 수의 관계")

st.write(
    "개봉일에 확보한 스크린 수와 영화의 총 관객 수 사이의 "
    "관계를 살펴봅니다."
)


# ---------------------------------------------------------
# 산점도용 데이터
# ---------------------------------------------------------
scatter_df = df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi"
    ]
).copy()

# 정상적인 값만 사용
scatter_df = scatter_df[
    (scatter_df["first_scrn"] >= 0) &
    (scatter_df["total_audi"] >= 0)
].copy()


# ---------------------------------------------------------
# 산점도 만들기
# ---------------------------------------------------------
fig4 = go.Figure()


# 장르별로 하나씩 그래프를 만들어
# 장르마다 다른 색이 나타나도록 함
for genre in sorted(scatter_df["genre"].unique()):

    genre_df = scatter_df[
        scatter_df["genre"] == genre
    ]

    fig4.add_trace(
        go.Scatter(
            x=genre_df["first_scrn"],
            y=genre_df["total_audi"],

            mode="markers",

            name=genre,

            marker=dict(
                size=10,
                opacity=0.75
            ),

            # 마우스를 올렸을 때 표시할 영화명
            text=genre_df["movieNm"],

            hovertemplate=(
                "<b>%{text}</b><br>"
                "장르: " + genre + "<br>"
                "개봉일 스크린 수: %{x:,}개<br>"
                "총 관객: %{y:,}명"
                "<extra></extra>"
            )
        )
    )


# ---------------------------------------------------------
# 그래프 모양 설정
# ---------------------------------------------------------
fig4.update_layout(
    title="개봉일 스크린 수와 총 관객 수",
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",

    margin=dict(
        t=70,
        l=70,
        r=30,
        b=70
    ),

    height=650,

    legend_title="장르",

    hovermode="closest"
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


# ---------------------------------------------------------
# 그래프 4 해석 공간
# ---------------------------------------------------------
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린 수가 많은 영화와 총 관객 수가 많은 영화가 "
    "어떤 관계를 보이는지 살펴볼 수 있습니다."
)


# =========================================================
# 그래프 5
# 앞으로 추가할 그래프
# =========================================================

st.divider()

st.header("📈 그래프 5")
st.write("다음 그래프를 여기에 추가합니다.")

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")
