import json
from src import config

def check_escalation_rules(
    user_query: str, 
    persona_data: dict, 
    context_chunks: list, 
    chat_history: list = None
) -> tuple[bool, str, dict | None]:
    """
    Evaluates whether a conversation needs to be escalated to a human support representative.
    
    Returns:
        (should_escalate: bool, reason: str, handoff_data: dict | None)
    """
    if chat_history is None:
        chat_history = []
        
    query_lower = user_query.lower()
    
    # Trigger 1: Explicit Human Requests
    human_triggers = [
        "human", "representative", "agent", "support person", "talk to someone", 
        "operator", "real person", "live chat", "connect me", "speak to a manager"
    ]
    if any(trigger in query_lower for trigger in human_triggers):
        handoff = generate_handoff_data(
            user_query, persona_data, context_chunks, chat_history, 
            reason="User explicitly requested human assistance"
        )
        return True, "User requested human agent", handoff
        
    # Trigger 2: Sensitive Billing, Security, or Legal Topics (detected by classifier or config keywords)
    if persona_data.get("is_sensitive", False):
        handoff = generate_handoff_data(
            user_query, persona_data, context_chunks, chat_history, 
            reason="Sensitive business topic detected (billing, security audit, refund, account deletion)"
        )
        return True, "Sensitive issue detected", handoff
        
    # Trigger 3: Low Retrieval Confidence or No Info Found in RAG
    best_score = max([chunk["score"] for chunk in context_chunks]) if context_chunks else 0.0
    
    if len(context_chunks) == 0 or best_score < config.CONFIDENCE_THRESHOLD:
        reason = f"No documentation matches query (Confidence: {best_score} < Threshold: {config.CONFIDENCE_THRESHOLD})"
        handoff = generate_handoff_data(
            user_query, persona_data, context_chunks, chat_history, 
            reason=reason
        )
        return True, "Low retrieval confidence", handoff
        
    # Trigger 4: Unresolved Repeated Frustration
    # If the user's sentiment is repeatedly Negative/Frustrated over consecutive turns, escalate.
    frustration_count = 0
    if persona_data.get("sentiment") == "Negative/Frustrated":
        frustration_count += 1
        
    # Check history (look at the last 3 user messages)
    user_history = [msg for msg in chat_history if msg.get("role") == "user"]
    for old_msg in reversed(user_history[-3:]):
        # We can extract metadata from old messages
        old_meta = old_msg.get("metadata", {})
        if old_meta.get("sentiment") == "Negative/Frustrated":
            frustration_count += 1
            
    if frustration_count >= 3:
        reason = "User sentiment indicates persistent unresolved frustration across multiple turns"
        handoff = generate_handoff_data(
            user_query, persona_data, context_chunks, chat_history, 
            reason=reason
        )
        return True, "Persistent customer frustration", handoff

    # Otherwise, continue with automated response
    return False, "", None

def generate_handoff_data(
    user_query: str, 
    persona_data: dict, 
    context_chunks: list, 
    chat_history: list,
    reason: str
) -> dict:
    """Compiles a detailed, structured JSON handoff summary for a human agent ticket."""
    
    best_score = max([c["score"] for c in context_chunks]) if context_chunks else 0.0
    sources = list(set([c["source"] for c in context_chunks])) if context_chunks else []
    
    # Extract attempted steps based on user query and sources retrieved
    attempted_actions = []
    if sources:
        attempted_actions.append(f"Searched support database for: {', '.join(sources)}")
    else:
        attempted_actions.append("Searched support database (no matching records found)")
        
    # Formulate recommendations based on topic keyword matching
    rec = "Inspect logs and contact customer to resolve the inquiry."
    q_low = user_query.lower()
    
    if "refund" in q_low or "billing" in q_low or "charge" in q_low:
        rec = "Locate user's payment transaction history in Stripe, check invoice status, and process credit if duplicate exists."
    elif "password" in q_low or "reset" in q_low or "login" in q_low:
        rec = "Verify if account is locked due to login attempts. If necessary, manually issue password reset link from Admin Panel."
    elif "api" in q_low or "bearer" in q_low or "webhook" in q_low:
        rec = "Inspect server-side API execution logs for the user's client IP and trace authorization bearer failures."
    elif "cancel" in q_low or "close" in q_low or "delete" in q_low:
        rec = "Confirm customer's active account details, verify ownership, and proceed with account termination procedures."
        
    history_summary = []
    for msg in chat_history[-6:]: # Include up to last 6 messages for context
        role = "Agent" if msg.get("role") == "assistant" else "Customer"
        text = msg.get("content", "")
        # truncate large text
        if len(text) > 80:
            text = text[:80] + "..."
        history_summary.append(f"{role}: {text}")
        
    handoff_summary = {
        "escalation_status": "PENDING_HUMAN_REVIEW",
        "escalation_reason": reason,
        "persona": persona_data.get("persona", "Unknown"),
        "detected_sentiment": persona_data.get("sentiment", "Neutral"),
        "detected_issue": user_query[:120] + ("..." if len(user_query) > 120 else ""),
        "retrieved_sources": sources,
        "best_similarity_score": best_score,
        "actions_already_attempted": attempted_actions,
        "recommended_action": rec,
        "conversation_snippet": history_summary
    }
    
    return handoff_summary
