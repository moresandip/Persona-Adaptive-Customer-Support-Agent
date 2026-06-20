import os
import sys
import json
from dotenv import load_dotenv

# Ensure the root folder is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.escalator import check_escalation_rules
from src.generator import generate_adaptive_response

def run_test_scenarios():
    load_dotenv()
    
    # Verify API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY environment variable is not set. API calls will fail.")
        
    print("==================================================")
    print("INITIALIZING LOCAL RAG PIPELINE & DATABASE")
    print("==================================================")
    
    rag = LocalRAGPipeline()
    # Ingest documents in data folder
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist. Run scripts/generate_kb.py first.")
        return
        
    rag.ingest_directory(data_dir, force_reindex=True)
    print(f"Chroma DB contains {rag.collection.count()} text chunks.")
    
    # 5 Standard Verification Scenarios
    scenarios = [
        {
            "id": 1,
            "message": "Where is the guide to clear cookies? It's been an hour and nothing is loading on your interface!",
            "desc": "Frustrated User (Cookie Guide)"
        },
        {
            "id": 2,
            "message": "What are the header parameter requirements for your bearer token auth implementation?",
            "desc": "Technical Expert (Bearer Token)"
        },
        {
            "id": 3,
            "message": "Our operational uptime is decreasing. We need a timeline of when billing disputes are resolved.",
            "desc": "Business Executive (Billing Dispute Timeline)"
        },
        {
            "id": 4,
            "message": "I'm experiencing an issue with your database integration that's causing internal errors.",
            "desc": "Technical Expert (Database integration)"
        },
        {
            "id": 5,
            "message": "My billing statement has unexpected duplicate charges. I demand an immediate refund!",
            "desc": "Escalation Check (Duplicate Billing Charge Refund)"
        }
    ]
    
    print("\n==================================================")
    print("RUNNING 5 SCENARIOS VERIFICATION")
    print("==================================================")
    
    for sc in scenarios:
        print(f"\nScenario #{sc['id']}: {sc['desc']}")
        print(f"User Query: \"{sc['message']}\"")
        
        # 1. Classification
        persona_info = classify_customer_persona(sc['message'])
        print(f"  - Detected Persona: {persona_info['persona']} (Confidence: {persona_info['confidence']})")
        print(f"  - Sentiment: {persona_info['sentiment']}")
        print(f"  - Sensitive: {persona_info['is_sensitive']}")
        print(f"  - Reasoning: {persona_info['reasoning']}")
        
        # 2. Retrieval
        context = rag.retrieve_context(sc['message'], top_k=2)
        print(f"  - Context retrieved: {len(context)} chunks.")
        for idx, chunk in enumerate(context):
            print(f"    * Chunk {idx+1}: {chunk['source']} (Similarity Score: {chunk['score']})")
            
        # 3. Escalation Check
        should_escalate, reason, handoff = check_escalation_rules(
            sc['message'], persona_info, context
        )
        
        if should_escalate:
            print(f"  - [ESCALATED TO HUMAN AGENT] - Reason: {reason}")
            print("  - Handoff Report Details:")
            print(json.dumps(handoff, indent=4))
        else:
            print("  - [AUTOMATED AGENT RESPONSE]")
            # 4. Generate Response
            response_text = generate_adaptive_response(
                sc['message'], persona_info['persona'], context
            )
            print("  - Response Content:")
            print(f"    {response_text}")
        print("-" * 50)

if __name__ == "__main__":
    run_test_scenarios()
