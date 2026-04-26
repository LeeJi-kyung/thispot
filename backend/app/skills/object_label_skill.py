class ObjectLabelSkill:
    """Deterministic object labels for the local MVP color matcher."""

    def label(self, image_path: str, color: str = "blue") -> str:
        labels = {
            "red": "sign",
            "orange": "flower",
            "yellow": "light",
            "green": "leaf",
            "blue": "sky",
            "violet": "flower",
            "white": "cloud",
            "black": "shadow",
        }
        return labels.get(color, "sky")
