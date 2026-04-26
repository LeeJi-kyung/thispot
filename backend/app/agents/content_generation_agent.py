"""ContentGenerationAgent — shortform plan + image report."""

from app.models.schemas import AgentTrace, ContentGenerationInput, Report
from app.skills.report_render_skill import ReportRenderSkill
from app.skills.shortform_director_skill import ShortformDirectorSkill


class ContentGenerationAgent:
    def __init__(self) -> None:
        self.director = ShortformDirectorSkill()
        self.renderer = ReportRenderSkill()

    def run(
        self,
        payload: ContentGenerationInput,
        base_url: str = "http://localhost:8000",
    ) -> tuple[Report, AgentTrace]:
        plan, plan_trace = self.director.generate(payload)
        report = self.renderer.render(payload, plan, plan_trace.status, base_url)
        return report, AgentTrace(
            agent="ContentGenerationAgent",
            status=plan_trace.status,
            message=plan_trace.message,
        )
