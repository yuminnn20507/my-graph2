# ==========================================
# 그래프 8. 10위권 체류 기간과 총 관객의 관계
# ==========================================

st.divider()

st.header("🔵 그래프 8. 내 질문: 10위권에 오래 머문 영화는 총 관객도 많은가")

# 필요한 데이터만 준비
scatter8_df = df.dropna(
    subset=["movieNm", "days_in_top10", "total_audi"]
).copy()

# 정상적인 숫자 데이터만 사용
scatter8_df = scatter8_df[
    (scatter8_df["days_in_top10"] >= 0) &
    (scatter8_df["total_audi"] >= 0)
].copy()

# 산점도 생성
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

# 그래프 설명
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.write(
    "오른쪽으로 갈수록 10위권에 오래 머문 영화이고, "
    "위로 갈수록 총 관객이 많은 영화입니다. "
    "두 값이 함께 증가하는 경향이 있는지 산점도의 전체적인 모양을 통해 살펴볼 수 있습니다."
)
