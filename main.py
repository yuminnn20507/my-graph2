import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("영화의 장르와 관객 수 사이의 분포와 관계를 살펴봅니다.")


# ==========================================
# 데이터 불러오기
# ==========================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 개봉일
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자 데이터
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    df.loc[
        df["genre"].isin(["", "nan", "None"]),
        "genre"
    ] = "미상"

    return df


df = load_data()


# ==========================================
# 그래프 1
# 장르별 영화 수
# ==========================================

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
    margin=dict(
        t=60,
        l=20,
        r=20,
        b=20
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")


# ==========================================
# 그래프 2
# 장르 → 영화별 총 관객 수
# ==========================================

st.divider()

st.header("🗂️ 그래프 2. 장르 안에 들어 있는 영화와 총 관객 수")

treemap_df = df.dropna(
    subset=["movieNm", "genre", "total_audi"]
).copy()

treemap_df = treemap_df[
    treemap_df["total_audi"] >= 0
].copy()

genre_total = (
    treemap_df
    .groupby("genre")["total_audi"]
    .sum()
)

genre_labels = genre_total.index.tolist()
genre_values = genre_total.values.tolist()

movie_labels = treemap_df["movieNm"].tolist()
movie_values = treemap_df["total_audi"].tolist()
movie_parents = treemap_df["genre"].tolist()

labels = (
    ["영화 전체"]
    + genre_labels
    + movie_labels
)

parents = (
    [""]
    + ["영화 전체"] * len(genre_labels)
    + movie_parents
)

values = (
    [treemap_df["total_audi"].sum()]
    + genre_values
    + movie_values
)

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
    height=750
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.write("")


# ==========================================
# 그래프 3
# 영화별 총 관객 수 분포
# ==========================================

st.divider()

st.header("📈 그래프 3. 영화별 총 관객 수 분포")

hist_df = df.dropna(
    subset=["movieNm", "total_audi"]
).copy()

hist_df = hist_df[
    hist_df["total_audi"] >= 0
].copy()

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
    most_common_count = int(
        bin_counts.max()
    )

else:
    bin_width = 1
    most_common_bin = None
    most_common_count = 0


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
    height=550
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

max_movie = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

st.markdown("### 💡 이 그래프로 알 수 있는 것")

if most_common_bin is not None:

    lower = most_common_bin.left
    upper = most_common_bin.right

    st.write(
        f"대부분의 영화는 **{lower:,.0f}명 ~ "
        f"{upper:,.0f}명** 구간에 가장 많이 몰려 있으며, "
        f"이 구간에는 **{most_common_count}편**의 영화가 있습니다."
    )

st.write(
    f"가장 관객이 많은 영화는 **{max_movie['movieNm']}**으로, "
    f"총 관객 수는 **{max_movie['total_audi']:,.0f}명**입니다."
)


# ==========================================
# 그래프 4
# 개봉일 스크린 수와 총 관객 수
# ==========================================

st.divider()

st.header("🔵 그래프 4. 개봉일 스크린 수와 총 관객 수의 관계")

st.write(
    "개봉일에 확보한 스크린 수와 영화의 총 관객 수 사이의 관계를 살펴봅니다."
)

scatter_df = df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi"
    ]
).copy()

scatter_df = scatter_df[
    (scatter_df["first_scrn"] >= 0) &
    (scatter_df["total_audi"] >= 0)
].copy()

fig4 = go.Figure()

for genre in sorted(
    scatter_df["genre"].unique()
):

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

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "개봉일 스크린 수가 많은 영화와 총 관객 수가 많은 영화가 "
    "어떤 관계를 보이는지 살펴볼 수 있습니다."
)


# ==========================================
# 그래프 5
# 장르별 총 관객 수 상자 그림
# ==========================================

st.divider()

st.header("📦 그래프 5. 장르별 총 관객 수 분포")

st.write(
    "영화가 10편 이상 있는 장르만 골라 "
    "총 관객 수의 분포와 이상치를 비교합니다."
)

box_df = df.dropna(
    subset=[
        "movieNm",
        "genre",
        "total_audi"
    ]
).copy()

box_df = box_df[
    box_df["total_audi"] >= 0
].copy()

genre_movie_counts = (
    box_df["genre"].value_counts()
)

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index.tolist()

box_df = box_df[
    box_df["genre"].isin(selected_genres)
].copy()

fig5 = go.Figure()

for genre in sorted(selected_genres):

    genre_df = box_df[
        box_df["genre"] == genre
    ].copy()

    fig5.add_trace(
        go.Box(
            y=genre_df["total_audi"],
            name=genre,
            boxpoints="outliers",
            jitter=0.25,
            pointpos=0,
            marker=dict(
                size=7,
                opacity=0.8
            ),
            customdata=genre_df[
                ["movieNm", "total_audi"]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "장르: " + genre + "<br>"
                "총 관객: %{customdata[1]:,}명"
                "<extra></extra>"
            ),
            boxmean=False
        )
    )

fig5.update_layout(
    title="장르별 총 관객 수 분포",
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    height=650,
    margin=dict(
        t=70,
        l=70,
        r=30,
        b=70
    ),
    hovermode="closest",
    showlegend=False
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "상자의 높이와 위치를 비교하면 장르별 총 관객 수의 "
    "전반적인 분포를 볼 수 있고, 상자 밖의 점은 해당 장르에서 "
    "분포에서 벗어난 영화를 확인할 수 있습니다."
)


# ==========================================
# 그래프 6
# 버블 그래프
# ==========================================

st.divider()

st.header("🫧 그래프 6. 개봉일 스크린 수와 총 관객 수의 버블 그래프")

