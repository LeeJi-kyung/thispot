from app.models.schemas import AgentTrace, Badge


class RewardAgent:
    def run(
        self,
        *,
        target_color: str,
        best_match_score: float,
        is_new_spot: bool,
    ) -> tuple[Badge, AgentTrace]:
        color_name = target_color.capitalize()

        if is_new_spot and best_match_score >= 0.85:
            badge = Badge(
                title=f"{color_name} First Finder",
                description=f"You were one of the first to find today's {target_color} spot.",
                rarity="rare",
            )
        elif best_match_score >= 0.70:
            badge = Badge(
                title=f"{color_name} Finder",
                description=f"You found today's {target_color} during your walk.",
                rarity="standard",
            )
        else:
            badge = Badge(
                title="Try Again",
                description=f"Keep looking for today's {target_color} mission.",
                rarity="common",
            )

        return badge, AgentTrace(
            agent="RewardAgent",
            status="completed",
            message=f"{badge.title} badge created",
        )

    def fallback(self, target_color: str = "blue") -> tuple[Badge, AgentTrace]:
        badge = Badge(
            title=f"{target_color.capitalize()} First Finder",
            description=f"You were one of the first to find today's {target_color} spot.",
            rarity="rare",
        )
        return badge, AgentTrace(
            agent="RewardAgent",
            status="fallback",
            message=f"{badge.title} badge created",
        )
