class BadgeSkill:
    def rarity(self, *, is_new_spot: bool, match_score: float) -> str:
        if is_new_spot and match_score >= 0.85:
            return "rare"
        if match_score >= 0.70:
            return "standard"
        return "common"