st.write(
    "개봉일 스크린 수와 총 관객 수의 관계를 살펴보면서, "
    "버블 크기로 첫 주 관객 수까지 함께 비교합니다."
)

bubble_df = df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
).copy()

bubble_df = bubble_df[
    (bubble_df["first_scrn"] >= 0) &
    (bubble_df["total_audi"] >= 0) &
    (bubble_df["first_week_audi"] >= 0)
].copy()

fig6 = go.Figure()

max_first_week = bubble_df[
    "first_week_audi"
].max()

if max_first_week > 0:
    sizeref = (
        2.0 * max_first_week
        / (50 ** 2)
    )
else:
    sizeref = 1

for genre in sorted(
    bubble_df["genre"].unique()
):

    genre_df = bubble_df[
        bubble_df["genre"] == genre
    ].copy()

    fig6.add_trace(
        go.Scatter(
            x=genre_df["first_scrn"],
            y=genre_df["total_audi"],
            mode="markers",
            name=genre,
            marker=dict(
                size=genre_df["first_week_audi"],
                sizemode="area",
                sizeref=sizeref,
                sizemin=5,
                opacity=0.7
            ),
            customdata=genre_df[
                [
                    "movieNm",
                    "genre",
                    "first_week_audi"
                ]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "장르: %{customdata[1]}<br>"
                "개봉일 스크린 수: %{x:,}개<br>"
                "총 관객: %{y:,}명<br>"
                "첫 주 관객: %{customdata[2]:,}명"
                "<extra></extra>"
            )
        )
    )

fig6.update_layout(
    title="개봉일 스크린 수 × 총 관객 수 × 첫 주 관객",
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    height=700,
    margin=dict(
        t=70,
        l=70,
        r=30,
        b=70
    ),
    legend_title="장르",
    hovermode="closest"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "가로축은 개봉일 스크린 수, 세로축은 총 관객 수이며, "
    "버블이 클수록 첫 주 관객 수가 많은 영화입니다. "
    "개봉 규모, 첫 주 흥행, 장기적인 총 관객 규모를 "
    "함께 비교할 수 있습니다."
)


# ==========================================
# 그래프 7
# 제작 국가 → 장르 선버스트
# ==========================================

st.divider()

st.header("☀️ 그래프 7. 제작 국가와 장르의 영화 분포")

st.write(
    "제작 국가에서 장르로 내려가면서 영화가 어떻게 분포되어 있는지 살펴봅니다."
)

sunburst_df = df.dropna(
    subset=[
        "nation",
        "genre",
        "movieNm"
    ]
).copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .astype(str)
    .str.strip()
)

sunburst_df["genre"] = (
    sunburst_df["genre"]
    .astype(str)
    .str.strip()
)

sunburst_df.loc[
    sunburst_df["nation"].isin(
        ["", "nan", "None"]
    ),
    "nation"
] = "미상"

sunburst_df.loc[
    sunburst_df["genre"].isin(
        ["", "nan", "None"]
    ),
    "genre"
] = "미상"

sunburst_counts = (
    sunburst_df
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화편수")
)

labels = ["영화 전체"]
parents = [""]
values = [len(sunburst_df)]

nation_counts = (
    sunburst_df["nation"]
    .value_counts()
)

for nation in nation_counts.index:

    labels.append(nation)
    parents.append("영화 전체")
    values.append(
        int(nation_counts[nation])
    )

for _, row in sunburst_counts.iterrows():

    labels.append(row["genre"])
    parents.append(row["nation"])
    values.append(
        int(row["영화편수"])
    )

fig7 = go.Figure(
    go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        ),
        insidetextorientation="radial"
    )
)

fig7.update_layout(
    title="제작 국가 → 장르별 영화 분포",
    height=750,
    margin=dict(
        t=70,
        l=20,
        r=20,
        b=20
    )
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "제작 국가에서 장르로 내려가면서 "
    "각 국가와 장르에 영화가 몇 편씩 분포되어 있는지 "
    "한눈에 비교할 수 있습니다."
)


# ==========================================
# 그래프 8
# 10위권 체류 기간과 총 관객의 관계
# ==========================================

st.divider()

st.header(
    "🔵 그래프 8. "
    "내 질문: 10위권에 오래 머문 영화는 총 관객도 많은가"
)

scatter8_df = df.dropna(
    subset=[
        "movieNm",
        "days_in_top10",
        "total_audi"
    ]
).copy()

scatter8_df = scatter8_df[
    (scatter8_df["days_in_top10"] >= 0) &
    (scatter8_df["total_audi"] >= 0)
].copy()

fig8 = go.Figure()

fig8.add_trace(
    go.Scatter(
        x=scatter8_df["days_in_top10"],
        y=scatter8_df["total_audi"],
        mode="markers",
        marker=dict(
            size=10,
            opacity=0.75
        ),
        text=scatter8_df["movieNm"],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "10위권 체류 일수: %{x}일<br>"
            "총 관객: %{y:,}명"
            "<extra></extra>"
        )
    )
)

fig8.update_layout(
    title="내 질문: 10위권에 오래 머문 영화는 총 관객도 많은가",
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객 수",
    height=650,
    margin=dict(
        t=70,
        l=70,
        r=30,
        b=70
    ),
    hovermode="closest"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "오른쪽으로 갈수록 10위권에 오래 머문 영화이고, "
    "위로 갈수록 총 관객이 많은 영화입니다. "
    "두 값이 함께 증가하는 경향이 있는지 "
    "산점도의 전체적인 모양을 통해 살펴볼 수 있습니다."
)
