def build_repair_prompt(alert: dict, retrieved_context: str) -> str:
    """
    Builds the prompt for the LLM using the IoT alert
    and the retrieved manual content.
    """

    return f"""
You are an expert Industrial Maintenance Engineer.

Your task is to help a maintenance technician diagnose and repair industrial machinery.

Use ONLY the information provided in the manual context below.
Do NOT make up information.
If the answer is not present in the manual, clearly state that.

IoT Alert:
{alert}

Manual Context:
{retrieved_context}

Generate the response in the following format:

1. Problem Diagnosis

2. Step-by-Step Repair Procedure

3. Required Tools

4. Required Spare Parts

5. Safety Precautions

6. Manual References (if available)
"""