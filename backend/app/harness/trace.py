from app.models.schemas import AgentTrace


def trace(agent: str, status: str, message: str) -> AgentTrace:
    return AgentTrace(agent=agent, status=status, message=message)
