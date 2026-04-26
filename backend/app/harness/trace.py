def make_trace(agent: str, message: str, status: str = "completed") -> dict:
    return {"agent": agent, "status": status, "message": message}
