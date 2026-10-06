from io import BytesIO

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from utils import apply_styles

st.set_page_config(page_title="이미지 필터 | Designer Color Studio", page_icon="🖼️", layout="wide")
apply_styles()


def apply_filter(image: Image.Image, effect: str, blur_radius: float) -> Image.Image:
    if effect == "흑백":
        return ImageOps.grayscale(image).convert("RGB")
    if effect == "세피아":
        grayscale = ImageOps.grayscale(image)
        return ImageOps.colorize(grayscale, black="#30231D", white="#E8C99D").convert("RGB")
    if effect == "블러":
        return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    if effect == "빈티지":
        faded = ImageEnhance.Color(image).enhance(0.65)
        return ImageEnhance.Contrast(faded).enhance(0.9)
    return image


st.markdown('<div class="eyebrow">03 / Image filter</div>', unsafe_allow_html=True)
st.title("이미지 필터")
st.caption("효과를 적용하고 PNG 결과물을 다운로드하세요.")

uploaded_file = st.file_uploader("이미지 선택", type=("png", "jpg", "jpeg", "webp"))
effect = st.radio("필터", ("원본", "흑백", "세피아", "블러", "빈티지"), horizontal=True)
blur_radius = st.slider("블러 강도", 1, 20, 8, disabled=effect != "블러")

if uploaded_file is None:
    st.info("PNG, JPG 또는 WebP 이미지를 업로드해 주세요.")
else:
    original = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
    filtered = apply_filter(original, effect, blur_radius)
    before, after = st.columns(2, gap="medium")
    with before:
        st.subheader("원본")
        st.image(original, use_container_width=True)
    with after:
        st.subheader(effect)
        st.image(filtered, use_container_width=True)

    output = BytesIO()
    filtered.save(output, format="PNG")
    st.download_button(
        "결과 이미지 다운로드",
        data=output.getvalue(),
        file_name="filtered-image.png",
        mime="image/png",
    )