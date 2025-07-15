"""
Core functionality for the Multilingual Resume Assistant.

This module contains the fundamental components for resume processing,
language detection, and data management.
"""

from .config import Config
from .exceptions import ResumeProcessingError, LanguageDetectionError

__all__ = ['Config', 'ResumeProcessingError', 'LanguageDetectionError'] 