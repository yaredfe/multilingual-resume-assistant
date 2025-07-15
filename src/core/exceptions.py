"""
Custom exceptions for the Multilingual Resume Assistant.

This module defines application-specific exceptions that provide
clear error messages and help with debugging.
"""


class ResumeProcessingError(Exception):
    """
    Raised when there's an error processing a resume.
    
    This exception is used when resume parsing, analysis, or
    processing fails due to invalid data or processing errors.
    """
    
    def __init__(self, message: str, resume_id: str = None, details: dict = None):
        """
        Initialize the ResumeProcessingError.
        
        Args:
            message (str): Human-readable error message
            resume_id (str, optional): ID of the resume that caused the error
            details (dict, optional): Additional error details for debugging
        """
        self.message = message
        self.resume_id = resume_id
        self.details = details or {}
        super().__init__(self.message)


class LanguageDetectionError(Exception):
    """
    Raised when language detection fails.
    
    This exception is used when the system cannot determine
    the language of a text document.
    """
    
    def __init__(self, message: str, text_sample: str = None):
        """
        Initialize the LanguageDetectionError.
        
        Args:
            message (str): Human-readable error message
            text_sample (str, optional): Sample of the text that failed detection
        """
        self.message = message
        self.text_sample = text_sample
        super().__init__(self.message)


class ModelLoadingError(Exception):
    """
    Raised when ML models fail to load.
    
    This exception is used when translation models, NLP models,
    or other ML components fail to initialize.
    """
    
    def __init__(self, message: str, model_name: str = None, model_path: str = None):
        """
        Initialize the ModelLoadingError.
        
        Args:
            message (str): Human-readable error message
            model_name (str, optional): Name of the model that failed to load
            model_path (str, optional): Path where the model was expected
        """
        self.message = message
        self.model_name = model_name
        self.model_path = model_path
        super().__init__(self.message)


class DataValidationError(Exception):
    """
    Raised when data validation fails.
    
    This exception is used when input data doesn't meet
    the expected format or validation requirements.
    """
    
    def __init__(self, message: str, field_name: str = None, value: any = None):
        """
        Initialize the DataValidationError.
        
        Args:
            message (str): Human-readable error message
            field_name (str, optional): Name of the field that failed validation
            value (any, optional): The value that failed validation
        """
        self.message = message
        self.field_name = field_name
        self.value = value
        super().__init__(self.message) 