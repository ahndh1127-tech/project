import calendar
import json
import os
from datetime import date
from uuid import uuid4

import pandas as pd
import streamlit as st


diary_file = "diary.csv"
settings_file = "settings.json"
wellness_file = "wellness.csv"
food_file = "food.csv"
weather_options = ["맑음", "흐림", "비", "눈", "바람"]
MOOD_OPTIONS = ["매우 좋음", "좋음", "보통", "나쁨", "매우 나쁨"]
DIARY_COLUMNS = ["diary_id", "날짜", "제목", "내용", "날씨", "작성자"]
WELLNESS_COLUMNS = ["날짜", "기분", "운동"]
FOOD_COLUMNS = ["날짜", "음식", "섭취량", "1회 kcal", "총 kcal"]
DEFAULT_SETTINGS = {"author_name": "", "theme": "파랑", "last_viewed_date": None}
theme_colors = {
    "파랑": "#2563EB",
    "초록": "#15803D",
    "보라": "#7E22CE",
    "주황": "#C2410C",
    "빨강": "#B91C1C",
}
FOOD_CALORIES = {
    "밥 (1공기)": 300,
    "김치찌개 (1인분)": 250,
    "된장찌개 (1인분)": 200,
    "계란후라이 (1개)": 90,
    "사과 (1개)": 95,
    "바나나 (1개)": 105,
    "닭가슴살 (100g)": 165,
    "라면 (1봉지)": 500,
    "우유 (1컵)": 130,
    "요거트 (1개)": 120,
}


def load_settings():
    try:
        with open(settings_file, encoding="utf-8") as settings_file_handle:
            stored_settings = json.load(settings_file_handle)
    except FileNotFoundError:
        return DEFAULT_SETTINGS.copy()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        st.warning("설정 파일이 손상되어 기본값으로 초기화했어요.")
        return DEFAULT_SETTINGS.copy()

    if not isinstance(stored_settings, dict):
        st.warning("설정 파일이 손상되어 기본값으로 초기화했어요.")
        return DEFAULT_SETTINGS.copy()
    return {**DEFAULT_SETTINGS, **stored_settings}


def save_settings(settings):
    with open(settings_file, "w", encoding="utf-8") as settings_file_handle:
        json.dump(settings, settings_file_handle, ensure_ascii=False, indent=2)


