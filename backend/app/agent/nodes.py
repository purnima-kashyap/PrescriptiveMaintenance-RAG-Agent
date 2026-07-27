from app.agent.state import RepairAgentState
from app.query_generate.query_generator import generate_query
from app.vectorstore.vector_store import query_manuals
from app.prompts.repair_prompt import build_repair_prompt
from app.llm.ollama_client import generate_response_async
from app.models.iot_models import IoTAlert


async def generate_query_node(state: RepairAgentState):
    """Generate a search query from the IoT alert."""
    alert = IoTAlert(**state["alert"])
    query = generate_query(alert)

    return {
        "query": query
    }


async def retrieve_context_node(state: RepairAgentState):
    """Retrieve relevant manual chunks from ChromaDB."""
    hits = await query_manuals(state["query"])

    print("\n========== CHROMA HITS ==========")
    print(hits)

    best_distance = hits[0]["distance"] if hits else None
    print(f"\n========== BEST MATCH DISTANCE: {best_distance} ==========")

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
        "retrieved_context": context,
        "best_match_distance": best_distance,
    }


def _check_error_code_in_context(error_code: str, context: str) -> bool:
    """Deterministic exact-match check for the error code in retrieved text."""
    if not error_code:
        return False
    return error_code.strip().lower() in context.lower()


def _check_machine_id_in_context(machine_id: str, context: str) -> bool:
    """
    Deterministic check: does the reported machine_id (or a close variant)
    appear anywhere in the retrieved manual context? This catches cases
    where overall embedding distance is low (strong content match, e.g. a
    correctly matched error code) but the actual machine/model name itself
    doesn't appear anywhere in the manual — which the distance-based check
    alone can miss, since a strong error-code match can offset a weak
    machine-name match in the overall similarity score.
    """
    if not machine_id:
        return False
    return machine_id.strip().lower() in context.lower()


async def build_prompt_node(state: RepairAgentState):
    """Build the LLM prompt, with verified error-code, machine-id, and relevance facts."""
    error_code = state["alert"].get("error_code", "")
    machine_id = state["alert"].get("machine_id", "")

    error_code_found = _check_error_code_in_context(error_code, state["retrieved_context"])
    machine_id_found = _check_machine_id_in_context(machine_id, state["retrieved_context"])

    best_match_distance = state.get("best_match_distance")

    print(f"\n========== ERROR CODE CHECK ==========")
    print(f"'{error_code}' found in context: {error_code_found}")

    print(f"\n========== MACHINE ID CHECK ==========")
    print(f"'{machine_id}' found in context: {machine_id_found}")

    prompt = build_repair_prompt(
        alert=state["alert"],
        retrieved_context=state["retrieved_context"],
        error_code_found=error_code_found,
        machine_id_found=machine_id_found,
        best_match_distance=best_match_distance,
    )

    print("\n========== FINAL PROMPT ==========")
    print(prompt)

    return {
        "prompt": prompt
    }


async def generate_repair_plan_node(state: RepairAgentState):
    """Generate the repair plan using Ollama (async-safe, non-blocking)."""
    repair_plan = await generate_response_async(state["prompt"])

    print("\n========== LLM RESPONSE ==========")
    print(repair_plan)

    return {
        "repair_plan": repair_plan
    }