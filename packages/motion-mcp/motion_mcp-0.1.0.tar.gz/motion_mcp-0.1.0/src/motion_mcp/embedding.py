# -*- coding: utf-8 -*-
"""
Ali DashScope text embedding service.
Uses text-embedding-v4 model for generating 1024-dimensional vectors.
"""
import os
from typing import List, Optional

from .config import config

# Set API key before importing dashscope
os.environ["DASHSCOPE_API_KEY"] = config.DASHSCOPE_API_KEY


class EmbeddingService:
    """
    Text embedding service using Ali DashScope text-embedding-v4.
    """
    
    def __init__(self):
        self.model = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION
        self._dashscope = None
    
    def _get_dashscope(self):
        """Lazy load dashscope module."""
        if self._dashscope is None:
            try:
                from dashscope import TextEmbedding
                self._dashscope = TextEmbedding
            except ImportError:
                raise ImportError("dashscope package not installed. Run: pip install dashscope")
        return self._dashscope
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector for text (synchronous).
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (1024 dimensions) or None on error
        """
        if not text or not text.strip():
            return None
        
        if not config.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY not configured")
        
        try:
            TextEmbedding = self._get_dashscope()
            
            # Call DashScope API
            response = TextEmbedding.call(
                model=self.model,
                input=text,
                dimension=self.dimension
            )
            
            if response.status_code == 200:
                embeddings = response.output.get("embeddings", [])
                if embeddings:
                    return embeddings[0].get("embedding")
                return None
            else:
                raise RuntimeError(f"DashScope API error: {response.code} - {response.message}")
                
        except Exception as e:
            raise RuntimeError(f"Error getting embedding: {e}")


# Singleton instance
embedding_service = EmbeddingService()
