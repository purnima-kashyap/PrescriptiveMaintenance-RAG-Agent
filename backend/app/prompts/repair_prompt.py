def build_repair_prompt(
    alert: dict,
    retrieved_context: str,
    error_code_found: bool,
    machine_id_found: bool = False,
    best_match_distance: float = None,
) -> str:
    """
    Builds the prompt for the LLM using the IoT alert and retrieved manual
    content.

    error_code_found and machine_id_found are computed deterministically in
    Python (exact substring match against retrieved_context) BEFORE this
    prompt is built, rather than relying on embedding distance alone or
    trusting the LLM to self-verify. This catches the case where a strong
    error-code match lowers the overall similarity distance even though the
    actual machine/model name never appears in the manual at all.
    """
    error_code = alert.get("error_code", "UNKNOWN")
    machine_id = alert.get("machine_id", "UNKNOWN")

    code_status_note = (
        f'[VERIFIED FACT: The exact error code "{error_code}" WAS found in the '
        f"retrieved manual context below. You may treat it as confirmed.]"
        if error_code_found
        else
        f'[VERIFIED FACT: The exact error code "{error_code}" was NOT found anywhere '
        f"in the retrieved manual context below. This manual does not use this "
        f"numeric code — you MUST state this explicitly in Section 0, and clarify "
        f"that your diagnosis is based only on matching the reported symptom "
        f"(e.g. the temperature reading) to the manual's plain-language malfunction "
        f"descriptions, not the error code itself.]"
    )

    machine_status_note = (
        f'\n[VERIFIED FACT: The reported machine/model identifier "{machine_id}" WAS '
        f"found in the retrieved manual context below. You may treat this manual as "
        f"confirmed to cover this equipment.]"
        if machine_id_found
        else
        f'\n[VERIFIED FACT: The reported machine/model identifier "{machine_id}" was '
        f"NOT found anywhere in the retrieved manual context below, even though other "
        f"content (such as the error code) may match closely. You MUST state this "
        f"explicitly in Section 0C: the manual does not explicitly confirm it covers "
        f'this specific machine ("{machine_id}"). Recommend the technician verify the '
        f"machine's actual nameplate/model against this manual before relying fully on "
        f"this diagnosis, even though a plausible fix is provided below as a "
        f"best-effort fallback.]"
    )

    relevance_note = ""
    if best_match_distance is not None and best_match_distance > 0.65:
        relevance_note = (
            f'\n[SYSTEM WARNING: The best matching content had a similarity distance '
            f'of {best_match_distance:.2f}, which indicates only a WEAK overall match. '
            f'Factor this into Section 0C alongside the machine-id verification fact above.]'
        )

    return f"""
You are an expert Industrial Maintenance Engineer.

Your task is to help a maintenance technician diagnose and repair industrial machinery.

Use ONLY the information provided in the manual context below.
Do NOT make up information.

{code_status_note}
{machine_status_note}
{relevance_note}

Respond in EXACTLY this order. Do not skip or reorder any section:

SECTION 0 — Error Code Verification (required, write this first, 1-2 sentences):
State plainly whether the exact error code "{error_code}" was found in the
manual, using the verified fact above. Do not contradict it.

SECTION 0B — System/Subsystem Variant Check (required):
Look at the retrieved manual context below. List every distinct
system/subsystem variant present (e.g. different cooling system types,
different machine models, etc.).
- If only ONE variant is present, state that clearly and proceed normally.
- If MORE THAN ONE variant is present, you MUST state: "Multiple system
  variants detected in the retrieved context: [list them]. The technician
  must confirm which variant applies to this specific machine before
  proceeding." Then base your repair plan ONLY on the single most likely
  variant given the alert data, and clearly name which variant you chose
  and why — do NOT merge fixes from different variants together.

SECTION 0C — Equipment Scope Check (required):
Use the machine-id verified fact above. If the machine identifier was NOT
found in the manual, you MUST state this clearly and recommend verifying
the correct manual has been uploaded for this equipment, even if other
details (like the error code) matched well. If it WAS found, confirm scope
match and proceed normally.

1. Problem Diagnosis

2. Step-by-Step Repair Procedure

3. Required Tools

4. Required Spare Parts

5. Safety Precautions

6. Manual References (if available)

IoT Alert:
{alert}

Manual Context:
{retrieved_context}
"""