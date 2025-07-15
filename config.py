"""
Configuration file for Multilingual Resume Screener & Interview Assistant
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SCRIPTS_DIR = BASE_DIR / "Scripts"

# Data directories
RESUMES_DIR = DATA_DIR / "resumes"
TRANSLATED_DIR = DATA_DIR / "translated"
PARSED_DIR = DATA_DIR / "parsed"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
JOB_DESCRIPTIONS_DIR = DATA_DIR / "job_descriptions"
MATCH_RESULTS_DIR = DATA_DIR / "match_results"
INTERVIEW_QUESTIONS_DIR = DATA_DIR / "interview_questions"

# Model paths
SENTENCE_TRANSFORMER_MODEL = MODELS_DIR / "sentence-transformers" / "all-MiniLM-L6-v2"
FLAN_T5_MODEL = MODELS_DIR / "flan-t5-base"

# Translation models
TRANSLATION_MODELS = {
    "fr": MODELS_DIR / "opus-mt-fr-en",
    "es": MODELS_DIR / "opus-mt-es-en", 
    "de": MODELS_DIR / "opus-mt-de-en"
}

# ChromaDB settings
CHROMA_COLLECTION_NAME = "resume_collection"

# Semantic matching settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Processing settings
MAX_RESUME_LENGTH = 10000  # characters
MAX_QUESTION_LENGTH = 1000  # characters
BATCH_SIZE = 10

# Web application settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes")

# Supported languages
SUPPORTED_LANGUAGES = ["en", "fr", "es", "de"]

# File extensions
RESUME_EXTENSIONS = [".txt", ".pdf", ".doc", ".docx"]
CSV_EXTENSIONS = [".csv"]
JSON_EXTENSIONS = [".json"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API settings
API_TITLE = "Multilingual Resume Screener & Interview Assistant"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
An AI-powered resume screening and interview question generation system that supports multiple languages.

## Features

* **Multilingual Support**: Automatically detect and translate resumes from French, German, Spanish, and English
* **Smart Semantic Matching**: AI-powered matching using sentence transformers
* **Interview Question Generation**: Generate personalized interview questions
* **Web Interface**: Modern, responsive web interface
* **Real-time Processing**: Upload and process new resumes on-the-fly

## Endpoints

* `POST /api/match-candidates` - Find matching candidates for a job description
* `POST /api/upload-resume` - Upload and process a new resume
* `GET /api/health` - Health check endpoint
"""

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/app.db")

# Email settings (for future use)
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Cache settings
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 1000

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["text/plain", "application/pdf", "application/msword", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Model settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "flan-t5-base"
TRANSLATION_MODEL_PREFIX = "opus-mt"

# Processing pipeline settings
ENABLE_TRANSLATION = True
ENABLE_PARSING = True
ENABLE_EMBEDDING = True
ENABLE_MATCHING = True
ENABLE_QUESTION_GENERATION = True

# Quality settings
MIN_RESUME_LENGTH = 100  # characters
MIN_JOB_DESCRIPTION_LENGTH = 50  # characters
MAX_QUESTIONS_PER_CANDIDATE = 5

# Export settings
EXPORT_FORMATS = ["json", "csv", "pdf"]
DEFAULT_EXPORT_FORMAT = "json"

# Monitoring settings
ENABLE_METRICS = True
METRICS_PORT = 9090

# Backup settings
BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 24
BACKUP_RETENTION_DAYS = 7

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        RESUMES_DIR,
        TRANSLATED_DIR,
        PARSED_DIR,
        CHROMA_DB_DIR,
        JOB_DESCRIPTIONS_DIR,
        MATCH_RESULTS_DIR,
        INTERVIEW_QUESTIONS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_model_path(model_name):
    """Get the full path for a model"""
    return MODELS_DIR / model_name

def is_supported_language(lang_code):
    """Check if a language is supported"""
    return lang_code in SUPPORTED_LANGUAGES

def get_translation_model(lang_code):
    """Get the translation model path for a language"""
    return TRANSLATION_MODELS.get(lang_code)

# Initialize directories on import
ensure_directories() 