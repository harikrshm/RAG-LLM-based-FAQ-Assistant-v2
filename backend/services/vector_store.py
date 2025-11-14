"""
Vector Store Service

Service for semantic search and retrieval from ChromaDB.
"""

import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
import time

from backend.config.settings import settings
from backend.exceptions import (
    VectorStoreConnectionError,
    VectorStoreQueryError,
    VectorStoreNotInitializedError,
    EmbeddingGenerationError,
)
from backend.models.knowledge import (
    KnowledgeChunk,
    ChunkMetadata,
    RetrievalResult,
    VectorSearchQuery,
)

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service for interacting with the vector database.
    
    Handles semantic search, retrieval, and embedding generation.
    """

    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = None,
        embedding_model: str = None,
    ):
        """
        Initialize the vector store service.
        
        Args:
            persist_directory: Path to ChromaDB persistence directory
            collection_name: Name of the collection to use
            embedding_model: Name of the embedding model
        """
        self.persist_directory = persist_directory or settings.VECTORDB_PATH
        self.collection_name = collection_name or settings.VECTORDB_COLLECTION
        self.embedding_model_name = embedding_model or settings.EMBEDDING_MODEL
        
        logger.info(f"Initializing VectorStoreService with collection: {self.collection_name}")
        
        # Initialize ChromaDB client
        self._init_client()
        
        # Initialize embedding model
        self._init_embedding_model()
        
        logger.info("VectorStoreService initialized successfully")

    def _init_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False,
                ),
            )
            
            # Get the collection
            self.collection = self.client.get_collection(name=self.collection_name)
            
            # Get collection info
            count = self.collection.count()
            logger.info(f"Connected to collection '{self.collection_name}' with {count} chunks")
            
        except ValueError as e:
            # Collection doesn't exist
            logger.error(f"Collection '{self.collection_name}' not found: {e}")
            raise VectorStoreNotInitializedError(
                f"Vector store collection '{self.collection_name}' does not exist. "
                "Please run the data ingestion pipeline first.",
                details={"collection": self.collection_name, "error": str(e)}
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise VectorStoreConnectionError(
                f"Failed to connect to vector database: {str(e)}",
                details={"path": self.persist_directory, "error": str(e)}
            )

    def _init_embedding_model(self):
        """Initialize the embedding model for query encoding."""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded. Dimension: {self.embedding_dimension}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise EmbeddingGenerationError(
                f"Failed to load embedding model '{self.embedding_model_name}': {str(e)}",
                details={"model": self.embedding_model_name, "error": str(e)}
            )

    def encode_query(self, query: str) -> List[float]:
        """
        Encode a text query into a vector embedding.
        
        Args:
            query: Text query to encode
            
        Returns:
            List of floats representing the embedding
        """
        try:
            if not self.embedding_model:
                raise VectorStoreNotInitializedError(
                    "Embedding model not initialized",
                    details={"model": self.embedding_model_name}
                )
            
            embedding = self.embedding_model.encode(
                query,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embedding.tolist()
            
        except VectorStoreNotInitializedError:
            raise
        except Exception as e:
            logger.error(f"Failed to encode query: {e}")
            raise EmbeddingGenerationError(
                f"Failed to generate embedding for query: {str(e)}",
                details={"query_length": len(query), "error": str(e)}
            )

    def search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """
        Perform semantic search in the vector database.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            filters: Metadata filters (e.g., {"amc_name": "HDFC Mutual Fund"})
            
        Returns:
            RetrievalResult with chunks and scores
        """
        start_time = time.time()
        
        try:
            logger.info(f"Searching for: '{query}' (top_k={top_k})")
            
            # Encode query
            query_embedding = self.encode_query(query)
            
            # Apply similarity threshold
            threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"],
            )
            
            # Process results
            chunks = []
            similarity_scores = []
            
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    # Convert distance to similarity score (cosine distance -> similarity)
                    distance = results["distances"][0][i]
                    similarity = 1 - distance  # ChromaDB uses cosine distance
                    
                    # Apply threshold
                    if similarity < threshold:
                        logger.debug(f"Skipping chunk with similarity {similarity:.3f} < {threshold}")
                        continue
                    
                    # Extract chunk data
                    chunk_id = results["ids"][0][i]
                    content = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    
                    # Create KnowledgeChunk
                    chunk = self._create_knowledge_chunk(chunk_id, content, metadata)
                    chunks.append(chunk)
                    similarity_scores.append(similarity)
            
            # Calculate retrieval time
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Retrieved {len(chunks)} chunks (filtered from {len(results['ids'][0]) if results['ids'] else 0}) "
                f"in {retrieval_time_ms:.2f}ms"
            )
            
            return RetrievalResult(
                chunks=chunks,
                similarity_scores=similarity_scores,
                total_retrieved=len(chunks),
                query=query,
                retrieval_time_ms=retrieval_time_ms,
            )
            
        except (VectorStoreNotInitializedError, EmbeddingGenerationError):
            raise
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreQueryError(
                f"Vector store search failed: {str(e)}",
                details={"query": query[:100], "error": str(e)}
            )

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """
        Perform search using a pre-computed embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Metadata filters
            
        Returns:
            RetrievalResult with chunks and scores
        """
        start_time = time.time()
        
        try:
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"],
            )
            
            # Process results
            chunks = []
            similarity_scores = []
            
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    distance = results["distances"][0][i]
                    similarity = 1 - distance
                    
                    chunk_id = results["ids"][0][i]
                    content = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    
                    chunk = self._create_knowledge_chunk(chunk_id, content, metadata)
                    chunks.append(chunk)
                    similarity_scores.append(similarity)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return RetrievalResult(
                chunks=chunks,
                similarity_scores=similarity_scores,
                total_retrieved=len(chunks),
                query="[embedding-based query]",
                retrieval_time_ms=retrieval_time_ms,
            )
            
        except Exception as e:
            logger.error(f"Embedding-based search failed: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        """
        Retrieve a specific chunk by ID.
        
        Args:
            chunk_id: Unique chunk identifier
            
        Returns:
            KnowledgeChunk or None if not found
        """
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"],
            )
            
            if results["ids"] and len(results["ids"]) > 0:
                return self._create_knowledge_chunk(
                    chunk_id=results["ids"][0],
                    content=results["documents"][0],
                    metadata=results["metadatas"][0],
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunk {chunk_id}: {e}")
            return None

    def get_chunks_by_source(
        self,
        source_url: str,
        limit: int = 100,
    ) -> List[KnowledgeChunk]:
        """
        Retrieve all chunks from a specific source URL.
        
        Args:
            source_url: Source URL to filter by
            limit: Maximum number of chunks to return
            
        Returns:
            List of KnowledgeChunk objects
        """
        try:
            results = self.collection.get(
                where={"source_url": source_url},
                limit=limit,
                include=["documents", "metadatas"],
            )
            
            chunks = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    chunk = self._create_knowledge_chunk(
                        chunk_id=results["ids"][i],
                        content=results["documents"][i],
                        metadata=results["metadatas"][i],
                    )
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunks for source {source_url}: {e}")
            return []

    def get_chunks_by_amc(
        self,
        amc_name: str,
        limit: int = 100,
    ) -> List[KnowledgeChunk]:
        """
        Retrieve all chunks for a specific AMC.
        
        Args:
            amc_name: AMC name to filter by
            limit: Maximum number of chunks to return
            
        Returns:
            List of KnowledgeChunk objects
        """
        try:
            results = self.collection.get(
                where={"amc_name": amc_name},
                limit=limit,
                include=["documents", "metadatas"],
            )
            
            chunks = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    chunk = self._create_knowledge_chunk(
                        chunk_id=results["ids"][i],
                        content=results["documents"][i],
                        metadata=results["metadatas"][i],
                    )
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunks for AMC {amc_name}: {e}")
            return []

    def _create_knowledge_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> KnowledgeChunk:
        """
        Create a KnowledgeChunk object from ChromaDB results.
        
        Args:
            chunk_id: Chunk identifier
            content: Chunk text content
            metadata: Chunk metadata
            
        Returns:
            KnowledgeChunk object
        """
        # Extract metadata fields
        chunk_metadata = ChunkMetadata(
            source_url=metadata.get("source_url", ""),
            amc_name=metadata.get("amc_name"),
            amc_id=metadata.get("amc_id"),
            title=metadata.get("title"),
            content_type=metadata.get("content_type"),
            scraped_at=metadata.get("scraped_at"),
            structured_info={},  # TODO: Parse from metadata if stored as JSON
        )
        
        return KnowledgeChunk(
            chunk_id=chunk_id,
            content=content,
            source_url=metadata.get("source_url", ""),
            chunk_index=metadata.get("chunk_index", 0),
            metadata=chunk_metadata,
            embedding=None,  # Don't include embeddings in response by default
            groww_page_url=metadata.get("groww_page_url"),
        )

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Try to get sample to determine metadata fields
            sample = self.collection.get(limit=1, include=["metadatas"])
            metadata_fields = []
            if sample["metadatas"] and len(sample["metadatas"]) > 0:
                metadata_fields = list(sample["metadatas"][0].keys())
            
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "embedding_dimension": self.embedding_dimension,
                "embedding_model": self.embedding_model_name,
                "metadata_fields": metadata_fields,
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e),
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Check if the vector store is healthy and accessible.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Try to count documents
            count = self.collection.count()
            
            return {
                "status": "healthy",
                "collection_accessible": True,
                "document_count": count,
                "embedding_model_loaded": self.embedding_model is not None,
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Singleton instance
_vector_store_instance: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """
    Get or create the singleton VectorStoreService instance.
    
    Returns:
        VectorStoreService instance
    """
    global _vector_store_instance
    
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    
    return _vector_store_instance

