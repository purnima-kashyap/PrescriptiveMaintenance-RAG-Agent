from langgraph.graph import StateGraph, END

from app.agent.state import RepairAgentState
from app.agent.nodes import (
    generate_query_node,
    retrieve_context_node,
    build_prompt_node,
    generate_repair_plan_node,
)

# Create the graph
workflow = StateGraph(RepairAgentState)

# Add nodes
workflow.add_node("generate_query", generate_query_node)
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("build_prompt", build_prompt_node)
workflow.add_node("generate_repair_plan", generate_repair_plan_node)

# Define execution flow
workflow.set_entry_point("generate_query")

workflow.add_edge("generate_query", "retrieve_context")
workflow.add_edge("retrieve_context", "build_prompt")
workflow.add_edge("build_prompt", "generate_repair_plan")
workflow.add_edge("generate_repair_plan", END)

# Compile graph
repair_graph = workflow.compile()