import colorsys

import streamlit as st

from utils import apply_styles, make_theme, render_color_chips, rgb_color_family, rgb_to_hex

st.set_page_config(page_title="컬러 피커 | Designer Color Studio", page_icon="🎨", layout="wide")
apply_styles()

st.markdown('<div class="eyebrow">01 / Color picker</div>', unsafe_allow_html=True)
st.title("컬러 피커")
st.caption("RGB 값을 조절해 기준색을 정하고, 함께 쓸 테마 색상을 확인하세요.")

left, right = st.columns([0.9, 1.1], gap="large")
with left:
    red = st.slider("Red", 0, 255, 220, key="picker_red")
    green = st.slider("Green", 0, 255, 91, key="picker_green")
    blue = st.slider("Blue", 0, 255, 61, key="picker_blue")

base_color = rgb_to_hex((red, green, blue))
with right:
    st.markdown('<div class="eyebrow">Selected color</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="height:170px;border-radius:8px;background:{base_color};border:1px solid #e2e9e5"></div>',
        unsafe_allow_html=True,
    )
    st.subheader(base_color)
    hue, lightness, saturation = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
    st.markdown(f"**색상 계열**  `{rgb_color_family((red, green, blue))}`")
    st.markdown(f"**RGB**  `{red}, {green}, {blue}`　 **HSL**  `{round(hue * 360)}°, {round(saturation * 100)}%, {round(lightness * 100)}%`")

st.divider()
st.subheader("컬러 테마")
render_color_chips(make_theme(base_color))