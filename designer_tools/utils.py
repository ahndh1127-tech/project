from __future__ import annotations

import colorsys
from collections.abc import Sequence

import streamlit as st
from PIL import Image


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
        :root { --ink: #17231f; --muted: #65736d; --line: #e2e9e5; --accent: #dc5b3d; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
        .stApp { background: #f7f8f5; }
        .block-container { max-width: 1120px; padding-top: 2.5rem; padding-bottom: 4rem; }
        h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: 0; }
        .eyebrow { color: var(--accent); font-size: .76rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
        .subtle { color: var(--muted); }
        .tool-card { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 1.3rem; min-height: 220px; }
        .tool-card h3 { margin: .8rem 0 .35rem; font-size: 1.15rem; }
        .tool-card p { color: var(--muted); font-size: .92rem; min-height: 2.7rem; }
        .swatch-row { display: flex; height: 44px; overflow: hidden; border-radius: 5px; }
        .swatch-row span { flex: 1; }
        .color-chip { border: 1px solid rgba(23,35,31,.08); border-radius: 7px; padding: 1rem; min-height: 116px; display: flex; flex-direction: column; justify-content: space-between; }
        .color-chip strong { font-size: .76rem; text-transform: uppercase; }
        .color-chip code { color: inherit; background: transparent; font-size: .9rem; }
        div[data-testid="stDownloadButton"] button, div[data-testid="stPageLink"] a { border-radius: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_hex(value: str) -> str:
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    if len(value) != 6 or any(character not in "0123456789abcdefABCDEF" for character in value):
        raise ValueError("HEX 색상은 #RGB 또는 #RRGGBB 형식이어야 합니다.")
    return f"#{value.upper()}"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    color = normalize_hex(value).lstrip("#")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def rgb_to_hex(rgb: Sequence[int]) -> str:
    return "#" + "".join(f"{max(0, min(255, int(channel))):02X}" for channel in rgb)


def rgb_color_family(rgb: Sequence[int]) -> str:
    red, green, blue = (channel / 255 for channel in rgb)
    hue, saturation, _ = colorsys.rgb_to_hsv(red, green, blue)
    if saturation < 0.12:
        return "무채색 계열"

    degrees = hue * 360
    if degrees < 15 or degrees >= 345:
        return "빨강 계열"
    if degrees < 75:
        return "노랑 계열"
    if degrees < 165:
        return "초록 계열"
    if degrees < 255:
        return "파랑 계열"
    return "보라 계열"


def make_theme(base_hex: str) -> list[tuple[str, str]]:
    red, green, blue = (channel / 255 for channel in hex_to_rgb(base_hex))
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    accent = colorsys.hls_to_rgb((hue + 0.5) % 1, min(0.58, max(0.38, lightness)), max(0.48, saturation))
    background = colorsys.hls_to_rgb(hue, 0.96, min(0.3, saturation * 0.25))
    return [
        ("기본색", normalize_hex(base_hex)),
        ("보조색", rgb_to_hex(tuple(round(channel * 255) for channel in accent))),
        ("배경색", rgb_to_hex(tuple(round(channel * 255) for channel in background))),
    ]


def render_color_chips(colors: Sequence[tuple[str, str]]) -> None:
    columns = st.columns(len(colors))
    for column, (label, color) in zip(columns, colors):
        red, green, blue = hex_to_rgb(color)
        luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255
        foreground = "#17231F" if luminance > 0.62 else "#FFFFFF"
        column.markdown(
            f'<div class="color-chip" style="background:{color};color:{foreground}">'
            f"<strong>{label}</strong><code>{color}</code></div>",
            unsafe_allow_html=True,
        )


def extract_dominant_colors(image: Image.Image, count: int = 5) -> list[str]:
    thumbnail = image.convert("RGB")
    thumbnail.thumbnail((240, 240))
    quantized = thumbnail.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = sorted(quantized.getcolors() or [], reverse=True)
    colors: list[str] = []
    for _, palette_index in color_counts:
        offset = palette_index * 3
        color = rgb_to_hex(palette[offset : offset + 3])
        if color not in colors:
            colors.append(color)
        if len(colors) == count:
            break
    return colors