from app.agent.state import RepairAgentState
from app.query_generate.query_generator import generate_query
from app.vectorstore.vector_store import query_manuals
from app.prompts.repair_prompt import build_repair_prompt
from app.llm.ollama_client import generate_response
from app.models.iot_models import IoTAlert


async def generate_query_node(state: RepairAgentState):
    """
    Generate a search query from the IoT alert.
    """

    alert = IoTAlert(**state["alert"])
    query = generate_query(alert)

    return {
        "query": query
    }


async def retrieve_context_node(state: RepairAgentState):
    """
    Retrieve relevant manual chunks from ChromaDB.
    """

    hits = await query_manuals(state["query"])

    print("\n========== CHROMA HITS ==========")
    print(hits)

    context = "\n\n".join(
        [
            f"Manual: {hit['manual_name']}\n"
            f"Page: {hit['page_number']}\n"
            f"{hit['text']}"
            for hit in hits
        ]
    )

    print("\n========== RETRIEVED CONTEXT ==========")
    print(context)

    return {
        "retrieved_context": context
    }


async def build_prompt_node(state: RepairAgentState):
    """
    Build the LLM prompt.
    """

    prompt = build_repair_prompt(
        alert=state["alert"],
        retrieved_context=state["retrieved_context"],
    )

    print("\n========== FINAL PROMPT ==========")
    print(prompt)

    return {
        "prompt": prompt
    }


async def generate_repair_plan_node(state: RepairAgentState):
    """
    Generate the repair plan using Ollama.
    """

    repair_plan = generate_response(state["prompt"])

    print("\n========== LLM RESPONSE ==========")
    print(repair_plan)

    return {
        "repair_plan": repair_plan
    }