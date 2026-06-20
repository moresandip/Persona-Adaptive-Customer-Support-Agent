import os
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# API Keys & DB Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
CHROMA_DB_DIR = os.environ.get("CHROMA_DB_DIR", "./chroma_db")

# Model Definitions
EMBEDDING_MODEL = "gemini-embedding-2"
GENERATION_MODEL = "gemini-2.5-flash"
CLASSIFICATION_MODEL = "gemini-2.5-flash"

# Escalation Rules & Thresholds
CONFIDENCE_THRESHOLD = 0.45

# Topics that trigger immediate human escalation
SENSITIVE_TOPICS = [
    "refund",
    "billing dispute",
    "double charge",
    "overcharge",
    "hack",
    "compromised",
    "data breach",
    "unauthorized access",
    "cancel account",
    "close account",
    "delete my account",
    "sue",
    "legal",
    "lawyer",
    "compliance"
]
