import calendar

import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="항공 승객·레스토랑 팁 분석", layout="wide")

flights_tab, tips_tab = st.tabs(["✈️ 항공 승객 분석", "🍽️ 레스토랑 팁 분석"])

with flights_tab:

    @st.cache_data
    def load_flights_data() -> pd.DataFrame:
        flights = sns.load_dataset("flights")
        month_numbers = {
            calendar.month_abbr[number]: number for number in range(1, 13)
        }
        flights["month_number"] = flights["month"].map(month_numbers).astype(int)
        flights["month_label"] = flights["month_number"].map(
            lambda month: f"{month}월"
        )
        return flights

    flights = load_flights_data()
    month_labels = [f"{month}월" for month in range(1, 13)]

    metrics = st.columns(3)
    metrics[0].metric("총 행 수", f"{len(flights):,}")
    metrics[1].metric(
        "연도 범위", f"{flights['year'].min()}–{flights['year'].max()}"
    )
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

with tips_tab:

    @st.cache_data
    def load_tips_data() -> pd.DataFrame:
        return sns.load_dataset("tips")

    tips = load_tips_data()

    st.subheader("기술 통계 요약")
    metrics = st.columns(4)
    metrics[0].metric("총 데이터 수", f"{len(tips):,}")
    metrics[1].metric("평균 식사 금액", f"${tips['total_bill'].mean():.2f}")
    metrics[2].metric("평균 팁 금액", f"${tips['tip'].mean():.2f}")
    average_tip_percentage = (tips["tip"] / tips["total_bill"] * 100).mean()
    metrics[3].metric("평균 팁 비율", f"{average_tip_percentage:.2f}%")
    st.dataframe(tips.describe(), use_container_width=True)

    color_options = {
        "성별(sex)": "sex",
        "흡연여부(smoker)": "smoker",
        "요일(day)": "day",
        "시간대(time)": "time",
    }
    group_options = {
        "요일(day)": "day",
        "성별(sex)": "sex",
        "시간대(time)": "time",
        "흡연여부(smoker)": "smoker",
    }

    st.sidebar.header("차트 설정")
    selected_color_label = st.sidebar.selectbox(
        "산점도 색상 기준",
        list(color_options),
    )
    selected_group_label = st.sidebar.selectbox(
        "막대차트 그룹 기준",
        list(group_options),
    )

    st.subheader("식사 금액과 팁의 관계")
    scatter_fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        color=color_options[selected_color_label],
        hover_data={
            "total_bill": ":.2f",
            "tip": ":.2f",
            "size": True,
        },
        trendline="ols",
        labels={
            "total_bill": "식사 금액 ($)",
            "tip": "팁 금액 ($)",
            "size": "인원수",
            "sex": "성별",
            "smoker": "흡연 여부",
            "day": "요일",
            "time": "시간대",
        },
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.subheader("조건별 식사 금액 합계")
    group_column = group_options[selected_group_label]
    bill_totals = (
        tips.groupby(group_column, observed=True, as_index=False)["total_bill"]
        .sum()
        .sort_values("total_bill", ascending=False)
    )
    tips_bar_fig = px.bar(
        bill_totals,
        x=group_column,
        y="total_bill",
        text="total_bill",
        title="선택 기준별 총 식사 금액 합계",
        labels={
            group_column: selected_group_label,
            "total_bill": "총 식사 금액 ($)",
        },
    )
    tips_bar_fig.update_traces(
        texttemplate="$%{y:,.2f}",
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(tips_bar_fig, use_container_width=True)
