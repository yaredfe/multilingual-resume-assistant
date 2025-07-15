"""
Translation service for multilingual resume processing.

This module provides language detection and text translation capabilities
using pre-trained machine learning models. It supports multiple languages
and provides robust error handling for production use.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import glob

from tqdm import tqdm
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect, LangDetectException

from ..core.exceptions import LanguageDetectionError, ModelLoadingError
from ..core.config import config

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for detecting languages and translating text between languages.
    
    This class provides methods for:
    - Detecting the language of input text
    - Loading translation models for supported languages
    - Translating text from various languages to English
    - Batch processing of multiple documents
    
    Attributes:
        model_dir (str): Directory containing translation models
        supported_languages (Dict[str, str]): Mapping of language codes to model paths
        loaded_models (Dict[str, Tuple[MarianMTModel, MarianTokenizer]]): Cache of loaded models
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the translation service.
        
        Args:
            model_dir (str, optional): Directory containing translation models.
                Defaults to the configured model directory.
        
        Raises:
            ModelLoadingError: If the model directory doesn't exist or is invalid
        """
        self.model_dir = Path(model_dir or config.model.translation_models_dir)
        
        if not self.model_dir.exists():
            raise ModelLoadingError(
                f"Model directory does not exist: {self.model_dir}",
                model_path=str(self.model_dir)
            )
        
        # Define supported languages and their corresponding model paths
        self.supported_languages = {
            "fr": str(self.model_dir / "opus-mt-fr-en"),
            "es": str(self.model_dir / "opus-mt-es-en"),
            "de": str(self.model_dir / "opus-mt-de-en"),
        }
        
        # Cache for loaded models to avoid reloading
        self.loaded_models: Dict[str, Tuple[MarianMTModel, MarianTokenizer]] = {}
        
        logger.info(f"Translation service initialized with model directory: {self.model_dir}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        This method uses the langdetect library to identify the language
        of the provided text. It handles various edge cases and provides
        meaningful error messages.
        
        Args:
            text (str): The text to analyze for language detection
            
        Returns:
            str: ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de')
            
        Raises:
            LanguageDetectionError: If language detection fails
            ValueError: If input text is empty or invalid
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        # Clean and prepare text for detection
        cleaned_text = self._preprocess_text_for_detection(text)
        
        if len(cleaned_text.strip()) < 10:
            raise LanguageDetectionError(
                "Text too short for reliable language detection",
                text_sample=text[:100] + "..." if len(text) > 100 else text
            )
        
        try:
            detected_lang = detect(cleaned_text)
            logger.debug(f"Detected language: {detected_lang} for text sample: {text[:50]}...")
            return detected_lang
            
        except LangDetectException as e:
            raise LanguageDetectionError(
                f"Language detection failed: {str(e)}",
                text_sample=text[:100] + "..." if len(text) > 100 else text
            )
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            raise LanguageDetectionError(
                f"Unexpected error during language detection: {str(e)}",
                text_sample=text[:100] + "..." if len(text) > 100 else text
            )
    
    def _preprocess_text_for_detection(self, text: str) -> str:
        """
        Preprocess text to improve language detection accuracy.
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Preprocessed text suitable for language detection
        """
        # Remove excessive whitespace and normalize
        cleaned = " ".join(text.split())
        
        # Remove common non-language specific patterns
        import re
        # Remove email addresses
        cleaned = re.sub(r'\S+@\S+', '', cleaned)
        # Remove URLs
        cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
        # Remove phone numbers
        cleaned = re.sub(r'[\+]?[1-9][\d]{0,15}', '', cleaned)
        
        return cleaned
    
    def load_model(self, language_code: str) -> Tuple[MarianMTModel, MarianTokenizer]:
        """
        Load translation model and tokenizer for a specific language.
        
        This method loads the MarianMT model and tokenizer for the specified
        language. Models are cached to avoid repeated loading.
        
        Args:
            language_code (str): ISO 639-1 language code (e.g., 'fr', 'es', 'de')
            
        Returns:
            Tuple[MarianMTModel, MarianTokenizer]: Model and tokenizer for the language
            
        Raises:
            ModelLoadingError: If the model for the language is not found or fails to load
            ValueError: If the language code is not supported
        """
        if language_code not in self.supported_languages:
            raise ValueError(f"Unsupported language code: {language_code}. "
                           f"Supported languages: {list(self.supported_languages.keys())}")
        
        # Return cached model if already loaded
        if language_code in self.loaded_models:
            logger.debug(f"Using cached model for language: {language_code}")
            return self.loaded_models[language_code]
        
        model_path = self.supported_languages[language_code]
        
        if not Path(model_path).exists():
            raise ModelLoadingError(
                f"Translation model not found for language: {language_code}",
                model_name=f"opus-mt-{language_code}-en",
                model_path=model_path
            )
        
        try:
            logger.info(f"Loading translation model for language: {language_code}")
            tokenizer = MarianTokenizer.from_pretrained(model_path)
            model = MarianMTModel.from_pretrained(model_path)
            
            # Cache the loaded model
            self.loaded_models[language_code] = (model, tokenizer)
            
            logger.info(f"Successfully loaded translation model for {language_code}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load translation model for {language_code}: {e}")
            raise ModelLoadingError(
                f"Failed to load translation model for {language_code}: {str(e)}",
                model_name=f"opus-mt-{language_code}-en",
                model_path=model_path
            )
    
    def translate_text(self, text: str, source_language: Optional[str] = None) -> Tuple[str, str]:
        """
        Translate text from the source language to English.
        
        This method automatically detects the language if not provided and
        translates the text to English using the appropriate model.
        
        Args:
            text (str): Text to translate
            source_language (str, optional): Source language code. If None, will be detected.
            
        Returns:
            Tuple[str, str]: (translated_text, detected_language)
            
        Raises:
            LanguageDetectionError: If language detection fails
            ModelLoadingError: If translation model fails to load
            ValueError: If input text is invalid or language is not supported
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        # Detect language if not provided
        if source_language is None:
            source_language = self.detect_language(text)
        
        # Check if language is supported
        if source_language not in self.supported_languages:
            logger.warning(f"Language {source_language} not supported for translation. "
                         f"Returning original text.")
            return text, source_language
        
        try:
            # Load model and tokenizer
            model, tokenizer = self.load_model(source_language)
            
            # Prepare text for translation
            batch = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")
            
            # Generate translation
            with torch.no_grad():
                generated = model.generate(**batch)
                translated = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
            
            logger.debug(f"Translated text from {source_language} to English")
            return translated, source_language
            
        except Exception as e:
            logger.error(f"Translation failed for language {source_language}: {e}")
            # Return original text if translation fails
            return text, source_language
    
    def batch_translate(self, texts: List[str], source_languages: Optional[List[str]] = None) -> List[Tuple[str, str]]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts (List[str]): List of texts to translate
            source_languages (List[str], optional): List of source language codes.
                If None, languages will be detected automatically.
                
        Returns:
            List[Tuple[str, str]]: List of (translated_text, detected_language) tuples
        """
        if not texts:
            return []
        
        results = []
        
        # Detect languages if not provided
        if source_languages is None:
            source_languages = [self.detect_language(text) for text in texts]
        
        # Process each text
        for text, lang in tqdm(zip(texts, source_languages), 
                             total=len(texts), 
                             desc="Translating texts"):
            try:
                translated, detected_lang = self.translate_text(text, lang)
                results.append((translated, detected_lang))
            except Exception as e:
                logger.error(f"Failed to translate text: {e}")
                results.append((text, lang))  # Return original text on error
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List[str]: List of supported ISO 639-1 language codes
        """
        return list(self.supported_languages.keys())
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported for translation.
        
        Args:
            language_code (str): ISO 639-1 language code
            
        Returns:
            bool: True if language is supported, False otherwise
        """
        return language_code in self.supported_languages


# Import torch here to avoid circular imports
import torch


# Global translation service instance
translation_service = TranslationService() 