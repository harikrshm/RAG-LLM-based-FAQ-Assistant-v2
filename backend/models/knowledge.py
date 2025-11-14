"""
Knowledge Base Models

Pydantic models for knowledge base chunks and retrieval.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChunkMetadata(BaseModel):
    """
    Model for chunk metadata.
    
    Represents metadata associated with a knowledge base chunk.
    """
    source_url: str = Field(..., description="Original source URL")
    amc_name: Optional[str] = Field(None, description="AMC name")
    amc_id: Optional[str] = Field(None, description="AMC identifier")
    title: Optional[str] = Field(None, description="Document title")
    content_type: Optional[str] = Field(None, description="Content type classification")
    scraped_at: Optional[str] = Field(None, description="Scraping timestamp")
    structured_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Extracted structured information"
    )


class KnowledgeChunk(BaseModel):
    """
    Model for a knowledge base chunk.
    
    Represents a single chunk of information from the knowledge base.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk text content")
    source_url: str = Field(..., description="Source URL")
    chunk_index: int = Field(..., ge=0, description="Index within source document")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    groww_page_url: Optional[str] = Field(
        None,
        description="Mapped Groww page URL if available"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "hdfc-equity-chunk-1",
                "content": "HDFC Equity Fund has an expense ratio of 1.05%...",
                "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                "chunk_index": 0,
                "metadata": {
                    "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                    "amc_name": "HDFC Mutual Fund",
                    "amc_id": "hdfc",
                    "title": "HDFC Equity Fund",
                    "content_type": "fund_page"
                },
                "groww_page_url": "https://groww.in/mutual-funds/hdfc-equity-fund"
            }
        }


class RetrievalResult(BaseModel):
    """
    Model for retrieval results.
    
    Represents the results of a vector search query.
    """
    chunks: List[KnowledgeChunk] = Field(..., description="Retrieved chunks")
    similarity_scores: List[float] = Field(
        ...,
        description="Similarity scores for each chunk"
    )
    total_retrieved: int = Field(..., ge=0, description="Total number of chunks retrieved")
    query: str = Field(..., description="Original query")
    retrieval_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Retrieval time in milliseconds"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {
                        "chunk_id": "hdfc-equity-chunk-1",
                        "content": "HDFC Equity Fund has an expense ratio of 1.05%...",
                        "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                        "chunk_index": 0,
                        "metadata": {
                            "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                            "amc_name": "HDFC Mutual Fund"
                        }
                    }
                ],
                "similarity_scores": [0.95, 0.89, 0.85],
                "total_retrieved": 3,
                "query": "What is the expense ratio?",
                "retrieval_time_ms": 45.2
            }
        }


class VectorSearchQuery(BaseModel):
    """
    Model for vector search query.
    
    Represents a query to the vector database.
    """
    query_text: str = Field(..., description="Query text to search for")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    similarity_threshold: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata filters (e.g., amc_name)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "What is the expense ratio of HDFC Equity Fund?",
                "top_k": 5,
                "similarity_threshold": 0.7,
                "filters": {
                    "amc_name": "HDFC Mutual Fund"
                }
            }
        }

