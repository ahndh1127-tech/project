from io import BytesIO

import streamlit as st
from PIL import Image

from utils import apply_styles, extract_dominant_colors, make_theme, render_color_chips

st.set_page_config(page_title="이미지 컬러 추출 | Designer Color Studio", page_icon="🖼️", layout="wide")
apply_styles()

st.markdown('<div class="eyebrow">02 / Image colors</div>', unsafe_allow_html=True)
st.title("이미지 컬러 추출")
st.caption("이미지를 올리면 자주 등장하는 색 다섯 가지를 팔레트로 정리합니다.")

uploaded_file = st.file_uploader("이미지 선택", type=("png", "jpg", "jpeg", "webp"))
if uploaded_file is None:
    st.info("PNG, JPG 또는 WebP 이미지를 업로드해 주세요.")
else:
    image = Image.open(BytesIO(uploaded_file.getvalue()))
    colors = extract_dominant_colors(image)
    preview, palette = st.columns([1, 1.3], gap="large")
    with preview:
        st.image(image, caption=uploaded_file.name, use_container_width=True)
    with palette:
        st.subheader("추출 팔레트")
        render_color_chips([(f"Color {index + 1}", color) for index, color in enumerate(colors)])
        st.subheader("컬러 테마")
        if colors:
            render_color_chips(make_theme(colors[0]))
        palette_text = "\n".join(colors)
        st.download_button(
            "팔레트 HEX 다운로드",
            data=palette_text,
            file_name="image-palette.txt",
            mime="text/plain",
        )