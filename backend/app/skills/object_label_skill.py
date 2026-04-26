class ObjectLabelSkill:
    """Reserved for post-MVP object labels. Not used by the demo stub."""

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
