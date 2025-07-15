"""
Main FastAPI application for the Multilingual Resume Assistant.

This module provides the main application entry point with comprehensive
API endpoints, middleware, error handling, and production-ready features.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from ..core.config import config
from ..core.exceptions import (
    ResumeProcessingError, 
    LanguageDetectionError, 
    ModelLoadingError, 
    DataValidationError
)
from .routes import resume, matching, interview, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This function handles:
    - Model initialization on startup
    - Resource cleanup on shutdown
    - Health checks and validation
    """
    # Startup
    logger.info("Starting Multilingual Resume Assistant...")
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize services (models will be loaded on first use)
        logger.info("Services initialized successfully")
        
        logger.info("Multilingual Resume Assistant started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Multilingual Resume Assistant...")
    logger.info("Cleanup completed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Multilingual Resume Assistant",
        description="""
        AI-Powered Resume Analysis and Job Matching System
        
        This API provides comprehensive resume processing capabilities including:
        - Multilingual resume parsing and translation
        - Semantic job-resume matching
        - Interview question generation
        - Skills analysis and extraction
        
        Built with FastAPI, spaCy, and advanced ML models for production use.
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add middleware
    _add_middleware(app)
    
    # Add exception handlers
    _add_exception_handlers(app)
    
    # Include routers
    _include_routers(app)
    
    # Mount static files
    _mount_static_files(app)
    
    return app


def _add_middleware(app: FastAPI):
    """Add middleware to the FastAPI application."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.allowed_origins,
        allow_credentials=True,
        allow_methods=config.api.allowed_methods,
        allow_headers=config.api.allowed_headers,
    )
    
    # Trusted host middleware (for production)
    if not config.api.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your domain
        )


def _add_exception_handlers(app: FastAPI):
    """Add custom exception handlers to the FastAPI application."""
    
    @app.exception_handler(ResumeProcessingError)
    async def resume_processing_exception_handler(request: Request, exc: ResumeProcessingError):
        """Handle resume processing errors."""
        logger.error(f"Resume processing error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Resume processing failed",
                "message": exc.message,
                "resume_id": exc.resume_id,
                "details": exc.details
            }
        )
    
    @app.exception_handler(LanguageDetectionError)
    async def language_detection_exception_handler(request: Request, exc: LanguageDetectionError):
        """Handle language detection errors."""
        logger.error(f"Language detection error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Language detection failed",
                "message": exc.message,
                "text_sample": exc.text_sample
            }
        )
    
    @app.exception_handler(ModelLoadingError)
    async def model_loading_exception_handler(request: Request, exc: ModelLoadingError):
        """Handle model loading errors."""
        logger.error(f"Model loading error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Model loading failed",
                "message": exc.message,
                "model_name": exc.model_name,
                "model_path": exc.model_path
            }
        )
    
    @app.exception_handler(DataValidationError)
    async def data_validation_exception_handler(request: Request, exc: DataValidationError):
        """Handle data validation errors."""
        logger.error(f"Data validation error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Data validation failed",
                "message": exc.message,
                "field_name": exc.field_name,
                "value": str(exc.value) if exc.value is not None else None
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError):
        """Handle value errors."""
        logger.error(f"Value error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid input",
                "message": str(exc)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred" if not config.api.debug else str(exc)
            }
        )


def _include_routers(app: FastAPI):
    """Include API routers in the FastAPI application."""
    
    # Health check routes
    app.include_router(health.router, prefix="/api", tags=["Health"])
    
    # Resume processing routes
    app.include_router(resume.router, prefix="/api/resume", tags=["Resume Processing"])
    
    # Job matching routes
    app.include_router(matching.router, prefix="/api/match", tags=["Job Matching"])
    
    # Interview question routes
    app.include_router(interview.router, prefix="/api/interview", tags=["Interview Questions"])


def _mount_static_files(app: FastAPI):
    """Mount static files for the web interface."""
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("Static files mounted successfully")
    except Exception as e:
        logger.warning(f"Failed to mount static files: {e}")


# Create the application instance
app = create_app()


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint providing basic information about the API.
    
    Returns:
        Dict[str, Any]: API information and available endpoints
    """
    return {
        "message": "Welcome to Multilingual Resume Assistant API",
        "version": "1.0.0",
        "description": "AI-Powered Resume Analysis and Job Matching System",
        "documentation": "/docs",
        "health_check": "/api/health",
        "endpoints": {
            "resume_processing": "/api/resume",
            "job_matching": "/api/match",
            "interview_questions": "/api/interview"
        }
    }


@app.get("/api", include_in_schema=False)
async def api_info():
    """
    API information endpoint.
    
    Returns:
        Dict[str, Any]: Detailed API information
    """
    return {
        "name": "Multilingual Resume Assistant API",
        "version": "1.0.0",
        "description": "AI-Powered Resume Analysis and Job Matching System",
        "author": "Yared Fereja",
        "contact": {
            "email": "yared.fereja@example.com",
            "linkedin": "https://www.linkedin.com/in/yared-fereja-067872326/"
        },
        "features": [
            "Multilingual resume parsing",
            "Language detection and translation",
            "Semantic job-resume matching",
            "Interview question generation",
            "Skills analysis and extraction"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "health": "/api/health"
    }


if __name__ == "__main__":
    """Run the application directly for development."""
    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
        workers=config.api.workers,
        log_level=config.logging.level.lower()
    ) 