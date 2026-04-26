import os
from pathlib import Path

from app.models.schemas import AgentTrace, Badge
from app.skills.image_generate_skill import (
    build_badge_prompt,
    extract_structured_keywords,
    generate_badge_image,
)


APP_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = APP_DIR / "outputs" / "reports"


class RewardAgent:
    def run(
        self,
        *,
        target_color: str,
        best_match_score: float,
        is_new_spot: bool,
        session_id: str = "session_123",
        photo_paths: list[Path] | None = None,
        base_url: str = "http://localhost:8000",
    ) -> tuple[Badge, AgentTrace]:
        color_name = target_color.capitalize()

        if is_new_spot and best_match_score >= 0.85:
            badge = Badge(
                title=f"{color_name} First Finder",
                description=f"You were one of the first to find today's {target_color} spot.",
                rarity="rare",
            )
        elif best_match_score >= 0.70:
            badge = Badge(
                title=f"{color_name} Finder",
                description=f"You found today's {target_color} during your walk.",
                rarity="standard",
            )
        else:
            badge = Badge(
                title="Try Again",
                description=f"Keep looking for today's {target_color} mission.",
                rarity="common",
            )

        image_generated = self._attach_badge_image(
            badge=badge,
            target_color=target_color,
            session_id=session_id,
            photo_paths=photo_paths or [],
            base_url=base_url,
        )
        message = f"{badge.title} badge created"
        if image_generated:
            message = f"{badge.title} badge image generated"
        elif os.getenv("GEMINI_API_KEY"):
            message = f"{badge.title} badge created; image generation unavailable"

        return badge, AgentTrace(
            agent="RewardAgent",
            status="completed",
            message=message,
        )

    def fallback(self, target_color: str = "blue") -> tuple[Badge, AgentTrace]:
        badge = Badge(
            title=f"{target_color.capitalize()} First Finder",
            description=f"You were one of the first to find today's {target_color} spot.",
            rarity="rare",
        )
        return badge, AgentTrace(
            agent="RewardAgent",
            status="fallback",
            message=f"{badge.title} badge created",
        )

    def _attach_badge_image(
        self,
        *,
        badge: Badge,
        target_color: str,
        session_id: str,
        photo_paths: list[Path],
        base_url: str,
    ) -> bool:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False

        keywords = extract_structured_keywords(
            photo_paths,
            api_key=api_key,
            target_color=target_color,
        )
        prompt = build_badge_prompt(color=target_color, keywords=keywords or None)
        file_base = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in session_id)
        image_path = REPORTS_DIR / f"{file_base}_badge.png"
        if not generate_badge_image(prompt, image_path):
            return False

        badge.image_url = f"{base_url.rstrip('/')}/outputs/reports/{image_path.name}"
        return True
