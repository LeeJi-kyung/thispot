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
        shortform_plan, director_trace = self.director.generate_with_trace(payload)
        report = self.renderer.render_image_report(payload, shortform_plan=shortform_plan)
        status = "fallback" if director_trace.status == "fallback" or report.type == "image" else "completed"
        report.status = status
        report.can_share_to_instagram_story = bool(report.share_media_url and status in {"completed", "fallback"})
        message = director_trace.message if director_trace.status == "fallback" else "Short-form report generated"
        if report.type == "image" and director_trace.status != "fallback":
            message = "MP4 render unavailable; image report generated"
        return report, AgentTrace(
            agent="ContentGenerationAgent",
            status=status,
            message=message,
        )

    def fallback(self, session_id: str = "session_123") -> tuple[Report, AgentTrace]:
        report = self.renderer.static_demo_report(session_id)
        return report, AgentTrace(
            agent="ContentGenerationAgent",
            status="fallback",
            message="Static demo report returned",
        )
