from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.models.schemas import ContentGenerationInput, Report, ShortformPlan
from app.storage.sessions import safe_id


APP_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = APP_DIR / "outputs" / "reports"
VIDEOS_DIR = APP_DIR / "outputs" / "videos"
CHARACTER_DIR = APP_DIR / "assets" / "character"
BASE_URL = "http://localhost:8000"


COLOR_RGB = {
    "red": (239, 68, 68),
    "orange": (249, 115, 22),
    "yellow": (234, 179, 8),
    "green": (34, 197, 94),
    "blue": (59, 130, 246),
    "indigo": (99, 102, 241),
    "violet": (139, 92, 246),
}


class ReportRenderSkill:
    def ensure_demo_assets(self) -> None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        CHARACTER_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_character_asset()
        should_render_static = (
            not (REPORTS_DIR / "static_demo_report.jpg").exists()
            or not (REPORTS_DIR / "static_demo_report_thumb.jpg").exists()
        )
        if should_render_static:
            payload = ContentGenerationInput(
                session_id="static_demo_report",
                target_color="blue",
                distance_m=1240,
                steps=1843,
                duration_sec=720,
                best_match_score=0.87,
                badge_title="Blue Finder",
            )
            self.render_image_report(payload, basename="static_demo_report")

    def render_image_report(
        self,
        payload: ContentGenerationInput,
        shortform_plan: ShortformPlan | None = None,
        basename: str | None = None,
    ) -> Report:
        from PIL import Image, ImageDraw, ImageFont

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        CHARACTER_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_character_asset()

        file_base = safe_id(basename or payload.session_id)
        image_path = REPORTS_DIR / f"{file_base}.jpg"
        thumb_path = REPORTS_DIR / f"{file_base}_thumb.jpg"

        color = payload.target_color.lower()
        accent = COLOR_RGB.get(color, COLOR_RGB["blue"])
        width, height = 1080, 1920
        image = Image.new("RGB", (width, height), (248, 250, 252))
        draw = ImageDraw.Draw(image)

        for y in range(height):
            blend = y / height
            r = int((248 * (1 - blend)) + (accent[0] * blend * 0.42))
            g = int((250 * (1 - blend)) + (accent[1] * blend * 0.42))
            b = int((252 * (1 - blend)) + (accent[2] * blend * 0.42))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        font_title = self._font(ImageFont, 88)
        font_large = self._font(ImageFont, 64)
        font_medium = self._font(ImageFont, 42)
        font_small = self._font(ImageFont, 34)

        draw.text((72, 86), "ThiSpot", font=font_large, fill=(15, 23, 42))
        draw.text((72, 186), "Today's Color", font=font_medium, fill=(51, 65, 85))
        draw.text((72, 244), color.capitalize(), font=font_title, fill=accent)

        character = Image.open(CHARACTER_DIR / "base.png").convert("RGBA")
        character = character.resize((360, 360))
        image.paste(character, (646, 118), character)

        card_y = 610
        self._rounded_rect(draw, (72, card_y, 1008, card_y + 560), (255, 255, 255))
        stats = [
            ("distance", f"{payload.distance_m / 1000:.2f}km"),
            ("steps", f"{payload.steps:,}"),
            ("duration", self._format_duration(payload.duration_sec)),
            ("best match score", f"{int(round(payload.best_match_score * 100))}%"),
        ]
        x_positions = [126, 586]
        y_positions = [card_y + 90, card_y + 310]
        for index, (label, value) in enumerate(stats):
            x = x_positions[index % 2]
            y = y_positions[index // 2]
            draw.text((x, y), label, font=font_small, fill=(71, 85, 105))
            draw.text((x, y + 54), value, font=font_large, fill=(15, 23, 42))

        badge_y = 1260
        self._rounded_rect(draw, (72, badge_y, 1008, badge_y + 360), accent)
        draw.text((126, badge_y + 72), "badge", font=font_small, fill=(255, 255, 255))
        draw.text((126, badge_y + 132), payload.badge_title, font=font_large, fill=(255, 255, 255))
        draw.text(
            (126, badge_y + 232),
            f"I found today's {color} with ThiSpot.",
            font=font_medium,
            fill=(255, 255, 255),
        )

        draw.text(
            (72, 1740),
            "Mission proof complete",
            font=font_medium,
            fill=(15, 23, 42),
        )

        image.save(image_path, quality=92)
        image.resize((540, 960)).save(thumb_path, quality=88)

        video_path = self._render_mp4_from_image(image_path, file_base)
        return Report(
            type="video" if video_path else "image",
            video_url=f"{BASE_URL}/outputs/videos/{video_path.name}" if video_path else "",
            image_url=f"{BASE_URL}/outputs/reports/{image_path.name}",
            thumbnail_url=f"{BASE_URL}/outputs/reports/{thumb_path.name}",
            shortform_prompt=shortform_plan.generation_prompt if shortform_plan else "",
            style=shortform_plan.style if shortform_plan else "",
            caption=shortform_plan.share_caption if shortform_plan else "",
            storyboard=[
                scene.model_dump() for scene in shortform_plan.storyboard
            ] if shortform_plan else [],
        )

    def static_demo_report(self, session_id: str = "session_123") -> Report:
        self.ensure_demo_assets()
        image_path = REPORTS_DIR / "static_demo_report.jpg"
        video_path = VIDEOS_DIR / "static_demo_report.mp4"
        if not video_path.exists():
            self._render_mp4_from_image(image_path, "static_demo_report")
        has_video = video_path.exists()
        return Report(
            type="video" if has_video else "image",
            video_url=f"{BASE_URL}/outputs/videos/{video_path.name}" if has_video else "",
            image_url=f"{BASE_URL}/outputs/reports/static_demo_report.jpg",
            thumbnail_url=f"{BASE_URL}/outputs/reports/static_demo_report_thumb.jpg",
            shortform_prompt="Vertical 9:16 ThiSpot color mission recap with a cute avatar, mission proof stamp, walk stats, and badge unlock.",
            style="color-hunt vlog recap",
            caption="POV: I went outside just to find today's blue.",
            storyboard=[],
        )

    def _ensure_character_asset(self) -> None:
        from PIL import Image, ImageDraw

        path = CHARACTER_DIR / "base.png"
        if path.exists():
            return

        image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((126, 56, 386, 316), fill=(255, 255, 255), outline=(15, 23, 42), width=10)
        draw.ellipse((190, 150, 220, 180), fill=(15, 23, 42))
        draw.ellipse((292, 150, 322, 180), fill=(15, 23, 42))
        draw.arc((206, 178, 306, 250), 0, 180, fill=(15, 23, 42), width=8)
        draw.rounded_rectangle((146, 294, 366, 462), radius=58, fill=(59, 130, 246), outline=(15, 23, 42), width=8)
        draw.ellipse((70, 318, 166, 430), fill=(255, 255, 255), outline=(15, 23, 42), width=8)
        draw.ellipse((346, 318, 442, 430), fill=(255, 255, 255), outline=(15, 23, 42), width=8)
        image.save(path)

    @staticmethod
    def _render_mp4_from_image(image_path: Path, basename: str) -> Path | None:
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            return None

        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        video_path = VIDEOS_DIR / f"{basename}.mp4"
        try:
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(image_path),
                    "-t",
                    "5",
                    "-r",
                    "30",
                    "-vf",
                    "scale=1080:1920,format=yuv420p",
                    "-movflags",
                    "+faststart",
                    str(video_path),
                ],
                check=True,
                capture_output=True,
                timeout=20,
            )
        except Exception:
            return None
        return video_path if video_path.exists() else None

    @staticmethod
    def _rounded_rect(draw, box: tuple[int, int, int, int], fill: tuple[int, int, int]) -> None:
        draw.rounded_rectangle(box, radius=32, fill=fill)

    @staticmethod
    def _font(image_font, size: int):
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return image_font.truetype(candidate, size=size)
        return image_font.load_default()

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, remainder = divmod(int(seconds), 60)
        if minutes < 60:
            return f"{minutes}m {remainder:02d}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes:02d}m"
