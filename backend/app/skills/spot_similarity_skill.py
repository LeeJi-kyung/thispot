class SpotSimilaritySkill:
    def is_same_color(self, spot_color: str, target_color: str) -> bool:
        return spot_color.lower() == target_color.lower()

    def is_shared_spot(self, *, distance_m: float | None, spot_color: str, target_color: str) -> bool:
        return (
            distance_m is not None
            and distance_m <= 50
            and self.is_same_color(spot_color, target_color)
        )
