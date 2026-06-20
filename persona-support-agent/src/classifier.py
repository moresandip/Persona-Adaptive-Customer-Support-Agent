import os
import json
from google import genai
from google.genai import types
from src import config

def get_gemini_client():
    api_key = config.GEMINI_API_KEY
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

def classify_customer_persona(user_message: str) -> dict:
    """
    Analyzes the user's message and classifies it into one of the three target personas:
    1. 'Technical Expert': Uses jargon, asks about APIs, code, logs, webhooks.
    2. 'Frustrated User': Uses emotional language, exclamation marks, or mentions urgency, delay.
    3. 'Business Executive': Focuses on business impact, pricing tiers, SLAs, timelines, ROI, and brevity.
    """
    client = get_gemini_client()

    system_instruction = (
        "You are an advanced classification engine. Your task is to analyze the "
        "sentiment, vocabulary, and tone of an incoming support message and classify "
        "it into exactly one of three customer personas:\n"
        "1. 'Technical Expert': Uses jargon, asks about APIs/code/configs.\n"
        "2. 'Frustrated User': Uses emotional language, exclamation marks, or mentions urgency.\n"
        "3. 'Business Executive': Focuses on business impact, ROI, timelines, and brevity.\n\n"
        "Also determine if the issue is highly sensitive (billing refunds, legal disputes, "
        "security breaches, or account cancellation requests) and capture the customer's sentiment."
    )

    # Define structured schema output
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "persona": {
                "type": "STRING",
                "enum": ["Technical Expert", "Frustrated User", "Business Executive"]
            },
            "confidence": {"type": "NUMBER"},
            "reasoning": {"type": "STRING"},
            "sentiment": {
                "type": "STRING",
                "enum": ["Positive", "Neutral", "Negative/Frustrated"]
            },
            "is_sensitive": {"type": "BOOLEAN"}
        },
        "required": ["persona", "confidence", "reasoning", "sentiment", "is_sensitive"]
    }

    try:
        response = client.models.generate_content(
            model=config.CLASSIFICATION_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1
            )
        )
        result = json.loads(response.text)
    except Exception as e:
        # Fallback in case of API error or invalid response format
        print(f"Classification API warning: {e}. Using rule-based fallback.")
        result = fallback_classification(user_message)

    # Programmatic safety override: check if keywords are present in user message
    msg_lower = user_message.lower()
    for word in config.SENSITIVE_TOPICS:
        if word in msg_lower:
            result["is_sensitive"] = True
            result["reasoning"] += f" (Triggered sensitive keyword override: '{word}')"
            break
            
    return result

def fallback_classification(user_message: str) -> dict:
    """Deterministic fallback logic when the API fails."""
    msg_lower = user_message.lower()
    
    # Technical checks
    tech_keywords = ["api", "bearer", "token", "header", "http", "curl", "webhook", "sdk", "endpoint", "database", "500 error", "401 unauthorized", "429"]
    exec_keywords = ["sla", "timeline", "uptime", "roi", "cost", "pricing", "pricing plan", "business", "operations", "executive", "impact"]
    frustrated_keywords = ["!", "urgent", "broken", "worst", "terrible", "angry", "disappointed", "waiting for hours", "fail", "nothing works", "demand"]
    
    tech_hits = sum(1 for w in tech_keywords if w in msg_lower)
    exec_hits = sum(1 for w in exec_keywords if w in msg_lower)
    frust_hits = sum(1 for w in frustrated_keywords if w in msg_lower)
    
    # Default outputs
    persona = "Business Executive"
    if tech_hits > exec_hits and tech_hits > frust_hits:
        persona = "Technical Expert"
    elif frust_hits > tech_hits and frust_hits > exec_hits:
        persona = "Frustrated User"
    elif tech_hits == 0 and frust_hits == 0 and exec_hits == 0:
        # Default fallback
        persona = "Frustrated User" if "!" in user_message or "?" in user_message else "Business Executive"
        
    is_sensitive = any(word in msg_lower for word in config.SENSITIVE_TOPICS)
    
    return {
        "persona": persona,
        "confidence": 0.5,
        "reasoning": "Rule-based fallback due to API execution exception.",
        "sentiment": "Negative/Frustrated" if frust_hits > 0 else "Neutral",
        "is_sensitive": is_sensitive
    }
