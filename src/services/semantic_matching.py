"""
Semantic matching service for job-resume compatibility analysis.

This module provides advanced semantic matching capabilities using
sentence transformers and vector similarity to match resumes with
job descriptions based on content similarity and skill alignment.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

from ..core.exceptions import ModelLoadingError, DataValidationError
from ..core.config import config

logger = logging.getLogger(__name__)


class SemanticMatchingService:
    """
    Service for semantic matching between resumes and job descriptions.
    
    This class provides methods for:
    - Building and managing vector embeddings for resumes and jobs
    - Performing semantic similarity searches
    - Calculating match scores with confidence metrics
    - Batch processing for multiple comparisons
    
    Attributes:
        embedding_model: Sentence transformer model for text embeddings
        chroma_client: ChromaDB client for vector storage
        collection: ChromaDB collection for storing embeddings
    """
    
    def __init__(self, model_name: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize the semantic matching service.
        
        Args:
            model_name (str, optional): Name of the sentence transformer model.
                Defaults to the configured model.
            db_path (str, optional): Path to ChromaDB database.
                Defaults to the configured path.
        
        Raises:
            ModelLoadingError: If the embedding model fails to load
        """
        self.model_name = model_name or config.model.sentence_transformer_model
        self.db_path = db_path or "data/chroma_db"
        
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=self.db_path)
            self.embedding_function = SentenceTransformerEmbeddingFunction(
                model_name=self.model_name
            )
            
            # Get or create collection
            self.collection = self._get_or_create_collection()
            
            logger.info("Semantic matching service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic matching service: {e}")
            raise ModelLoadingError(
                f"Failed to initialize semantic matching service: {str(e)}",
                model_name=self.model_name
            )
    
    def _get_or_create_collection(self, collection_name: str = "resumes") -> chromadb.Collection:
        """
        Get existing collection or create a new one.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            chromadb.Collection: ChromaDB collection
        """
        try:
            # Try to get existing collection
            collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Using existing collection: {collection_name}")
            return collection
        except Exception:
            # Create new collection if it doesn't exist
            logger.info(f"Creating new collection: {collection_name}")
            return self.chroma_client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
    
    def add_resume_embedding(self, resume_id: str, resume_text: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a resume embedding to the vector database.
        
        Args:
            resume_id (str): Unique identifier for the resume
            resume_text (str): Text content of the resume
            metadata (Dict, optional): Additional metadata for the resume
            
        Returns:
            bool: True if successfully added
            
        Raises:
            ValueError: If inputs are invalid
            DataValidationError: If data validation fails
        """
        if not resume_id or not isinstance(resume_id, str):
            raise ValueError("Resume ID must be a non-empty string")
        
        if not resume_text or not isinstance(resume_text, str):
            raise ValueError("Resume text must be a non-empty string")
        
        if len(resume_text.strip()) < config.processing.min_text_length:
            raise DataValidationError(
                f"Resume text too short (minimum {config.processing.min_text_length} characters)",
                field_name="resume_text",
                value=len(resume_text)
            )
        
        try:
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "type": "resume",
                "text_length": len(resume_text),
                "timestamp": str(np.datetime64('now'))
            })
            
            # Add to collection
            self.collection.add(
                documents=[resume_text],
                metadatas=[metadata],
                ids=[resume_id]
            )
            
            logger.info(f"Added resume embedding for ID: {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add resume embedding for ID {resume_id}: {e}")
            return False
    
    def add_job_embedding(self, job_id: str, job_description: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a job description embedding to the vector database.
        
        Args:
            job_id (str): Unique identifier for the job
            job_description (str): Text content of the job description
            metadata (Dict, optional): Additional metadata for the job
            
        Returns:
            bool: True if successfully added
            
        Raises:
            ValueError: If inputs are invalid
            DataValidationError: If data validation fails
        """
        if not job_id or not isinstance(job_id, str):
            raise ValueError("Job ID must be a non-empty string")
        
        if not job_description or not isinstance(job_description, str):
            raise ValueError("Job description must be a non-empty string")
        
        if len(job_description.strip()) < config.processing.min_text_length:
            raise DataValidationError(
                f"Job description too short (minimum {config.processing.min_text_length} characters)",
                field_name="job_description",
                value=len(job_description)
            )
        
        try:
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "type": "job",
                "text_length": len(job_description),
                "timestamp": str(np.datetime64('now'))
            })
            
            # Add to collection
            self.collection.add(
                documents=[job_description],
                metadatas=[metadata],
                ids=[job_id]
            )
            
            logger.info(f"Added job embedding for ID: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job embedding for ID {job_id}: {e}")
            return False
    
    def find_matching_resumes(self, job_description: str, top_k: int = 10, 
                            min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Find resumes that match a job description.
        
        Args:
            job_description (str): Job description text
            top_k (int): Number of top matches to return
            min_score (float): Minimum similarity score threshold
            
        Returns:
            List[Dict[str, Any]]: List of matching resumes with scores and metadata
        """
        if not job_description or not isinstance(job_description, str):
            raise ValueError("Job description must be a non-empty string")
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[job_description],
                n_results=top_k,
                where={"type": "resume"}
            )
            
            matches = []
            if results['ids'] and results['ids'][0]:
                for i, (resume_id, distance, metadata) in enumerate(zip(
                    results['ids'][0], 
                    results['distances'][0], 
                    results['metadatas'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1 - distance
                    
                    if similarity_score >= min_score:
                        matches.append({
                            "resume_id": resume_id,
                            "similarity_score": round(similarity_score, 4),
                            "metadata": metadata,
                            "rank": i + 1
                        })
            
            logger.info(f"Found {len(matches)} matching resumes for job description")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to find matching resumes: {e}")
            return []
    
    def find_matching_jobs(self, resume_text: str, top_k: int = 10, 
                          min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Find jobs that match a resume.
        
        Args:
            resume_text (str): Resume text
            top_k (int): Number of top matches to return
            min_score (float): Minimum similarity score threshold
            
        Returns:
            List[Dict[str, Any]]: List of matching jobs with scores and metadata
        """
        if not resume_text or not isinstance(resume_text, str):
            raise ValueError("Resume text must be a non-empty string")
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[resume_text],
                n_results=top_k,
                where={"type": "job"}
            )
            
            matches = []
            if results['ids'] and results['ids'][0]:
                for i, (job_id, distance, metadata) in enumerate(zip(
                    results['ids'][0], 
                    results['distances'][0], 
                    results['metadatas'][0]
                )):
                    # Convert distance to similarity score
                    similarity_score = 1 - distance
                    
                    if similarity_score >= min_score:
                        matches.append({
                            "job_id": job_id,
                            "similarity_score": round(similarity_score, 4),
                            "metadata": metadata,
                            "rank": i + 1
                        })
            
            logger.info(f"Found {len(matches)} matching jobs for resume")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to find matching jobs: {e}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Generate embeddings
            embedding1 = self.embedding_model.encode([text1])
            embedding2 = self.embedding_model.encode([text2])
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1[0], embedding2[0]) / (
                np.linalg.norm(embedding1[0]) * np.linalg.norm(embedding2[0])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def batch_similarity_search(self, query_texts: List[str], 
                              document_type: str = "resume",
                              top_k: int = 5) -> List[List[Dict[str, Any]]]:
        """
        Perform batch similarity search for multiple query texts.
        
        Args:
            query_texts (List[str]): List of query texts
            document_type (str): Type of documents to search ("resume" or "job")
            top_k (int): Number of top matches per query
            
        Returns:
            List[List[Dict[str, Any]]]: List of matches for each query
        """
        if not query_texts:
            return []
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=query_texts,
                n_results=top_k,
                where={"type": document_type}
            )
            
            all_matches = []
            for query_idx in range(len(query_texts)):
                query_matches = []
                if results['ids'] and results['ids'][query_idx]:
                    for i, (doc_id, distance, metadata) in enumerate(zip(
                        results['ids'][query_idx],
                        results['distances'][query_idx],
                        results['metadatas'][query_idx]
                    )):
                        similarity_score = 1 - distance
                        query_matches.append({
                            "document_id": doc_id,
                            "similarity_score": round(similarity_score, 4),
                            "metadata": metadata,
                            "rank": i + 1
                        })
                all_matches.append(query_matches)
            
            logger.info(f"Completed batch similarity search for {len(query_texts)} queries")
            return all_matches
            
        except Exception as e:
            logger.error(f"Failed to perform batch similarity search: {e}")
            return [[] for _ in query_texts]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample documents to analyze
            sample_results = self.collection.get(limit=100)
            
            stats = {
                "total_documents": count,
                "resume_count": 0,
                "job_count": 0,
                "average_text_length": 0,
                "model_name": self.model_name
            }
            
            if sample_results['metadatas']:
                resume_count = sum(1 for meta in sample_results['metadatas'] 
                                 if meta.get('type') == 'resume')
                job_count = sum(1 for meta in sample_results['metadatas'] 
                              if meta.get('type') == 'job')
                
                avg_length = np.mean([meta.get('text_length', 0) 
                                    for meta in sample_results['metadatas']])
                
                stats.update({
                    "resume_count": resume_count,
                    "job_count": job_count,
                    "average_text_length": int(avg_length)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            bool: True if successfully cleared
        """
        try:
            self.collection.delete(where={})
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False


# Global semantic matching service instance
semantic_matching_service = SemanticMatchingService() 