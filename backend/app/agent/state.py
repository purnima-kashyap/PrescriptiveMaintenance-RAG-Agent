from typing import TypedDict, Optional


class RepairAgentState(TypedDict):
    """Shared state passed between all LangGraph nodes."""

    alert: dict
    query: str
    retrieved_context: str
    best_match_distance: Optional[float]
    prompt: str
    repair_plan: str
    inventory: dict