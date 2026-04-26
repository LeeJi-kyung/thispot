import json
import os
from pathlib import Path

from app.models.schemas import AgentTrace, VisionResult
from app.skills.color_match_skill import ColorMatchSkill
from app.skills.image_color_skill import ImageColorSkill
from app.skills.object_label_skill import ObjectLabelSkill


class VisionMissionAgent:
    """Gemini-first mission proof agent with local HSV fallback."""

    def __init__(
        self,
        image_color_skill: ImageColorSkill | None = None,
        color_match_skill: ColorMatchSkill | None = None,
        object_label_skill: ObjectLabelSkill | None = None,
    ) -> None:
        self.image_color_skill = image_color_skill or ImageColorSkill()
        self.color_match_skill = color_match_skill or ColorMatchSkill()
        self.object_label_skill = object_label_skill or ObjectLabelSkill()

    def run(self, photo_path: Path, target_color: str) -> tuple[VisionResult, AgentTrace]:
        target = (target_color or "blue").lower()
        if os.getenv("GEMINI_API_KEY"):
            try:
                result = self._run_gemini(photo_path, target)
                return result, AgentTrace(
                    agent="VisionMissionAgent",
                    status="completed",
                    message=(
                        f"Gemini verified {target} proof - "
                        f"{int(round(result.match_score * 100))}% match"
                    ),
                )
            except Exception:
                result = self._run_local(photo_path, target)
                return result, AgentTrace(
                    agent="VisionMissionAgent",
                    status="fallback",
                    message=(
                        f"Gemini vision failed; local {target} detector used - "
                        f"{int(round(result.match_score * 100))}% match"
                    ),
                )

        result = self._run_local(photo_path, target)
        return result, AgentTrace(
            agent="VisionMissionAgent",
            status="fallback",
            message=(
                f"Gemini unavailable; local {target} detector used - "
                f"{int(round(result.match_score * 100))}% match"
            ),
        )

    def _run_local(self, photo_path: Path, target: str) -> VisionResult:
        pixels = self.image_color_skill.sample_pixels(photo_path)
        match_score = self.color_match_skill.score_pixels(pixels, target)
        is_matched = match_score >= 0.70
        label = self.object_label_skill.label(str(photo_path), target)
        status_text = "fits" if is_matched else "does not fit"
        evidence_text = "evidence was found" if is_matched else "evidence was not strong enough"
        return VisionResult(
            detected_color=target,
            match_score=match_score,
            is_matched=is_matched,
            object_label=label,
            feedback=(
                f"{target.capitalize()} {evidence_text} in this photo. "
                f"This {status_text} today's {target} mission."
            ),
        )

    def _run_gemini(self, photo_path: Path, target: str) -> VisionResult:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        image_bytes = photo_path.read_bytes()
        mime_type = self._mime_type(photo_path)
        prompt = f"""
You are ThiSpot's VisionMissionAgent.

Task:
- Verify whether the user's intended main subject proves today's target color mission.
- Target color: {target}
- First identify the main subject the user likely intended to photograph.
- The main subject is usually centered, large, foregrounded, in focus, or visually emphasized.
- Judge the target color only on that intended main subject.
- Do not accept tiny incidental details, background clutter, distant spectators, small logos, labels, stickers, reflections, UI text, or accidental color specks.
- A photo passes only when the intended main subject itself is clearly and meaningfully {target}.
- If the target color appears only as a minor accent on an otherwise different subject, return a low score.
- Return detected_color as exactly "{target}" for API compatibility.
- match_score must be between 0.0 and 1.0.
- Use match_score >= 0.70 only when the main subject clearly satisfies the target color mission.
- object_label should name the intended main subject, not a tiny colored detail.
- feedback should be one concise sentence for a mobile UI.

Return JSON matching the schema exactly.
"""
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VisionResult,
                temperature=0.1,
            ),
        )

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, VisionResult):
            return self._normalize_result(parsed, target)

        text = getattr(response, "text", "") or ""
        return self._normalize_result(VisionResult.model_validate(json.loads(text)), target)

    def _normalize_result(self, result: VisionResult, target: str) -> VisionResult:
        score = max(0.0, min(1.0, float(result.match_score)))
        return VisionResult(
            detected_color=target,
            match_score=round(score, 2),
            is_matched=score >= 0.70,
            object_label=result.object_label or self.object_label_skill.label("", target),
            feedback=result.feedback or f"{target.capitalize()} proof checked.",
        )

    @staticmethod
    def _mime_type(photo_path: Path) -> str:
        suffix = photo_path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if suffix == ".png":
            return "image/png"
        if suffix == ".webp":
            return "image/webp"
        return "image/jpeg"

    def fallback(self, target_color: str = "blue") -> tuple[VisionResult, AgentTrace]:
        detected_color = (target_color or "blue").lower()
        result = VisionResult(
            detected_color=detected_color,
            match_score=0.0,
            is_matched=False,
            object_label="unknown subject",
            feedback=(
                "We could not verify this photo. Please try another mission proof."
            ),
        )
        trace = AgentTrace(
            agent="VisionMissionAgent",
            status="fallback",
            message=f"{detected_color.capitalize()} proof could not be verified",
        )
        return result, trace
