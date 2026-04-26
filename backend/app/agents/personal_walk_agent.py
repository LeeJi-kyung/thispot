from app.models.schemas import RecommendColorRequest, RecommendColorResponse


class PersonalWalkAgent:
    COLORS = ["red", "orange", "yellow", "green", "blue", "violet", "white", "black"]
    DEMO_COLOR = "red"

    def run(self, request: RecommendColorRequest) -> RecommendColorResponse:
        target = self.DEMO_COLOR
        title_color = target.capitalize()
        return RecommendColorResponse(
            target_color=target,
            mission_title=f"{title_color} Energy Walk",
            mission_text=f"Find {target} moments during today's walk.",
            character_outfit_color=target,
        )
