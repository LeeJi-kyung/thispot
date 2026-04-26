"""VisionMissionAgent — verifies photo proof for a color mission."""

from PIL import Image

from app.models.schemas import VisionResult
from app.skills.color_match_skill import compute_match
from app.skills.image_color_skill import extract_dominant_color
from app.skills.object_label_skill import label_object

MATCH_THRESHOLD = 0.70


def run(image: Image.Image, target_color: str) -> tuple[VisionResult, str]:
    """Analyze image against target color. Returns (VisionResult, trace_message)."""
    color_info = extract_dominant_color(image)
    dominant_color = color_info["dominant_color"]
    dominant_hue = color_info["dominant_hue"]

    match_score = compute_match(dominant_hue, target_color)
    is_matched = match_score >= MATCH_THRESHOLD

    object_label = label_object(image, dominant_color, dominant_hue)

    if is_matched:
        feedback = (
            f"{detected_cap(dominant_color)} {object_label} detected. "
            "This fits today's mission."
        )
    else:
        feedback = (
            f"{detected_cap(dominant_color)} {object_label} detected. "
            f"{int(match_score * 100)}% match — mission not verified."
        )

    trace_msg = f"{detected_cap(dominant_color)} {object_label} detected - {int(match_score * 100)}% match"

    result = VisionResult(
        detected_color=dominant_color,
        match_score=match_score,
        is_matched=is_matched,
        object_label=object_label,
        feedback=feedback,
    )
    return result, trace_msg


def detected_cap(color: str) -> str:
    return color.capitalize()
