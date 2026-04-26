"""Render a static image report card (JPG + thumbnail) using Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.models.schemas import ContentGenerationInput, Report, ShortformPlan

_OUTPUTS = Path(__file__).resolve().parents[2] / "outputs"

_COLOR_SWATCH: dict[str, tuple[int, int, int]] = {
    "red": (220, 50, 50),
    "orange": (255, 140, 0),
    "yellow": (240, 200, 0),
    "green": (34, 139, 34),
    "blue": (46, 116, 230),
    "violet": (148, 0, 211),
    "black": (40, 40, 40),
    "white": (220, 220, 220),
}

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _render_card(payload: ContentGenerationInput, plan: ShortformPlan) -> Path:
    W, H = 800, 800
    color = payload.target_color.lower()
    accent = _COLOR_SWATCH.get(color, (100, 100, 200))
    text_color = (255, 255, 255) if sum(accent) < 400 else (30, 30, 30)

    img = Image.new("RGB", (W, H), (248, 248, 248))
    draw = ImageDraw.Draw(img)

    # Top accent band
    draw.rectangle([0, 0, W, 120], fill=accent)

    # Title in band
    f_title = _load_font(36)
    title_text = f"{color.upper()} WALK COMPLETE"
    draw.text((W // 2, 60), title_text, font=f_title, fill=(255, 255, 255), anchor="mm")

    # Large color circle
    cx, cy, r = W // 2, 320, 140
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
    f_pct = _load_font(48)
    pct_text = f"{int(payload.best_match_score * 100)}%"
    draw.text((cx, cy), pct_text, font=f_pct, fill=text_color, anchor="mm")

    # Stats
    dist_km = round(payload.distance_m / 1000, 2)
    duration_min = payload.duration_sec // 60
    stats = [
        f"{dist_km} km",
        f"{payload.steps:,} steps",
        f"{duration_min} min",
        payload.badge_title,
    ]
    f_stat = _load_font(28)
    f_caption = _load_font(22)
    y = 510
    for line in stats:
        draw.text((W // 2, y), line, font=f_stat, fill=(60, 60, 60), anchor="mm")
        y += 50

    # Caption from shortform plan
    draw.text((W // 2, 740), f'"{plan.caption}"', font=f_caption, fill=(120, 120, 120), anchor="mm")

    out_path = _OUTPUTS / "reports" / f"{payload.session_id}.jpg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=90)
    return out_path


def _make_thumbnail(source: Path, session_id: str) -> Path:
    thumb_path = _OUTPUTS / "reports" / f"{session_id}_thumb.jpg"
    img = Image.open(source)
    img.thumbnail((300, 300))
    img.save(thumb_path, format="JPEG", quality=85)
    return thumb_path


class ReportRenderSkill:
    def render(
        self,
        payload: ContentGenerationInput,
        plan: ShortformPlan,
        plan_status: str,
        base_url: str = "http://localhost:8000",
    ) -> Report:
        card_path = _render_card(payload, plan)
        _make_thumbnail(card_path, payload.session_id)

        status = "completed" if plan_status == "completed" else "fallback"
        return Report(
            status=status,
            type="image",
            image_url=f"{base_url}/outputs/reports/{payload.session_id}.jpg",
            thumbnail_url=f"{base_url}/outputs/reports/{payload.session_id}_thumb.jpg",
            shortform_prompt=plan.shortform_prompt,
            style=plan.style,
            caption=plan.caption,
            storyboard=plan.storyboard,
        )
