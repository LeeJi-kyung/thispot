from app.models.schemas import RecommendColorRequest, RecommendColorResponse


class PersonalWalkAgent:
    COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    DEMO_ORDER = ["blue", "yellow", "orange", "violet", "indigo", "green", "red"]

    def run(self, request: RecommendColorRequest) -> RecommendColorResponse:
        recent = {color.lower() for color in request.previous_colors[-3:]}
        target = next((color for color in self.DEMO_ORDER if color not in recent), "blue")
        title_color = target.capitalize()
        return RecommendColorResponse(
            target_color=target,
            mission_title=f"{title_color} Energy Walk",
            mission_text=f"Find {target} moments during today's walk.",
            character_outfit_color=target,
        )
