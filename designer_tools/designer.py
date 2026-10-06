import streamlit as st

from utils import apply_styles

st.set_page_config(page_title="Designer Color Studio", page_icon="🎨", layout="wide")
apply_styles()

st.markdown('<div class="eyebrow">Designer Color Studio</div>', unsafe_allow_html=True)
st.title("색을 고르고, 다듬고, 완성하세요.")
st.markdown('<p class="subtle">작업 흐름에 맞춘 세 가지 컬러 도구</p>', unsafe_allow_html=True)
st.write("")

tools = [
    {
        "path": "pages/01_color_picker.py",
        "title": "컬러 피커",
        "description": "RGB를 조정해 원하는 기준색과 컬러 테마를 만듭니다.",
        "swatches": ("#DC5B3D", "#3D80DC", "#F7EDE9"),
    },
    {
        "path": "pages/02_image_color.py",
        "title": "이미지 컬러 추출",
        "description": "이미지에서 분위기를 결정하는 대표 색상 다섯 개를 찾습니다.",
        "swatches": ("#D27752", "#68827A", "#D4B77A", "#4A5550", "#E8DDD0"),
    },
    {
        "path": "pages/03_image_filter.py",
        "title": "이미지 필터",
        "description": "흑백, 세피아, 블러 효과를 미리 보고 결과물을 저장합니다.",
        "swatches": ("#303431", "#A9784F", "#B4BAB6"),
    },
]

columns = st.columns(3, gap="medium")
for column, tool in zip(columns, tools):
    with column:
        swatches = "".join(f'<span style="background:{color}"></span>' for color in tool["swatches"])
        st.markdown(
            f'<div class="tool-card"><div class="swatch-row">{swatches}</div>'
            f'<h3>{tool["title"]}</h3><p>{tool["description"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.page_link(tool["path"], label="도구 열기", icon=":material/arrow_forward:")