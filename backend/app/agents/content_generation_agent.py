from app.models.schemas import AgentTrace, ContentGenerationInput, Report
from app.skills.report_render_skill import ReportRenderSkill
from app.skills.shortform_director_skill import ShortformDirectorSkill


class ContentGenerationAgent:
    def __init__(
        self,
        renderer: ReportRenderSkill | None = None,
        director: ShortformDirectorSkill | None = None,
    ) -> None:
        self.renderer = renderer or ReportRenderSkill()
        self.director = director or ShortformDirectorSkill()

    def run(self, payload: ContentGenerationInput) -> tuple[Report, AgentTrace]:
        shortform_plan = self.director.generate(payload)
        report = self.renderer.render_image_report(payload, shortform_plan=shortform_plan)
        return report, AgentTrace(
            agent="ContentGenerationAgent",
            status="completed",
            message="Short-form report generated",
        )

    def fallback(self, session_id: str = "session_123") -> tuple[Report, AgentTrace]:
        report = self.renderer.static_demo_report(session_id)
        return report, AgentTrace(
            agent="ContentGenerationAgent",
            status="fallback",
            message="Static demo report returned",
        )
