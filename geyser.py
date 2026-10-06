import math
from statistics import stdev

import plotly.graph_objects as go
import seaborn as sns
import streamlit as st


st.set_page_config(
    page_title="Old Faithful | Geyser Monitor",
    page_icon="🌋",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #202b28;
        --muted: #687571;
        --paper: #f4f5f1;
        --line: #dce2dc;
        --green: #177e69;
        --coral: #d9634d;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #e9eee8; }
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; }
    .eyebrow {
        color: var(--green); font-size: .76rem; font-weight: 700;
        text-transform: uppercase;
    }
    h1, h2, h3 { color: var(--ink); }
    div[data-testid="stMetric"] {
        background: #fff; border: 1px solid var(--line); border-radius: 6px;
        padding: 1rem 1.1rem;
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--ink); }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=86_400)
def load_geyser_data():
    data = sns.load_dataset("geyser")
    required = {"duration", "waiting"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"필수 데이터 열이 없습니다: {', '.join(sorted(missing))}")

    data = data.dropna(subset=["duration", "waiting"]).copy()
    if "kind" not in data.columns:
        data["kind"] = data["duration"].map(lambda value: "long" if value >= 3 else "short")
    data["kind"] = data["kind"].astype(str).str.lower()
    return data


def estimate_density(values: list[float], points: int = 160) -> tuple[list[float], list[float]]:
    """Estimate a Gaussian kernel density without an extra runtime dependency."""
    low, high = min(values), max(values)
    spread = high - low
    if len(values) < 2 or spread == 0:
        return [low, high], [0.0, 0.0]

    bandwidth = max(1.06 * stdev(values) * len(values) ** -0.2, spread / points)
    x_values = [low + spread * index / (points - 1) for index in range(points)]
    scale = 1 / (len(values) * bandwidth * math.sqrt(2 * math.pi))
    y_values = [
        scale * sum(math.exp(-0.5 * ((x_value - value) / bandwidth) ** 2) for value in values)
        for x_value in x_values
    ]
    return x_values, y_values


try:
    geyser = load_geyser_data()
except Exception as error:
    st.error(f"geyser 데이터를 불러오지 못했습니다: {error}")
    st.info("Seaborn 데이터셋을 처음 불러올 때 인터넷 연결이 필요할 수 있습니다.")
    st.stop()


st.sidebar.markdown('<div class="eyebrow">데이터 필터</div>', unsafe_allow_html=True)
st.sidebar.header("관측 조건")
kind_options = ["전체", *[kind for kind in ("long", "short") if kind in geyser["kind"].unique()]]
selected_kind = st.sidebar.selectbox("분출 유형", kind_options)

duration_min, duration_max = float(geyser["duration"].min()), float(geyser["duration"].max())
waiting_min, waiting_max = float(geyser["waiting"].min()), float(geyser["waiting"].max())
duration_range = st.sidebar.slider(
    "분출 지속 시간 (분)",
    min_value=duration_min,
    max_value=duration_max,
    value=(duration_min, duration_max),
    step=0.1,
    format="%.1f",
)
waiting_range = st.sidebar.slider(
    "대기 시간 (분)",
    min_value=waiting_min,
    max_value=waiting_max,
    value=(waiting_min, waiting_max),
    step=1.0,
    format="%.0f",
)

filtered = geyser[
    geyser["duration"].between(*duration_range)
    & geyser["waiting"].between(*waiting_range)
]
if selected_kind != "전체":
    filtered = filtered[filtered["kind"] == selected_kind]

st.markdown('<div class="eyebrow">Yellowstone National Park · Old Faithful</div>', unsafe_allow_html=True)
st.title("간헐천 분출 패턴")
st.caption("분출 지속 시간과 다음 분출까지의 대기 시간을 필터링해 관측 패턴을 살펴봅니다.")

