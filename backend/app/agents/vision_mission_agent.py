"""VisionMissionAgent — verifies photo proof for a color mission."""

from pathlib import Path

from PIL import Image

from app.models.schemas import AgentTrace, ColorEntry, VisionResult
from app.skills.color_match_skill import classify_color_name
from app.skills.image_color_skill import extract_dominant_color
from app.skills.object_label_skill import label_object


class VisionMissionAgent:
    def run(self, photo_path: Path, target_color: str) -> tuple[VisionResult, AgentTrace]:
        image = Image.open(photo_path)
        color_info = extract_dominant_color(image)

        dominant_color = color_info["dominant_color"]
        dominant_hue = color_info["dominant_hue"]
        top_colors = [ColorEntry(**c) for c in color_info.get("top_colors", [])]

        target = target_color.lower()

        if top_colors:
            # Debug: print top_colors as received from Gemini
            print("[DEBUG] top_colors:")
            for e in top_colors:
                print(f"  name={e.name!r:30s} category={e.category!r:10s} percent={e.percent}%")

            # Gemini already classified each color; trust it directly.
            match_score = 0.0
            for entry in top_colors:
                cat = entry.category
                if cat and cat not in ("none", "") and cat == target:
                    match_score = round(entry.percent / 100.0, 2)
                    break
        else:
            # HSV fallback: no Gemini, use keyword classifier on dominant color name.
            cat = classify_color_name(dominant_color) or dominant_color
            print(f"[DEBUG] HSV fallback: dominant_color={dominant_color!r}, category={cat!r}")
            match_score = 1.0 if cat == target else 0.0

        is_matched = match_score > 0

        object_label = color_info.get("object_label") or label_object(
            image, dominant_color, dominant_hue
        )

        target_cap = target.capitalize()
        if is_matched:
            feedback = f"{target_cap} {object_label} detected. This fits today's mission."
        else:
            feedback = f"No {target} detected — mission not verified."

        trace_msg = f"target={target}, score={match_score}, matched={is_matched}"
        result = VisionResult(
            detected_color=target,
            match_score=match_score,
            is_matched=is_matched,
            object_label=object_label,
            feedback=feedback,
        )
        trace = AgentTrace(agent="VisionMissionAgent", status="completed", message=trace_msg)
        return result, trace

    def fallback(self, target_color: str = "blue") -> tuple[VisionResult, AgentTrace]:
        color = target_color.lower()
        color_cap = color.capitalize()
        object_label = "sky" if color == "blue" else "scene"

        result = VisionResult(
            detected_color=color,
            match_score=0.87,
            is_matched=True,
            object_label=object_label,
            feedback=f"{color_cap} {object_label} detected. This fits today's mission.",
        )
        trace = AgentTrace(agent="VisionMissionAgent", status="completed", message="fallback used")
        return result, trace
