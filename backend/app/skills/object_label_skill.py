"""Deterministic object labeling from color and spatial position. No ML."""

import numpy as np
from PIL import Image

from app.skills.image_color_skill import _circular_dist, _hue_to_color_name, _rgb_to_hsv


def _region_dominant_color(region: np.ndarray) -> tuple[str | None, float]:
    """Return (color_name, avg_saturation) for a pixel region."""
    hsv = _rgb_to_hsv(region)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    mask = (s > 0.20) & (v > 0.20)
    if mask.sum() < 5:
        return None, 0.0
    median_h = float(np.median(h[mask]))
    return _hue_to_color_name(median_h), float(np.mean(s[mask]))


def label_object(image: Image.Image, dominant_color: str, dominant_hue: float) -> str:
    """Return a simple object label based on color and spatial distribution.

    Rules:
    - blue dominant in top half  → sky
    - green dominant in bottom half → grass
    - red anywhere               → sign
    - otherwise                  → scene
    """
    img = image.convert("RGB").resize((100, 100), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0

    top_half = arr[:50, :, :]
    bottom_half = arr[50:, :, :]

    top_color, top_sat = _region_dominant_color(top_half)
    bottom_color, bottom_sat = _region_dominant_color(bottom_half)

    if top_color == "blue" and top_sat > 0.15:
        return "sky"
    if bottom_color == "green" and bottom_sat > 0.15:
        return "grass"
    if dominant_color == "red":
        return "sign"

    # Secondary check: is the overall dominant hue close to blue in the top?
    if _circular_dist(dominant_hue, 240.0) < 60.0 and top_sat > 0.10:
        return "sky"

    return "scene"
