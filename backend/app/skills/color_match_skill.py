"""Compare dominant image hue against a rainbow target color, returning a 0-1 score."""

_CANONICAL_HUES: dict[str, float] = {
    "red": 0.0,
    "orange": 30.0,
    "yellow": 60.0,
    "green": 120.0,
    "blue": 240.0,
    "indigo": 270.0,
    "violet": 300.0,
}


def _circular_dist(h1: float, h2: float) -> float:
    diff = abs(h1 - h2) % 360.0
    return min(diff, 360.0 - diff)


def compute_match(dominant_hue: float, target_color: str) -> float:
    """Return match score 0-1 between dominant hue and target rainbow color.

    Score is purely hue-distance based: 1.0 at 0° distance, 0.0 at 180°.
    Threshold for is_matched: >= 0.70 (i.e., within ~54° of target).
    """
    target_hue = _CANONICAL_HUES.get(target_color.lower(), 0.0)
    dist = _circular_dist(dominant_hue, target_hue)
    score = max(0.0, 1.0 - dist / 180.0)
    return round(score, 2)
