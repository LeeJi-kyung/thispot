"""Extract dominant color from an image.

Primary path: Gemini 2.0 Flash (GEMINI_API_KEY env var required).
Fallback path: HSV bucketing with NumPy (no API key needed).
"""

import io
import json
import os
import re

import numpy as np
from PIL import Image

try:
    from google import genai as _genai
    from google.genai import types as _gtypes

    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

_CANONICAL_HUES: dict[str, float] = {
    "red": 0.0,
    "orange": 30.0,
    "yellow": 60.0,
    "green": 120.0,
    "blue": 240.0,
    "indigo": 270.0,
    "violet": 300.0,
}

_GEMINI_PROMPT = """\
Analyze this image and return ONLY valid JSON (no markdown, no code block, no explanation):

{
  "top_colors": [
    {"name": "sky blue", "hex": "#87CEEB", "rgb": [135, 206, 235], "percent": 75.2, "category": "blue"},
    {"name": "white cloud", "hex": "#F8F8FF", "rgb": [248, 248, 255], "percent": 15.1, "category": "white"},
    {"name": "light gray", "hex": "#D3D3D3", "rgb": [211, 211, 211], "percent": 9.7, "category": "none"}
  ],
  "object_label": "sky"
}

Rules:
- top_colors: exactly 3 entries sorted by percent descending, percents sum to 100.0
- hex must be a valid 6-digit hex code that matches the rgb values
- name should be a descriptive color name in English (e.g. "olive khaki", "navy blue", "bright red")
- category must be exactly one of: red, orange, yellow, green, blue, violet, black, white, none
  (use "none" if the color does not clearly belong to any of the 8 categories)
- object_label must be exactly one of: sky, grass, sign, scene
"""


# ── Shared helpers ────────────────────────────────────────────────────────────


def _circular_dist(h1: float, h2: float) -> float:
    diff = abs(h1 - h2) % 360.0
    return min(diff, 360.0 - diff)


def _hue_to_color_name(hue: float) -> str:
    return min(_CANONICAL_HUES.items(), key=lambda kv: _circular_dist(hue, kv[1]))[0]


def _rgb_to_hue(rgb: list[int]) -> float:
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin
    if delta == 0:
        return 0.0
    if cmax == r:
        return (60.0 * ((g - b) / delta)) % 360.0
    if cmax == g:
        return 60.0 * ((b - r) / delta + 2.0)
    return 60.0 * ((r - g) / delta + 4.0)


# ── Gemini path ───────────────────────────────────────────────────────────────


def _extract_with_gemini(image: Image.Image, api_key: str) -> dict:
    client = _genai.Client(api_key=api_key)

    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    img_part = _gtypes.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[_GEMINI_PROMPT, img_part],
    )
    text = re.sub(r"```(?:json)?\s*|```", "", response.text).strip()
    data = json.loads(text)

    top_colors = data["top_colors"][:3]
    object_label = data.get("object_label", "scene")

    dominant_rgb = top_colors[0]["rgb"]
    dominant_hue = _rgb_to_hue(dominant_rgb)
    dominant_color = _hue_to_color_name(dominant_hue)

    return {
        "dominant_hue": round(dominant_hue, 1),
        "dominant_color": dominant_color,
        "dominant_rgb": dominant_rgb,
        "top_colors": top_colors,
        "object_label": object_label,
        "source": "gemini",
    }


# ── HSV fallback path ─────────────────────────────────────────────────────────


def _rgb_to_hsv_vec(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    h = np.zeros_like(cmax)
    nonzero = delta > 0
    max_is_r = nonzero & (cmax == r)
    max_is_g = nonzero & (cmax == g)
    max_is_b = nonzero & (cmax == b)

    h[max_is_r] = (60.0 * ((g[max_is_r] - b[max_is_r]) / delta[max_is_r])) % 360.0
    h[max_is_g] = 60.0 * ((b[max_is_g] - r[max_is_g]) / delta[max_is_g] + 2.0)
    h[max_is_b] = 60.0 * ((r[max_is_b] - g[max_is_b]) / delta[max_is_b] + 4.0)

    s = np.where(cmax > 0, delta / cmax, 0.0)
    return np.stack([h, s, cmax], axis=-1)


def _extract_with_hsv(image: Image.Image) -> dict:
    img = image.convert("RGB").resize((100, 100), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    hsv = _rgb_to_hsv_vec(arr)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    mask = (s > 0.20) & (v > 0.20)
    if mask.sum() < 10:
        mask = v > 0.40
    if mask.sum() == 0:
        dominant_h = float(np.mean(h))
        dominant_s = float(np.mean(s))
    else:
        dominant_h = float(np.median(h[mask]))
        dominant_s = float(np.mean(s[mask]))

    dominant_color = _hue_to_color_name(dominant_h)

    h_dist = np.abs(h - dominant_h) % 360.0
    h_dist = np.minimum(h_dist, 360.0 - h_dist)
    color_mask = mask & (h_dist < 30.0)

    if color_mask.sum() > 0:
        rep_rgb = arr[color_mask].mean(axis=0)
    else:
        rep_rgb = arr[mask].mean(axis=0) if mask.sum() > 0 else arr.mean(axis=(0, 1))

    dominant_rgb = [int(round(float(rep_rgb[c]) * 255)) for c in range(3)]

    return {
        "dominant_hue": round(dominant_h, 1),
        "dominant_saturation": round(dominant_s, 3),
        "dominant_color": dominant_color,
        "dominant_rgb": dominant_rgb,
        "top_colors": [],
        "source": "hsv",
    }


# ── Public entry point ────────────────────────────────────────────────────────


def extract_dominant_color(image: Image.Image) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and _HAS_GENAI:
        try:
            return _extract_with_gemini(image, api_key)
        except Exception:
            pass
    return _extract_with_hsv(image)
