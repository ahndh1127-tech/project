import calendar

import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="✈️ 항공 승객 분석", layout="wide")


@st.cache_data
def load_flights_data() -> pd.DataFrame:
    flights = sns.load_dataset("flights")
    month_numbers = {calendar.month_abbr[number]: number for number in range(1, 13)}
    flights["month_number"] = flights["month"].map(month_numbers).astype(int)
    flights["month_label"] = flights["month_number"].map(lambda month: f"{month}월")
    return flights


flights = load_flights_data()
month_labels = [f"{month}월" for month in range(1, 13)]

st.title("✈️ 항공 승객 분석")

metrics = st.columns(3)
metrics[0].metric("총 행 수", f"{len(flights):,}")
metrics[1].metric("연도 범위", f"{flights['year'].min()}–{flights['year'].max()}")
metrics[2].metric("최대 승객 수", f"{flights['passengers'].max():,}")

month_range = st.sidebar.slider(
    "월 범위",
    min_value=1,
    max_value=12,
    value=(1, 12),
    format="%d월",
)

selected_flights = flights[flights["month_number"].between(*month_range)]
yearly = (
    selected_flights.groupby("year", as_index=False)["passengers"]
    .mean()
    .sort_values("year")
    .rename(columns={"passengers": "average_passengers"})
)
yearly["rolling_mean"] = yearly["average_passengers"].rolling(window=3).mean()

st.subheader("연도별 평균 승객 수와 3년 이동평균")
yearly_long = yearly.melt(
    id_vars="year",
    value_vars=["average_passengers", "rolling_mean"],
    var_name="series",
    value_name="value",
)
yearly_long["series"] = yearly_long["series"].map(
    {
        "average_passengers": "연도별 평균",
        "rolling_mean": "3년 이동평균",
    }
)
line_fig = px.line(
    yearly_long,
    x="year",
    y="value",
    color="series",
    line_dash="series",
    category_orders={"series": ["연도별 평균", "3년 이동평균"]},
    color_discrete_map={"연도별 평균": "#1f77b4", "3년 이동평균": "#ff7f0e"},
    line_dash_map={"연도별 평균": "solid", "3년 이동평균": "dot"},
    labels={
        "year": "연도",
        "value": "평균 승객 수",
        "series": "구분",
    },
)
st.plotly_chart(line_fig, use_container_width=True)

st.subheader("월별 평균 승객 수")
monthly_average = (
    flights.groupby("month_number", as_index=False)["passengers"]
    .mean()
    .sort_values("month_number")
)
monthly_average["month_label"] = monthly_average["month_number"].map(
    lambda month: f"{month}월"
)
bar_fig = px.bar(
    monthly_average,
    x="month_label",
    y="passengers",
    category_orders={"month_label": month_labels},
    labels={"month_label": "월", "passengers": "평균 승객 수"},
)
st.plotly_chart(bar_fig, use_container_width=True)

st.subheader("월별 승객 수 분포")
box_fig = px.box(
    flights,
    x="month_label",
    y="passengers",
    category_orders={"month_label": month_labels},
    labels={"month_label": "월", "passengers": "승객 수"},
)
st.plotly_chart(box_fig, use_container_width=True)

st.subheader("연도별·월별 승객 수 히트맵")
heatmap_data = flights.pivot_table(
    index="year",
    columns="month_number",
    values="passengers",
).reindex(columns=range(1, 13))
heatmap_data.columns = month_labels
heatmap_fig = px.imshow(
    heatmap_data,
    x=month_labels,
    y=heatmap_data.index,
    text_auto=".0f",
    color_continuous_scale="Blues",
    labels={"x": "월", "y": "연도", "color": "승객 수"},
    aspect="auto",
)
st.plotly_chart(heatmap_fig, use_container_width=True)
