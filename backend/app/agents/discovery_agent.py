"""DiscoveryAgent — determines whether photo location is a new or shared color spot.

# TODO: Lane C owns the real geo-distance + spot similarity impl.
# This stub always reports a new spot so the demo path works end-to-end.
"""

from app.models.schemas import DiscoveryResult


def run(
    target_color: str,
    lat: float | None,
    lng: float | None,
) -> tuple[DiscoveryResult, str]:
    """Return discovery result and trace message."""
    color_cap = target_color.capitalize()
    result = DiscoveryResult(
        is_new_spot=True,
        shared_user_percent=0,
        message=f"New {color_cap} Spot discovered.",
    )
    trace_msg = f"New {color_cap} Spot discovered"
    return result, trace_msg
