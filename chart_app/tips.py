import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="🍽️ 레스토랑 팁 분석", layout="wide")


@st.cache_data
def load_tips_data() -> pd.DataFrame:
    return sns.load_dataset("tips")


tips = load_tips_data()

st.title("🍽️ 레스토랑 팁 분석")

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
bar_fig = px.bar(
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
bar_fig.update_traces(
    texttemplate="$%{y:,.2f}",
    textposition="outside",
    cliponaxis=False,
)
st.plotly_chart(bar_fig, use_container_width=True)
