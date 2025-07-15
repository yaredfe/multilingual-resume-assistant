"""
Configuration management for the Multilingual Resume Assistant.

This module provides centralized configuration management with environment
variable support, validation, and type safety for all application settings.
"""

import os
from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
import logging


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    host: str = "localhost"
    port: int = 5432
    name: str = "resume_assistant"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    
    @property
    def connection_string(self) -> str:
        """Generate database connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class ModelConfig:
    """Machine learning model configuration."""
    
    # Translation models
    translation_models_dir: str = "models"
    supported_languages: List[str] = field(default_factory=lambda: ["en", "es", "fr", "de"])
    
    # NLP models
    spacy_model: str = "en_core_web_sm"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    
    # Model loading settings
    device: str = "cpu"  # "cpu" or "cuda"
    max_length: int = 512
    batch_size: int = 32
    
    def get_model_path(self, language: str) -> str:
        """Get the path for a specific language model."""
        model_mapping = {
            "fr": "opus-mt-fr-en",
            "es": "opus-mt-es-en", 
            "de": "opus-mt-de-en"
        }
        model_name = model_mapping.get(language)
        if not model_name:
            raise ValueError(f"Unsupported language: {language}")
        return str(Path(self.translation_models_dir) / model_name)


@dataclass
class ProcessingConfig:
    """Resume processing configuration."""
    
    # File processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: List[str] = field(default_factory=lambda: [".pdf", ".txt", ".docx"])
    
    # Text processing
    min_text_length: int = 50
    max_text_length: int = 50000
    
    # Parsing settings
    confidence_threshold: float = 0.7
    extract_skills: bool = True
    extract_education: bool = True
    extract_experience: bool = True


@dataclass
class APIConfig:
    """API configuration settings."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    
    # CORS settings
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class Config:
    """
    Main configuration class for the Multilingual Resume Assistant.
    
    This class manages all configuration settings with environment variable
    support and validation. It provides a centralized way to access all
    application settings.
    """
    
    def __init__(self):
        """Initialize configuration with environment variable overrides."""
        self.database = self._load_database_config()
        self.model = self._load_model_config()
        self.processing = self._load_processing_config()
        self.api = self._load_api_config()
        self.logging = self._load_logging_config()
        
        # Set up logging
        self._setup_logging()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment variables."""
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "resume_assistant"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20"))
        )
    
    def _load_model_config(self) -> ModelConfig:
        """Load model configuration from environment variables."""
        return ModelConfig(
            translation_models_dir=os.getenv("MODEL_DIR", "models"),
            spacy_model=os.getenv("SPACY_MODEL", "en_core_web_sm"),
            sentence_transformer_model=os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2"),
            device=os.getenv("MODEL_DEVICE", "cpu"),
            max_length=int(os.getenv("MODEL_MAX_LENGTH", "512")),
            batch_size=int(os.getenv("MODEL_BATCH_SIZE", "32"))
        )
    
    def _load_processing_config(self) -> ProcessingConfig:
        """Load processing configuration from environment variables."""
        return ProcessingConfig(
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            min_text_length=int(os.getenv("MIN_TEXT_LENGTH", "50")),
            max_text_length=int(os.getenv("MAX_TEXT_LENGTH", "50000")),
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment variables."""
        return APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            workers=int(os.getenv("WORKERS", "1")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
            rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment variables."""
        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
    
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.logging.level),
            format=self.logging.format,
            handlers=self._get_log_handlers()
        )
    
    def _get_log_handlers(self) -> List[logging.Handler]:
        """Get logging handlers based on configuration."""
        handlers = [logging.StreamHandler()]
        
        if self.logging.file_path:
            from logging.handlers import RotatingFileHandler
            handlers.append(
                RotatingFileHandler(
                    self.logging.file_path,
                    maxBytes=self.logging.max_file_size,
                    backupCount=self.logging.backup_count
                )
            )
        
        return handlers
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            bool: True if configuration is valid, raises exception otherwise
        """
        # Validate database configuration
        if not self.database.host:
            raise ValueError("Database host cannot be empty")
        
        # Validate model configuration
        if not Path(self.model.translation_models_dir).exists():
            raise ValueError(f"Model directory does not exist: {self.model.translation_models_dir}")
        
        # Validate processing configuration
        if self.processing.confidence_threshold < 0 or self.processing.confidence_threshold > 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        
        # Validate API configuration
        if self.api.port < 1 or self.api.port > 65535:
            raise ValueError("API port must be between 1 and 65535")
        
        return True


# Global configuration instance
config = Config() 