import os
from google import genai
from google.genai import types
from src import config

def get_gemini_client():
    api_key = config.GEMINI_API_KEY
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

def generate_adaptive_response(
    user_query: str, 
    persona: str, 
    context_chunks: list
) -> str:
    """
    Generates a personalized support response matching the classified user persona,
    fully grounded in the retrieved documentation context.
    """
    client = get_gemini_client()

    # 1. Establish the instruction set based on the classified persona
    if persona == "Technical Expert":
        persona_instructions = (
            "You are a Senior Systems Engineer. Provide clear root-cause analysis, "
            "configuration parameters, exact API pathways, code blocks, or technical logs. "
            "Keep technical descriptions highly detailed, accurate, and structured."
        )
    elif persona == "Frustrated User":
        persona_instructions = (
            "You are a deeply empathetic, reassuring Customer Care Specialist. "
            "Begin the response by explicitly acknowledging and validating their difficulty with warm, genuine care. "
            "Break down the solution into simple, reassuring, and straightforward action-oriented bullet steps. "
            "Avoid complex technical jargon and long blocks of text. Make them feel heard and supported."
        )
    else:  # Business Executive
        persona_instructions = (
            "You are a concise Client Relations Director. Focus on direct business outcomes, "
            "SLA timelines, and operational impact. Keep your response extremely brief (under 4-5 sentences), "
            "highly professional, and skip unnecessary configurations, code blocks, or system internals."
        )

    # 2. Assemble the context chunks
    context_text = ""
    for c in context_chunks:
        page_info = f" (Page {c['page']})" if c.get("page", 1) > 1 else ""
        context_text += f"Source [{c['source']}{page_info}]:\n{c['text']}\n\n"

    # 3. Formulate the final system instruction prompting the LLM
    full_system_prompt = (
        f"{persona_instructions}\n\n"
        "CRITICAL COMPLIANCE RULES:\n"
        "- Base your response ONLY on the provided Factual Context Documents.\n"
        "- Do not make up, assume, or hallucinate facts that are not present in the documents.\n"
        "- If the retrieved documents do not contain the answer, say 'I apologize, but I am unable to locate the precise solution to your request. I am connecting you with a live human support specialist.' and do not attempt to construct a solution.\n"
        "- Cite your sources (e.g., source file name) when providing the solution.\n\n"
        f"FACTUAL CONTEXT DOCUMENTS:\n{context_text}"
    )

    try:
        response = client.models.generate_content(
            model=config.GENERATION_MODEL,
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=full_system_prompt,
                temperature=0.2
            )
        )
        return response.text
    except Exception as e:
        print(f"Generation API error: {e}")
        return (
            "I apologize, but we are experiencing a service interruption. "
            "I am transferring this issue to a human agent for resolution."
        )
