"""Generate a shortform video plan via Gemini, or a local fallback plan."""

import json
import os
import re

from app.models.schemas import AgentTrace, ContentGenerationInput, ShortformPlan, ShortformScene

try:
    from google import genai as _genai

    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

_PROMPT_TMPL = """\
Generate a shortform social media video plan for a color walk app.
User stats: {dist_km}km walked, {steps} steps, {duration_min} min, {match_pct}% color match for {color}.
Badge earned: {badge_title}.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "style": "color-hunt vlog recap",
  "caption": "POV: I went outside just to find today's {color}.",
  "shortform_prompt": "Vertical 9:16 trendy TikTok/Reels recap of a {color} color hunt walk.",
  "storyboard": [
    {{"scene": 1, "caption": "today's mission: find {color}", "visual": "ThiSpot avatar in {color}", "transition": "quick zoom"}},
    {{"scene": 2, "caption": "{dist_km}km · {steps} steps", "visual": "step counter spinning", "transition": "cut"}},
    {{"scene": 3, "caption": "{match_pct}% match ✓", "visual": "{color} circle filling up", "transition": "fade out"}}
  ]
}}

Rules:
- storyboard exactly 3 scenes
- captions: short, lowercase, trendy
- transitions: one of quick zoom / cut / fade out / wipe / slide
"""


def _fallback_plan(p: ContentGenerationInput) -> ShortformPlan:
    dist = round(p.distance_m / 1000, 2)
    pct = int(p.best_match_score * 100)
    color = p.target_color.lower()
    return ShortformPlan(
        style="color-hunt vlog recap",
        caption=f"POV: I went outside just to find today's {color}.",
        shortform_prompt=(
            f"Vertical 9:16 trendy TikTok/Reels recap of a {color} color hunt walk. "
            f"{dist}km, {p.steps:,} steps, {pct}% match."
        ),
        storyboard=[
            ShortformScene(scene=1, caption=f"today's mission: find {color.upper()}", visual=f"ThiSpot avatar wearing {color}", transition="quick zoom"),
            ShortformScene(scene=2, caption=f"{dist}km · {p.steps:,} steps", visual="step counter and map animating", transition="cut"),
            ShortformScene(scene=3, caption=f"{pct}% match ✓", visual=f"{color} color circle filling up", transition="fade out"),
        ],
    )


def _parse_plan(text: str) -> ShortformPlan:
    clean = re.sub(r"```(?:json)?\s*|```", "", text).strip()
    data = json.loads(clean)
    return ShortformPlan(
        style=data["style"],
        caption=data["caption"],
        shortform_prompt=data["shortform_prompt"],
        storyboard=[ShortformScene(**s) for s in data["storyboard"][:3]],
    )


class ShortformDirectorSkill:
    def generate(self, payload: ContentGenerationInput) -> tuple[ShortformPlan, AgentTrace]:
        if not os.getenv("GEMINI_API_KEY") or not _HAS_GENAI:
            return _fallback_plan(payload), AgentTrace(
                agent="ShortformDirectorSkill",
                status="fallback",
                message="GEMINI_API_KEY missing; local shortform plan used",
            )

        try:
            client = _genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            dist = round(payload.distance_m / 1000, 2)
            prompt = _PROMPT_TMPL.format(
                dist_km=dist,
                steps=f"{payload.steps:,}",
                duration_min=round(payload.duration_sec / 60),
                match_pct=int(payload.best_match_score * 100),
                color=payload.target_color.lower(),
                badge_title=payload.badge_title,
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt],
            )
            plan = _parse_plan(response.text)
            return plan, AgentTrace(
                agent="ShortformDirectorSkill",
                status="completed",
                message="Gemini shortform plan generated",
            )
        except Exception as e:
            print(f"[shortform] Gemini failed: {e}")
            return _fallback_plan(payload), AgentTrace(
                agent="ShortformDirectorSkill",
                status="fallback",
                message="Gemini failed; local shortform plan used",
            )
