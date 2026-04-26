"""Classify color names into 8 categories and match against a target."""

_CATEGORIES = ("red", "orange", "yellow", "green", "blue", "violet", "black", "white")

_KEYWORDS: dict[str, list[str]] = {
    "red": ["red", "crimson", "scarlet", "rose", "maroon", "burgundy", "ruby", "brick", "coral", "tomato"],
    "orange": ["orange", "amber", "peach", "apricot", "tangerine", "rust", "copper", "tan", "beige", "sienna", "umber", "tawny", "ochre"],
    "yellow": ["yellow", "gold", "lemon", "canary", "cream", "ivory", "sand", "wheat"],
    "green": ["green", "lime", "olive", "khaki", "emerald", "sage", "mint", "teal", "forest", "grass", "jade", "moss", "army", "military", "camouflage"],
    "blue": ["blue", "navy", "azure", "cobalt", "sky", "indigo", "sapphire", "cerulean", "steel", "slate", "periwinkle"],
    "violet": ["violet", "purple", "lavender", "magenta", "pink", "fuchsia", "plum", "mauve", "lilac"],
    "black": ["black", "dark", "charcoal", "ebony", "onyx", "jet"],
    "white": ["white", "snow", "light", "pale", "silver"],
}


def classify_color_name(name: str) -> str | None:
    """Map a free-form color name string to one of 8 canonical categories."""
    lower = name.lower()
    for category, keywords in _KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return None


def compute_match(dominant_hue: float, target_color: str) -> float:
    """Hue-distance score 0-1; kept for HSV fallback path."""
    _CANONICAL_HUES: dict[str, float] = {
        "red": 0.0, "orange": 30.0, "yellow": 60.0, "green": 120.0,
        "blue": 240.0, "indigo": 270.0, "violet": 300.0,
    }

    def _circular_dist(h1: float, h2: float) -> float:
        diff = abs(h1 - h2) % 360.0
        return min(diff, 360.0 - diff)

    target_hue = _CANONICAL_HUES.get(target_color.lower(), 0.0)
    dist = _circular_dist(dominant_hue, target_hue)
    return round(max(0.0, 1.0 - dist / 180.0), 2)
