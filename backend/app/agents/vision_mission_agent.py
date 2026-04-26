from pathlib import Path

from app.models.schemas import AgentTrace, VisionResult


class VisionMissionAgent:
    """Demo-only stub. It does not inspect image pixels or call a vision model."""

    def run(self, photo_path: Path, target_color: str) -> tuple[VisionResult, AgentTrace]:
        detected_color = (target_color or "blue").lower()
        label = self._label_for_color(detected_color)
        result = VisionResult(
            detected_color=detected_color,
            match_score=0.87,
            is_matched=True,
            object_label=label,
            feedback=(
                f"{detected_color.capitalize()} {label} detected. "
                "This fits today's mission."
            ),
        )
        trace = AgentTrace(
            agent="VisionMissionAgent",
            status="completed",
            message=f"{detected_color.capitalize()} {label} detected - 87% match",
        )
        return result, trace

    def fallback(self, target_color: str = "blue") -> tuple[VisionResult, AgentTrace]:
        return self.run(Path("demo_fallback.jpg"), target_color)

    @staticmethod
    def _label_for_color(color: str) -> str:
        labels = {
            "red": "sign",
            "orange": "flower",
            "yellow": "light",
            "green": "leaf",
            "blue": "sky",
            "indigo": "wall",
            "violet": "flower",
        }
        return labels.get(color, "sky")
