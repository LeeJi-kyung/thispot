from app.models.schemas import AgentTrace, DiscoveryResult, VisionResult
from app.storage.spot_repository import (
    MERGE_RADIUS_M,
    nearest_same_color_spot,
    record_verified_spot,
    shared_user_percent,
)


class DiscoveryAgent:
    def run(
        self,
        *,
        target_color: str,
        lat: float | None,
        lng: float | None,
        vision_result: VisionResult,
    ) -> tuple[DiscoveryResult, AgentTrace]:
        nearest = nearest_same_color_spot(target_color=target_color, lat=lat, lng=lng)
        nearest_spot = nearest[0] if nearest and nearest[1] <= MERGE_RADIUS_M else None
        is_shared = nearest_spot is not None
        color_name = target_color.capitalize()

        if is_shared:
            result = DiscoveryResult(
                is_new_spot=False,
                shared_user_percent=shared_user_percent(nearest_spot),
                message=f"Shared {color_name} Spot found nearby.",
            )
        else:
            result = DiscoveryResult(
                is_new_spot=True,
                shared_user_percent=8,
                message=f"New {color_name} Spot discovered.",
            )

        trace = AgentTrace(
            agent="DiscoveryAgent",
            status="completed",
            message=result.message.rstrip("."),
        )
        return result, trace

    def record_verified_spot(
        self,
        *,
        user_id: str,
        session_id: str,
        photo_id: str,
        target_color: str,
        lat: float | None,
        lng: float | None,
        vision_result: VisionResult,
    ) -> None:
        if not vision_result.is_matched or vision_result.match_score < 0.70:
            return
        record_verified_spot(
            user_id=user_id,
            session_id=session_id,
            photo_id=photo_id,
            target_color=target_color,
            object_label=vision_result.object_label,
            lat=lat,
            lng=lng,
        )

    def fallback(self, target_color: str = "blue") -> tuple[DiscoveryResult, AgentTrace]:
        color_name = target_color.capitalize()
        result = DiscoveryResult(
            is_new_spot=True,
            shared_user_percent=8,
            message=f"New {color_name} Spot discovered.",
        )
        return result, AgentTrace(
            agent="DiscoveryAgent",
            status="fallback",
            message=result.message.rstrip("."),
        )
