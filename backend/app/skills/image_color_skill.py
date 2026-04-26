"""Extract dominant color from an image using HSV bucketing."""

import numpy as np
from PIL import Image


_CANONICAL_HUES: dict[str, float] = {
    "red": 0.0,
    "orange": 30.0,
    "yellow": 60.0,
    "green": 120.0,
    "blue": 240.0,
    "indigo": 270.0,
    "violet": 300.0,
}


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """Vectorized RGB (0-1 float) → HSV (H:0-360, S:0-1, V:0-1)."""
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


def _hue_to_color_name(hue: float) -> str:
    best = min(_CANONICAL_HUES.items(), key=lambda kv: _circular_dist(hue, kv[1]))
    return best[0]


def _circular_dist(h1: float, h2: float) -> float:
    diff = abs(h1 - h2) % 360.0
    return min(diff, 360.0 - diff)


def extract_dominant_color(image: Image.Image) -> dict:
    """Return dominant hue, color name, RGB, and saturation from an image."""
    img = image.convert("RGB").resize((100, 100), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    hsv = _rgb_to_hsv(arr)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # Use colorful, non-dark pixels for dominance detection
    mask = (s > 0.20) & (v > 0.20)
    if mask.sum() < 10:
        mask = v > 0.40  # fall back to non-dark pixels

    if mask.sum() == 0:
        dominant_h = float(np.mean(h))
        dominant_s = float(np.mean(s))
    else:
        dominant_h = float(np.median(h[mask]))
        dominant_s = float(np.mean(s[mask]))

    dominant_color = _hue_to_color_name(dominant_h)

    # Reconstruct a representative RGB from pixels near the dominant hue
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
    }