long_share = (filtered["kind"] == "long").mean() * 100 if not filtered.empty else 0
short_share = (filtered["kind"] == "short").mean() * 100 if not filtered.empty else 0
kpis = st.columns(4)
kpis[0].metric("관측 건수", f"{len(filtered):,}")
kpis[1].metric("평균 분출 시간", f"{filtered['duration'].mean():.2f}분" if not filtered.empty else "—")
kpis[2].metric("평균 대기 시간", f"{filtered['waiting'].mean():.1f}분" if not filtered.empty else "—")
kpis[3].metric("Long / Short 비중", f"{long_share:.0f}% / {short_share:.0f}%")

if filtered.empty:
    st.warning("선택한 조건에 맞는 관측값이 없습니다. 사이드바 필터를 조정해 주세요.")
else:
    scatter_column, histogram_column = st.columns(2, gap="large")
    with scatter_column:
        st.subheader("분출 시간과 대기 시간")
        scatter = go.Figure()
        scatter.add_trace(
            go.Histogram2dContour(
                x=filtered["duration"],
                y=filtered["waiting"],
                colorscale=[[0, "rgba(23,126,105,0)"], [1, "rgba(23,126,105,0.45)"]],
                contours={"coloring": "fill", "showlines": False},
                ncontours=8,
                showscale=False,
                hoverinfo="skip",
                name="밀도",
            )
        )
        for kind, color in (("long", "#177e69"), ("short", "#d9634d")):
            subset = filtered[filtered["kind"] == kind]
            if not subset.empty:
                scatter.add_trace(
                    go.Scatter(
                        x=subset["duration"],
                        y=subset["waiting"],
                        mode="markers",
                        name=kind.capitalize(),
                        marker={"color": color, "size": 7, "opacity": 0.78},
                        customdata=subset.index,
                        hovertemplate=(
                            "분출: %{x:.2f}분<br>대기: %{y:.0f}분"
                            f"<br>유형: {kind}<extra></extra>"
                        ),
                    )
                )
        scatter.update_layout(
            template="plotly_white",
            height=390,
            margin={"l": 8, "r": 8, "t": 12, "b": 8},
            xaxis_title="분출 지속 시간 (분)",
            yaxis_title="대기 시간 (분)",
            legend_title_text="분출 유형",
        )
        st.plotly_chart(scatter, width="stretch")

    with histogram_column:
        st.subheader("대기 시간 분포")
        histogram = go.Figure()
        histogram.add_trace(
            go.Histogram(
                x=filtered["waiting"],
                histnorm="probability density",
                nbinsx=18,
                marker_color="#9bc8b9",
                opacity=0.75,
                name="관측 분포",
                hovertemplate="대기 시간: %{x:.0f}분<br>밀도: %{y:.3f}<extra></extra>",
            )
        )
        density_x, density_y = estimate_density(filtered["waiting"].astype(float).tolist())
        histogram.add_trace(
            go.Scatter(
                x=density_x,
                y=density_y,
                mode="lines",
                line={"color": "#d9634d", "width": 3},
                name="밀도 추정",
                hovertemplate="대기 시간: %{x:.1f}분<br>밀도: %{y:.3f}<extra></extra>",
            )
        )
        histogram.update_layout(
            template="plotly_white",
            height=390,
            margin={"l": 8, "r": 8, "t": 12, "b": 8},
            xaxis_title="대기 시간 (분)",
            yaxis_title="확률 밀도",
            barmode="overlay",
            legend_title_text="",
        )
        st.plotly_chart(histogram, width="stretch")

st.subheader("관측 데이터")
table_column, summary_column = st.columns([1.6, 1], gap="large")
with table_column:
    st.dataframe(filtered, width="stretch", hide_index=True)
with summary_column:
    st.markdown("**요약 통계량**")
    if filtered.empty:
        st.write("표시할 통계가 없습니다.")
    else:
        st.dataframe(
            filtered[["duration", "waiting"]].describe().T,
            width="stretch",
        )

st.caption("데이터 출처: Seaborn `geyser` 데이터셋 · 차트는 마우스 오버와 확대/축소를 지원합니다.")