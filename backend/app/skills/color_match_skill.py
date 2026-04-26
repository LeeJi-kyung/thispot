class ColorMatchSkill:
    """Reserved for post-MVP color matching. Not used by the demo stub."""

    def score(self, detected_color: str, target_color: str) -> float:
        return 0.87 if detected_color.lower() == target_color.lower() else 0.42
