"""
Resume parsing service for extracting structured information from resumes.

This module provides comprehensive resume parsing capabilities including
extraction of personal information, education, experience, skills, and
other relevant data from various resume formats.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import spacy
from datetime import datetime

from ..core.exceptions import ResumeProcessingError, DataValidationError
from ..core.config import config
from .translation import translation_service

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Service for parsing and extracting structured information from resumes.
    
    This class provides methods for:
    - Loading and preprocessing resume text
    - Extracting personal information (name, email, phone, etc.)
    - Extracting education history
    - Extracting work experience
    - Extracting skills and competencies
    - Handling multilingual resumes
    - Validating extracted data
    
    Attributes:
        nlp: spaCy NLP model for text processing
        confidence_threshold: Minimum confidence score for extracted entities
    """
    
    def __init__(self, spacy_model: Optional[str] = None, confidence_threshold: Optional[float] = None):
        """
        Initialize the resume parser.
        
        Args:
            spacy_model (str, optional): spaCy model to use for NLP processing.
                Defaults to the configured model.
            confidence_threshold (float, optional): Minimum confidence score for extracted entities.
                Defaults to the configured threshold.
        
        Raises:
            ModelLoadingError: If the spaCy model fails to load
        """
        self.confidence_threshold = confidence_threshold or config.processing.confidence_threshold
        
        try:
            model_name = spacy_model or config.model.spacy_model
            logger.info(f"Loading spaCy model: {model_name}")
            self.nlp = spacy.load(model_name)
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise ModelLoadingError(
                f"Failed to load spaCy model {model_name}: {str(e)}",
                model_name=model_name
            )
    
    def parse_resume(self, text: str, resume_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a resume and extract structured information.
        
        This method performs comprehensive parsing of resume text, including
        language detection, translation if needed, and extraction of all
        relevant information fields.
        
        Args:
            text (str): Raw resume text to parse
            resume_id (str, optional): Unique identifier for the resume
            
        Returns:
            Dict[str, Any]: Structured resume data containing all extracted information
            
        Raises:
            ResumeProcessingError: If parsing fails
            ValueError: If input text is invalid
        """
        if not text or not isinstance(text, str):
            raise ValueError("Resume text must be a non-empty string")
        
        if len(text.strip()) < config.processing.min_text_length:
            raise ResumeProcessingError(
                f"Resume text too short (minimum {config.processing.min_text_length} characters)",
                resume_id=resume_id,
                details={"text_length": len(text)}
            )
        
        try:
            logger.info(f"Starting resume parsing for ID: {resume_id}")
            
            # Detect language and translate if necessary
            language = translation_service.detect_language(text)
            if language != "en" and translation_service.is_language_supported(language):
                logger.info(f"Translating resume from {language} to English")
                translated_text, detected_lang = translation_service.translate_text(text, language)
                original_language = language
            else:
                translated_text = text
                original_language = "en"
            
            # Parse the resume
            parsed_data = {
                "resume_id": resume_id,
                "original_language": original_language,
                "parsing_timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "translated_text_length": len(translated_text),
                "extraction_confidence": 0.0
            }
            
            # Extract different sections
            if config.processing.extract_skills:
                parsed_data["skills"] = self._extract_skills(translated_text)
            
            if config.processing.extract_education:
                parsed_data["education"] = self._extract_education(translated_text)
            
            if config.processing.extract_experience:
                parsed_data["experience"] = self._extract_experience(translated_text)
            
            # Extract personal information
            parsed_data["personal_info"] = self._extract_personal_info(translated_text)
            
            # Calculate overall confidence
            parsed_data["extraction_confidence"] = self._calculate_confidence(parsed_data)
            
            logger.info(f"Resume parsing completed for ID: {resume_id}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Resume parsing failed for ID {resume_id}: {e}")
            raise ResumeProcessingError(
                f"Resume parsing failed: {str(e)}",
                resume_id=resume_id,
                details={"error_type": type(e).__name__}
            )
    
    def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """
        Extract personal information from resume text.
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            Dict[str, Any]: Extracted personal information
        """
        personal_info = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "website": None
        }
        
        # Extract email addresses
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            personal_info["email"] = emails[0]  # Take the first email found
        
        # Extract phone numbers
        phone_pattern = r'[\+]?[1-9][\d]{0,15}'
        phones = re.findall(phone_pattern, text)
        if phones:
            personal_info["phone"] = phones[0]  # Take the first phone number found
        
        # Extract LinkedIn URLs
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+'
        linkedin_urls = re.findall(linkedin_pattern, text)
        if linkedin_urls:
            personal_info["linkedin"] = linkedin_urls[0]
        
        # Extract website URLs
        website_pattern = r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        websites = re.findall(website_pattern, text)
        if websites:
            personal_info["website"] = websites[0]
        
        # Extract name using NLP
        doc = self.nlp(text[:1000])  # Analyze first 1000 characters for name
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                personal_info["name"] = ent.text.strip()
                break
        
        # Extract location
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                personal_info["location"] = ent.text.strip()
                break
        
        return personal_info
    
    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract skills and competencies from resume text.
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            List[Dict[str, Any]]: List of extracted skills with confidence scores
        """
        skills = []
        
        # Common skill keywords
        skill_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "sql", "mongodb", "postgresql", "mysql", "aws", "azure", "docker",
            "kubernetes", "git", "agile", "scrum", "machine learning", "ai",
            "data analysis", "statistics", "excel", "powerbi", "tableau",
            "html", "css", "bootstrap", "jquery", "php", "c++", "c#", ".net",
            "spring", "django", "flask", "fastapi", "express", "graphql",
            "rest api", "microservices", "ci/cd", "jenkins", "github actions"
        ]
        
        # Find skills in text
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                # Calculate confidence based on context
                confidence = self._calculate_skill_confidence(text, skill)
                if confidence >= self.confidence_threshold:
                    skills.append({
                        "skill": skill.title(),
                        "confidence": confidence,
                        "context": self._extract_skill_context(text, skill)
                    })
        
        # Sort by confidence
        skills.sort(key=lambda x: x["confidence"], reverse=True)
        
        return skills
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education history from resume text.
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            List[Dict[str, Any]]: List of education entries
        """
        education = []
        
        # Education section patterns
        education_patterns = [
            r"education",
            r"academic",
            r"degree",
            r"university",
            r"college",
            r"bachelor",
            r"master",
            r"phd",
            r"diploma"
        ]
        
        # Find education section
        lines = text.split('\n')
        in_education_section = False
        education_text = ""
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering education section
            if any(pattern in line_lower for pattern in education_patterns):
                in_education_section = True
                continue
            
            # Collect education information
            if in_education_section and line.strip():
                education_text += line + "\n"
            
            # Exit education section if we hit another major section
            if in_education_section and any(section in line_lower for section in ["experience", "work", "employment", "skills"]):
                break
        
        # Parse education entries
        if education_text:
            education = self._parse_education_entries(education_text)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from resume text.
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            List[Dict[str, Any]]: List of work experience entries
        """
        experience = []
        
        # Experience section patterns
        experience_patterns = [
            r"experience",
            r"work history",
            r"employment",
            r"professional experience",
            r"career"
        ]
        
        # Find experience section
        lines = text.split('\n')
        in_experience_section = False
        experience_text = ""
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering experience section
            if any(pattern in line_lower for pattern in experience_patterns):
                in_experience_section = True
                continue
            
            # Collect experience information
            if in_experience_section and line.strip():
                experience_text += line + "\n"
            
            # Exit experience section if we hit another major section
            if in_experience_section and any(section in line_lower for section in ["education", "skills", "projects"]):
                break
        
        # Parse experience entries
        if experience_text:
            experience = self._parse_experience_entries(experience_text)
        
        return experience
    
    def _calculate_skill_confidence(self, text: str, skill: str) -> float:
        """
        Calculate confidence score for a skill extraction.
        
        Args:
            text (str): Resume text
            skill (str): Skill keyword
            
        Returns:
            float: Confidence score between 0 and 1
        """
        # Simple confidence calculation based on context
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        if skill_lower in text_lower:
            # Check if skill is mentioned in a skills section
            if "skills" in text_lower or "competencies" in text_lower:
                return 0.9
            # Check if skill is mentioned in experience section
            elif "experience" in text_lower or "work" in text_lower:
                return 0.8
            else:
                return 0.6
        
        return 0.0
    
    def _extract_skill_context(self, text: str, skill: str) -> str:
        """
        Extract context around a skill mention.
        
        Args:
            text (str): Resume text
            skill (str): Skill keyword
            
        Returns:
            str: Context around the skill mention
        """
        import re
        
        # Find the skill in the text
        pattern = re.compile(rf'\b{re.escape(skill)}\b', re.IGNORECASE)
        match = pattern.search(text)
        
        if match:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            return text[start:end].strip()
        
        return ""
    
    def _parse_education_entries(self, education_text: str) -> List[Dict[str, Any]]:
        """
        Parse education entries from education section text.
        
        Args:
            education_text (str): Text from education section
            
        Returns:
            List[Dict[str, Any]]: Parsed education entries
        """
        entries = []
        
        # Simple parsing - split by lines and look for degree patterns
        lines = education_text.split('\n')
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree patterns
            degree_patterns = ["bachelor", "master", "phd", "associate", "diploma"]
            if any(pattern in line.lower() for pattern in degree_patterns):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {"degree": line, "institution": "", "year": ""}
            elif current_entry and not current_entry.get("institution"):
                current_entry["institution"] = line
            elif current_entry and not current_entry.get("year"):
                # Try to extract year
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    current_entry["year"] = year_match.group()
        
        if current_entry:
            entries.append(current_entry)
        
        return entries
    
    def _parse_experience_entries(self, experience_text: str) -> List[Dict[str, Any]]:
        """
        Parse work experience entries from experience section text.
        
        Args:
            experience_text (str): Text from experience section
            
        Returns:
            List[Dict[str, Any]]: Parsed experience entries
        """
        entries = []
        
        # Simple parsing - split by lines and look for job patterns
        lines = experience_text.split('\n')
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for job title patterns
            job_patterns = ["engineer", "developer", "manager", "analyst", "specialist", "consultant"]
            if any(pattern in line.lower() for pattern in job_patterns):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {"title": line, "company": "", "duration": "", "description": ""}
            elif current_entry and not current_entry.get("company"):
                current_entry["company"] = line
            elif current_entry and not current_entry.get("duration"):
                # Try to extract duration/date
                import re
                date_pattern = r'\b(19|20)\d{2}\b.*\b(19|20)\d{2}\b|\b(19|20)\d{2}\b.*present|\b(19|20)\d{2}\b.*now'
                if re.search(date_pattern, line, re.IGNORECASE):
                    current_entry["duration"] = line
            elif current_entry:
                current_entry["description"] += line + " "
        
        if current_entry:
            entries.append(current_entry)
        
        return entries
    
    def _calculate_confidence(self, parsed_data: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score for the parsing result.
        
        Args:
            parsed_data (Dict[str, Any]): Parsed resume data
            
        Returns:
            float: Overall confidence score between 0 and 1
        """
        scores = []
        
        # Personal info confidence
        personal_info = parsed_data.get("personal_info", {})
        if personal_info.get("email"):
            scores.append(0.8)
        if personal_info.get("name"):
            scores.append(0.7)
        if personal_info.get("phone"):
            scores.append(0.6)
        
        # Skills confidence
        skills = parsed_data.get("skills", [])
        if skills:
            avg_skill_confidence = sum(skill["confidence"] for skill in skills) / len(skills)
            scores.append(avg_skill_confidence * 0.8)
        
        # Education confidence
        education = parsed_data.get("education", [])
        if education:
            scores.append(0.7)
        
        # Experience confidence
        experience = parsed_data.get("experience", [])
        if experience:
            scores.append(0.7)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def validate_parsed_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Validate parsed resume data.
        
        Args:
            parsed_data (Dict[str, Any]): Parsed resume data to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            DataValidationError: If validation fails
        """
        required_fields = ["resume_id", "parsing_timestamp", "extraction_confidence"]
        
        for field in required_fields:
            if field not in parsed_data:
                raise DataValidationError(f"Missing required field: {field}")
        
        if parsed_data["extraction_confidence"] < 0 or parsed_data["extraction_confidence"] > 1:
            raise DataValidationError("Extraction confidence must be between 0 and 1")
        
        return True


# Global resume parser instance
resume_parser = ResumeParser() 