from __future__ import annotations

import json
import os

from app.models.schemas import ContentGenerationInput, ShortformPlan, ShortformScene


class ShortformDirectorSkill:
    def generate(self, payload: ContentGenerationInput) -> ShortformPlan:
        if os.getenv("GEMINI_API_KEY"):
            try:
                return self._generate_with_gemini(payload)
            except Exception:
                return self.fallback(payload)
        return self.fallback(payload)

    def _generate_with_gemini(self, payload: ContentGenerationInput) -> ShortformPlan:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        prompt = self._director_prompt(payload)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ShortformPlan,
                temperature=0.9,
            ),
        )

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, ShortformPlan):
            return parsed

        text = getattr(response, "text", "") or ""
        data = json.loads(text)
        return ShortformPlan.model_validate(data)

    def fallback(self, payload: ContentGenerationInput) -> ShortformPlan:
        color = payload.target_color.lower()
        match_percent = int(round(payload.best_match_score * 100))
        distance_km = payload.distance_m / 1000
        return ShortformPlan(
            style="color-hunt vlog recap",
            music_direction="bright lo-fi pop beat with camera shutter and stamp pop SFX",
            share_caption=f"POV: I went outside just to find today's {color}.",
            storyboard=[
                ShortformScene(
                    scene=1,
                    caption=f"today's mission: find {color.upper()}",
                    visual=f"cute ThiSpot avatar pops in wearing {color}",
                    transition="quick zoom",
                ),
                ShortformScene(
                    scene=2,
                    caption="went for a tiny walk...",
                    visual=f"soft map route appears with {distance_km:.2f}km progress",
                    transition="map swipe",
                ),
                ShortformScene(
                    scene=3,
                    caption=f"{color} spotted",
                    visual="best mission photo appears inside a rounded phone frame",
                    transition="camera flash",
                ),
                ShortformScene(
                    scene=4,
                    caption=f"{match_percent}% mission match",
                    visual="AI proof badge stamps onto the photo",
                    transition="stamp pop",
                ),
                ShortformScene(
                    scene=5,
                    caption=f"{payload.badge_title} unlocked",
                    visual="avatar celebrates with badge, steps, and color recap",
                    transition="confetti burst",
                ),
            ],
            generation_prompt=self._video_generation_prompt(payload),
        )

    def _director_prompt(self, payload: ContentGenerationInput) -> str:
        color = payload.target_color.lower()
        match_percent = int(round(payload.best_match_score * 100))
        distance_km = payload.distance_m / 1000
        duration = self._format_duration(payload.duration_sec)
        return f"""
You are a short-form video creative director for ThiSpot, an AI color mission walking app.

Create a trendy vertical short-form video concept for Instagram Reels/TikTok.

Input:
- Today's color: {color}
- Distance: {distance_km:.2f} km
- Steps: {payload.steps}
- Duration: {duration}
- Best match score: {match_percent}%
- Badge: {payload.badge_title}
- User character: cute walking avatar
- Available user photos: {len(payload.photo_paths)}
- Format: 9:16 vertical video

Return JSON matching this schema:
- style: short creative style name
- music_direction: music and SFX direction
- share_caption: one social caption
- storyboard: exactly 5 scenes, each with scene number, caption, visual, transition
- generation_prompt: one concise prompt for a downstream AI video generator

Constraints:
- Make it feel like a trendy TikTok/Reels recap.
- Keep it positive, lightweight, and playful.
- Emphasize real-world color mission proof.
- Do not mention calories.
- Do not sound like a fitness dashboard.
"""

    def _video_generation_prompt(self, payload: ContentGenerationInput) -> str:
        color = payload.target_color.lower()
        match_percent = int(round(payload.best_match_score * 100))
        distance_km = payload.distance_m / 1000
        return (
            "Vertical 9:16 trendy TikTok/Reels recap for ThiSpot. "
            f"A cute walking avatar wearing {color} completes a real-world color mission. "
            f"Show quick scenes: today's {color} mission, a soft map route, user photo moment, "
            f"AI proof stamp with {match_percent}% match, and {payload.badge_title} badge unlock. "
            f"Include stats: {distance_km:.2f}km, {payload.steps:,} steps. "
            "Playful, bright, modern mobile UI, camera flash transitions, sticker-like captions."
        )

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, remainder = divmod(int(seconds), 60)
        if minutes < 60:
            return f"{minutes}m {remainder:02d}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes:02d}m"
