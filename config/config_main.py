"""
Configuration file for CloudDesk
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "clouddesk.db")
DATABASE_PATH = os.getenv("DATABASE_PATH", "./")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
API_DEBUG = os.getenv("API_DEBUG", "False") == "True"

# RAG Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "clouddesk")

# Cache Configuration
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 86400))  # 24 hours
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True") == "True"

# Escalation Configuration
ESCALATION_CONFIDENCE_THRESHOLD = float(os.getenv("ESCALATION_CONFIDENCE_THRESHOLD", 0.6))
AUTO_ESCALATION_ENABLED = os.getenv("AUTO_ESCALATION_ENABLED", "True") == "True"

# Learning Configuration
LEARNING_ENABLED = os.getenv("LEARNING_ENABLED", "True") == "True"
LEARNING_CONFIDENCE_THRESHOLD = float(os.getenv("LEARNING_CONFIDENCE_THRESHOLD", 0.7))

# Notification Configuration
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "True") == "True"
NOTIFICATION_CHANNELS = os.getenv("NOTIFICATION_CHANNELS", "in_app,email").split(",")

# Audit Configuration
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "True") == "True"
AUDIT_LOG_RETENTION_DAYS = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", 365))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "clouddesk.log")
