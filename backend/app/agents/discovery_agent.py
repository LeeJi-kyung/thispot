from app.models.schemas import AgentTrace, DiscoveryResult, VisionResult
from app.skills.geo_distance_skill import GeoDistanceSkill
from app.skills.spot_similarity_skill import SpotSimilaritySkill
from app.storage.mock_spots import MOCK_SPOTS


class DiscoveryAgent:
    def __init__(self) -> None:
        self.geo_distance = GeoDistanceSkill()
        self.similarity = SpotSimilaritySkill()

    def run(
        self,
        *,
        target_color: str,
        lat: float | None,
        lng: float | None,
        vision_result: VisionResult,
    ) -> tuple[DiscoveryResult, AgentTrace]:
        nearest_same_color_m = self._nearest_same_color_distance(target_color, lat, lng)
        is_shared = nearest_same_color_m is not None and nearest_same_color_m <= 50
        color_name = target_color.capitalize()

        if is_shared:
            result = DiscoveryResult(
                is_new_spot=False,
                shared_user_percent=42,
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

    def _nearest_same_color_distance(
        self, target_color: str, lat: float | None, lng: float | None
    ) -> float | None:
        if lat is None or lng is None:
            return None
        distances = []
        for spot in MOCK_SPOTS:
            if not self.similarity.is_same_color(spot["color"], target_color):
                continue
            distances.append(
                self.geo_distance.distance_meters(
                    lat,
                    lng,
                    float(spot["lat"]),
                    float(spot["lng"]),
                )
            )
        return min(distances) if distances else None
