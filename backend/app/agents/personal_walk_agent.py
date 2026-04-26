from app.models.schemas import RecommendColorRequest, RecommendColorResponse


class PersonalWalkAgent:
    COLORS = ["red", "orange", "yellow", "green", "blue", "violet", "white", "black"]
    DEMO_ORDER = ["blue", "yellow", "orange", "violet", "white", "black", "green", "red"]

    def run(self, request: RecommendColorRequest) -> RecommendColorResponse:
        recent = {color.lower() for color in request.previous_colors[-3:]}
        candidates = [color for color in self.DEMO_ORDER if color not in recent] or self.DEMO_ORDER
        offset = max(0, len(request.previous_colors) - 3)
        target = candidates[offset % len(candidates)]
        title_color = target.capitalize()
        return RecommendColorResponse(
            target_color=target,
            mission_title=f"{title_color} Energy Walk",
            mission_text=f"Find {target} moments during today's walk.",
            character_outfit_color=target,
        )
