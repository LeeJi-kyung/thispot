"""RewardAgent — determines badge title/rarity and generates badge image via Imagen 2."""

import os
from pathlib import Path

from app.models.schemas import AgentTrace, Badge
from app.skills.image_generate_skill import (
    build_badge_prompt,
    extract_structured_keywords,
    generate_badge_image,
)

_OUTPUTS = Path(__file__).resolve().parents[2] / "outputs"


def _determine_badge(color: str, is_new_spot: bool, match_score: float) -> tuple[str, str, str]:
    c = color.capitalize()
    if is_new_spot:
        return f"{c} First Finder", f"You were one of the first to find today's {color} spot.", "rare"
    if match_score >= 0.8:
        return f"{c} Color Hunter", f"Impressive {int(match_score * 100)}% color match on your {color} walk.", "epic"
    return f"{c} Walker", f"Completed today's {color} color walk.", "common"


class RewardAgent:
    def run(
        self,
        color: str,
        is_new_spot: bool,
        match_score: float,
        session_id: str,
        photo_paths: list[Path] | None = None,
        base_url: str = "http://localhost:8000",
    ) -> tuple[Badge, AgentTrace]:
        title, description, rarity = _determine_badge(color, is_new_spot, match_score)

        # Step 1: extract structured keywords from walk photos
        keywords: list[dict] = []
        api_key = os.getenv("GEMINI_API_KEY")
        if photo_paths and api_key:
            keywords = extract_structured_keywords(photo_paths, api_key, target_color=color)
            print(f"[reward] extracted keywords from {len(keywords)} photo(s)")

        # Step 2: build prompt and generate badge image
        prompt = build_badge_prompt(title, color, rarity, keywords or None)
        print(f"[reward] badge prompt:\n{prompt}")

        image_url: str | None = None
        badge_path = _OUTPUTS / "reports" / f"{session_id}_badge.png"
        if generate_badge_image(prompt, badge_path):
            image_url = f"{base_url}/outputs/reports/{session_id}_badge.png"

        badge = Badge(title=title, description=description, rarity=rarity, image_url=image_url)
        trace = AgentTrace(agent="RewardAgent", status="completed", message=f"{title} badge created")
        return badge, trace