def load_csv(filename, columns):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return pd.DataFrame(columns=columns)
    return pd.read_csv(filename, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def save_csv(data, filename):
    data.to_csv(filename, index=False, encoding="utf-8-sig")


def load_diary():
    diary = load_csv(diary_file, DIARY_COLUMNS)
    changed = False
    for column in DIARY_COLUMNS:
        if column not in diary.columns:
            diary[column] = ""
            changed = True

    seen_ids = set()
    for row_index, diary_id in diary["diary_id"].items():
        if not diary_id or diary_id in seen_ids:
            diary_id = uuid4().hex
            diary.at[row_index, "diary_id"] = diary_id
            changed = True
        seen_ids.add(diary_id)

    if changed and not diary.empty:
        save_csv(diary, diary_file)
    return diary


def shift_month(month_start, offset):
    month_index = month_start.year * 12 + month_start.month - 1 + offset
    return date(month_index // 12, month_index % 12 + 1, 1)


def render_calendar(diary, wellness, food):
    today = date.today()
    st.session_state.setdefault("selected_date", today)
    st.session_state.setdefault("calendar_month", today.replace(day=1))
    selected_date = st.session_state.selected_date
    month_start = st.session_state.calendar_month

    header = st.columns([1, 4, 1])
    previous_month = header[0].button("◀ 이전 달", key="previous-month")
    next_month = header[2].button("다음 달 ▶", key="next-month")
    if previous_month:
        month_start = shift_month(month_start, -1)
        st.session_state.calendar_month = month_start
        selected_day = min(selected_date.day, calendar.monthrange(month_start.year, month_start.month)[1])
        selected_date = date(month_start.year, month_start.month, selected_day)
        st.session_state.selected_date = selected_date
    elif next_month:
        month_start = shift_month(month_start, 1)
        st.session_state.calendar_month = month_start
        selected_day = min(selected_date.day, calendar.monthrange(month_start.year, month_start.month)[1])
        selected_date = date(month_start.year, month_start.month, selected_day)
        st.session_state.selected_date = selected_date
    header[1].subheader(f"{month_start.year}년 {month_start.month}월")

    record_dates = set(diary["날짜"]) | set(wellness["날짜"]) | set(food["날짜"])
    weekday_columns = st.columns(7)
    for column, weekday in zip(weekday_columns, ["월", "화", "수", "목", "금", "토", "일"]):
        column.caption(weekday)

    for week in calendar.monthcalendar(month_start.year, month_start.month):
        day_columns = st.columns(7)
        for column, day_number in zip(day_columns, week):
            if not day_number:
                column.write("")
                continue
            calendar_date = date(month_start.year, month_start.month, day_number)
            date_key = calendar_date.isoformat()
            marker = " •" if date_key in record_dates else ""
            if column.button(
                f"{day_number}{marker}",
                key=f"calendar-day-{date_key}",
                use_container_width=True,
            ):
                st.session_state.selected_date = calendar_date
                selected_date = calendar_date
    return selected_date


settings = load_settings()
is_first_visit = not settings.get("last_viewed_date")
today = date.today()
settings["last_viewed_date"] = today.isoformat()
save_settings(settings)

with st.sidebar:
    st.subheader("설정")
    author_name = st.text_input("작성자 이름", value=settings.get("author_name", ""))
    theme_options = list(theme_colors)
    saved_theme = settings.get("theme", "파랑")
    if saved_theme not in theme_options:
        saved_theme = "파랑"
    selected_theme = st.selectbox(
        "테마 색상",
        theme_options,
        index=theme_options.index(saved_theme),
    )

if selected_theme != settings.get("theme"):
    settings["theme"] = selected_theme
    save_settings(settings)

if st.sidebar.button("저장"):
    settings["author_name"] = author_name
    settings["theme"] = selected_theme
    save_settings(settings)
    st.sidebar.success("설정을 저장했어요.")

st.markdown(
    f'<div style="background-color: {theme_colors[selected_theme]}; '
    'padding: 0.8rem 1rem; border-radius: 6px; color: white; font-weight: 600;">'
    f'{selected_theme} 테마</div>',
    unsafe_allow_html=True,
)
st.title("📔 나의 일기장")

diary = load_diary()
wellness = load_csv(wellness_file, WELLNESS_COLUMNS)
food = load_csv(food_file, FOOD_COLUMNS)
selected_date = render_calendar(diary, wellness, food)
selected_date_text = selected_date.isoformat()
st.header(f"{selected_date_text} 기록")

with st.form(f"diary-form-{selected_date_text}"):
    title = st.text_input("제목", key=f"diary-title-{selected_date_text}")
    content = st.text_area("내용", height=150, key=f"diary-content-{selected_date_text}")
    weather = st.selectbox("오늘의 날씨", weather_options, key=f"diary-weather-{selected_date_text}")
    save_diary = st.form_submit_button("일기 저장")

if save_diary:
    entry = pd.DataFrame(
        [
            {
                "diary_id": uuid4().hex,
                "날짜": selected_date_text,
                "제목": title,
                "내용": content,
                "날씨": weather,
                "작성자": author_name,
            }
        ]
    )
    diary = pd.concat([diary, entry], ignore_index=True)
    save_csv(diary, diary_file)
    st.success("일기가 저장되었습니다!")

wellness_for_date = wellness[wellness["날짜"] == selected_date_text]
current_wellness = wellness_for_date.iloc[-1] if not wellness_for_date.empty else None
mood_default = current_wellness["기분"] if current_wellness is not None else "보통"
if mood_default not in MOOD_OPTIONS:
    mood_default = "보통"
exercise_default = current_wellness["운동"] if current_wellness is not None else ""

with st.form(f"wellness-form-{selected_date_text}"):
    mood = st.selectbox(
        "오늘의 기분",
        MOOD_OPTIONS,
        index=MOOD_OPTIONS.index(mood_default),
        key=f"mood-{selected_date_text}",
    )
    exercise = st.text_area(
        "운동 기록",
        value=exercise_default,
        key=f"exercise-{selected_date_text}",
    )
    save_wellness = st.form_submit_button("기분·운동 저장")

if save_wellness:
    wellness = wellness[wellness["날짜"] != selected_date_text]
    wellness = pd.concat(
        [
            wellness,
            pd.DataFrame([{"날짜": selected_date_text, "기분": mood, "운동": exercise}]),
        ],
        ignore_index=True,
    )
    save_csv(wellness, wellness_file)
    st.success("기분과 운동 기록을 저장했어요.")

st.subheader("음식 기록")
st.caption("열량은 일반적인 1회 제공량 기준의 대략적인 참고값이며 실제 제품·조리법에 따라 달라요.")
with st.form(f"food-form-{selected_date_text}"):
    selected_food = st.selectbox(
        "음식",
        list(FOOD_CALORIES),
        key=f"food-choice-{selected_date_text}",
    )
    servings = st.number_input(
        "섭취량 (인분)",
        min_value=0.25,
        max_value=20.0,
        value=1.0,
        step=0.25,
        key=f"food-servings-{selected_date_text}",
    )
    st.caption(f"1회 기준 약 {FOOD_CALORIES[selected_food]} kcal")
    add_food = st.form_submit_button("음식 추가")

if add_food:
    food_entry = pd.DataFrame(
        [
            {
                "날짜": selected_date_text,
                "음식": selected_food,
                "섭취량": servings,
                "1회 kcal": FOOD_CALORIES[selected_food],
                "총 kcal": round(servings * FOOD_CALORIES[selected_food]),
            }
        ]
    )
    food = pd.concat([food, food_entry], ignore_index=True)
    save_csv(food, food_file)
    st.success("음식 기록을 추가했어요.")

st.subheader("선택한 날짜의 기록")
daily_diary = diary[diary["날짜"] == selected_date_text].drop(columns=["diary_id"], errors="ignore")
daily_wellness = wellness[wellness["날짜"] == selected_date_text]
daily_food = food[food["날짜"] == selected_date_text].copy()
if daily_diary.empty:
    st.info("이 날짜에 작성된 일기가 없어요.")
else:
    st.dataframe(daily_diary, hide_index=True, width="stretch")
if daily_wellness.empty:
    st.info("이 날짜에 기분·운동 기록이 없어요.")
else:
    st.dataframe(daily_wellness, hide_index=True, width="stretch")
if daily_food.empty:
    st.info("이 날짜에 음식 기록이 없어요.")
else:
    daily_food["총 kcal"] = pd.to_numeric(daily_food["총 kcal"], errors="coerce").fillna(0)
    daily_food["섭취량"] = pd.to_numeric(daily_food["섭취량"], errors="coerce").fillna(0)
    daily_food["1회 kcal"] = pd.to_numeric(daily_food["1회 kcal"], errors="coerce").fillna(0)
    st.dataframe(daily_food, hide_index=True, width="stretch")
total_calories = daily_food["총 kcal"].sum() if not daily_food.empty else 0
st.metric("하루 총 섭취 열량", f"{total_calories:,.0f} kcal")

st.subheader("전체 일기 목록")
if diary.empty:
    st.write("아직 작성된 일기가 없어요.")
else:
    diary_display = diary.drop(columns=["diary_id"], errors="ignore").copy()
    diary_display.insert(0, "번호", range(1, len(diary_display) + 1))
    st.dataframe(diary_display, hide_index=True, width="stretch")

    diary_ids = diary["diary_id"].tolist()
    diary_labels = {
        diary_id: f"{index + 1}. {row['날짜']} - {row['제목']}"
        for index, (_, row) in enumerate(diary.iterrows())
        for diary_id in [row["diary_id"]]
    }
    delete_id = st.selectbox(
        "삭제할 일기 번호",
        diary_ids,
        format_func=lambda diary_id: diary_labels[diary_id],
        key="diary-delete-selection",
    )
    confirm_delete = st.checkbox("선택한 일기를 삭제하겠습니다", key="confirm-diary-delete")
    if st.button("선택한 일기 삭제", disabled=not confirm_delete):
        diary = diary[diary["diary_id"] != delete_id].reset_index(drop=True)
        save_csv(diary, diary_file)
        st.success("선택한 일기를 삭제했습니다.")
        st.rerun()

if is_first_visit:
    st.write("처음 방문이에요! 일기를 써봐요 🌱")
else:
    st.write(f"마지막으로 일기를 확인한 날: {today.isoformat()}")