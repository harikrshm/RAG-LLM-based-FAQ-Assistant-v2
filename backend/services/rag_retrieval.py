"""
RAG Retrieval Pipeline

Orchestrates the retrieval process for the RAG system.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
import time

from backend.config.settings import settings
from backend.models.knowledge import (
    KnowledgeChunk,
    RetrievalResult,
)
from backend.services.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGRetrievalPipeline:
    """
    Pipeline for retrieving relevant knowledge chunks based on user queries.
    
    Handles query preprocessing, vector search, re-ranking, and result formatting.
    """

    def __init__(
        self,
        top_k: int = None,
        similarity_threshold: float = None,
    ):
        """
        Initialize the RAG retrieval pipeline.
        
        Args:
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.top_k = top_k or settings.RAG_TOP_K
        self.similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
        
        # Initialize vector store
        self.vector_store = get_vector_store()
        
        logger.info(
            f"RAG Retrieval Pipeline initialized (top_k={self.top_k}, "
            f"threshold={self.similarity_threshold})"
        )

    def retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> RetrievalResult:
        """
        Retrieve relevant knowledge chunks for a query.
        
        Args:
            query: User query text
            filters: Optional metadata filters (e.g., {"amc_name": "HDFC Mutual Fund"})
            top_k: Override default top_k
            similarity_threshold: Override default threshold
            
        Returns:
            RetrievalResult with retrieved chunks
        """
        start_time = time.time()
        
        try:
            # Preprocess query
            processed_query = self._preprocess_query(query)
            logger.info(f"Retrieving chunks for query: '{processed_query}'")
            
            # Use overrides or defaults
            k = top_k or self.top_k
            threshold = similarity_threshold or self.similarity_threshold
            
            # Perform vector search
            retrieval_result = self.vector_store.search(
                query=processed_query,
                top_k=k * 2,  # Retrieve more for re-ranking
                similarity_threshold=threshold * 0.8,  # Lower threshold before re-ranking
                filters=filters,
            )
            
            # Re-rank results
            reranked_chunks, reranked_scores = self._rerank_results(
                query=processed_query,
                chunks=retrieval_result.chunks,
                scores=retrieval_result.similarity_scores,
                top_k=k,
            )
            
            # Apply final threshold
            filtered_chunks, filtered_scores = self._apply_threshold(
                chunks=reranked_chunks,
                scores=reranked_scores,
                threshold=threshold,
            )
            
            # Calculate total time
            total_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Retrieved {len(filtered_chunks)} chunks in {total_time_ms:.2f}ms"
            )
            
            return RetrievalResult(
                chunks=filtered_chunks,
                similarity_scores=filtered_scores,
                total_retrieved=len(filtered_chunks),
                query=query,
                retrieval_time_ms=total_time_ms,
            )
            
        except Exception as e:
            logger.error(f"Retrieval failed for query '{query}': {e}")
            raise

    def retrieve_by_amc(
        self,
        query: str,
        amc_name: str,
        top_k: Optional[int] = None,
    ) -> RetrievalResult:
        """
        Retrieve chunks filtered by AMC name.
        
        Args:
            query: User query text
            amc_name: AMC name to filter by
            top_k: Number of results to return
            
        Returns:
            RetrievalResult with filtered chunks
        """
        logger.info(f"Retrieving chunks for AMC: {amc_name}")
        return self.retrieve(
            query=query,
            filters={"amc_name": amc_name},
            top_k=top_k,
        )

    def retrieve_by_content_type(
        self,
        query: str,
        content_type: str,
        top_k: Optional[int] = None,
    ) -> RetrievalResult:
        """
        Retrieve chunks filtered by content type.
        
        Args:
            query: User query text
            content_type: Content type to filter by (e.g., "fund_page", "blog")
            top_k: Number of results to return
            
        Returns:
            RetrievalResult with filtered chunks
        """
        logger.info(f"Retrieving chunks for content type: {content_type}")
        return self.retrieve(
            query=query,
            filters={"content_type": content_type},
            top_k=top_k,
        )

    def retrieve_multi_query(
        self,
        queries: List[str],
        top_k_per_query: int = 3,
    ) -> RetrievalResult:
        """
        Retrieve chunks for multiple related queries and merge results.
        
        Useful for query expansion or multi-aspect queries.
        
        Args:
            queries: List of query strings
            top_k_per_query: Number of chunks per query
            
        Returns:
            RetrievalResult with deduplicated and merged chunks
        """
        start_time = time.time()
        
        all_chunks = []
        all_scores = []
        seen_chunk_ids = set()
        
        for query in queries:
            result = self.retrieve(query=query, top_k=top_k_per_query)
            
            for chunk, score in zip(result.chunks, result.similarity_scores):
                if chunk.chunk_id not in seen_chunk_ids:
                    all_chunks.append(chunk)
                    all_scores.append(score)
                    seen_chunk_ids.add(chunk.chunk_id)
        
        # Sort by score
        sorted_pairs = sorted(
            zip(all_chunks, all_scores),
            key=lambda x: x[1],
            reverse=True,
        )
        
        if sorted_pairs:
            final_chunks, final_scores = zip(*sorted_pairs)
            final_chunks = list(final_chunks)[:self.top_k]
            final_scores = list(final_scores)[:self.top_k]
        else:
            final_chunks = []
            final_scores = []
        
        total_time_ms = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            chunks=final_chunks,
            similarity_scores=final_scores,
            total_retrieved=len(final_chunks),
            query=f"Multi-query: {', '.join(queries)}",
            retrieval_time_ms=total_time_ms,
        )

    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess the user query for better retrieval.
        
        Args:
            query: Raw user query
            
        Returns:
            Processed query
        """
        # Basic preprocessing
        processed = query.strip()
        
        # Remove multiple spaces
        processed = " ".join(processed.split())
        
        # TODO: Add more sophisticated preprocessing:
        # - Query expansion
        # - Synonym replacement
        # - Spell correction
        # - Entity recognition
        
        return processed

    def _rerank_results(
        self,
        query: str,
        chunks: List[KnowledgeChunk],
        scores: List[float],
        top_k: int,
    ) -> Tuple[List[KnowledgeChunk], List[float]]:
        """
        Re-rank retrieved results using additional signals.
        
        Args:
            query: Original query
            chunks: Retrieved chunks
            scores: Similarity scores
            top_k: Number of results to keep
            
        Returns:
            Tuple of (reranked_chunks, reranked_scores)
        """
        if not chunks:
            return [], []
        
        # Simple re-ranking based on multiple signals
        reranked_items = []
        
        for chunk, score in zip(chunks, scores):
            # Base score from vector similarity
            final_score = score
            
            # Boost based on content type (fund pages are more authoritative)
            if chunk.metadata.content_type == "fund_page":
                final_score *= 1.2
            elif chunk.metadata.content_type == "amc_overview":
                final_score *= 1.1
            elif chunk.metadata.content_type == "blog":
                final_score *= 0.95
            
            # Boost if query terms appear in title
            if chunk.metadata.title:
                query_lower = query.lower()
                title_lower = chunk.metadata.title.lower()
                
                # Check for query term matches in title
                query_terms = query_lower.split()
                title_match_count = sum(1 for term in query_terms if term in title_lower)
                if title_match_count > 0:
                    final_score *= (1.0 + (title_match_count * 0.05))
            
            # Boost if Groww page is available (indicates high-quality mapping)
            if chunk.groww_page_url:
                final_score *= 1.05
            
            # Cap the score at 1.0
            final_score = min(final_score, 1.0)
            
            reranked_items.append((chunk, final_score))
        
        # Sort by final score
        reranked_items.sort(key=lambda x: x[1], reverse=True)
        
        # Take top k
        reranked_items = reranked_items[:top_k]
        
        if reranked_items:
            reranked_chunks, reranked_scores = zip(*reranked_items)
            return list(reranked_chunks), list(reranked_scores)
        else:
            return [], []

    def _apply_threshold(
        self,
        chunks: List[KnowledgeChunk],
        scores: List[float],
        threshold: float,
    ) -> Tuple[List[KnowledgeChunk], List[float]]:
        """
        Filter results by similarity threshold.
        
        Args:
            chunks: List of chunks
            scores: Corresponding scores
            threshold: Minimum score
            
        Returns:
            Tuple of (filtered_chunks, filtered_scores)
        """
        filtered_pairs = [
            (chunk, score)
            for chunk, score in zip(chunks, scores)
            if score >= threshold
        ]
        
        if filtered_pairs:
            filtered_chunks, filtered_scores = zip(*filtered_pairs)
            return list(filtered_chunks), list(filtered_scores)
        else:
            return [], []

    def get_context_window(
        self,
        chunks: List[KnowledgeChunk],
        max_tokens: int = 2000,
    ) -> str:
        """
        Create a context window from retrieved chunks for LLM.
        
        Args:
            chunks: Retrieved knowledge chunks
            max_tokens: Maximum tokens (approximate)
            
        Returns:
            Formatted context string
        """
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation: 1 token ≈ 4 chars
        
        for i, chunk in enumerate(chunks, 1):
            # Format: [Source N] content
            chunk_text = f"[Source {i}] {chunk.content}\n\n"
            
            # Check if adding this chunk exceeds limit
            if total_chars + len(chunk_text) > max_chars:
                # Truncate the chunk to fit
                remaining_chars = max_chars - total_chars
                if remaining_chars > 100:  # Only add if meaningful
                    chunk_text = f"[Source {i}] {chunk.content[:remaining_chars]}...\n\n"
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            total_chars += len(chunk_text)
        
        return "".join(context_parts).strip()

    def get_sources(
        self,
        chunks: List[KnowledgeChunk],
    ) -> List[Dict[str, Any]]:
        """
        Extract source information from chunks for citation.
        
        Args:
            chunks: Retrieved knowledge chunks
            
        Returns:
            List of source dictionaries
        """
        sources = []
        seen_urls = set()
        
        for chunk in chunks:
            # Prioritize Groww page URL if available
            url = chunk.groww_page_url or chunk.source_url
            
            # Deduplicate by URL
            if url in seen_urls:
                continue
            
            seen_urls.add(url)
            
            source = {
                "url": url,
                "title": chunk.metadata.title,
                "amc_name": chunk.metadata.amc_name,
                "content_type": chunk.metadata.content_type,
            }
            
            sources.append(source)
        
        return sources

    def health_check(self) -> Dict[str, Any]:
        """
        Check if the retrieval pipeline is healthy.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check vector store health
            vector_store_health = self.vector_store.health_check()
            
            return {
                "status": "healthy" if vector_store_health["status"] == "healthy" else "unhealthy",
                "vector_store": vector_store_health,
                "top_k": self.top_k,
                "similarity_threshold": self.similarity_threshold,
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Singleton instance
_rag_retrieval_instance: Optional[RAGRetrievalPipeline] = None


def get_rag_retrieval() -> RAGRetrievalPipeline:
    """
    Get or create the singleton RAGRetrievalPipeline instance.
    
    Returns:
        RAGRetrievalPipeline instance
    """
    global _rag_retrieval_instance
    
    if _rag_retrieval_instance is None:
        _rag_retrieval_instance = RAGRetrievalPipeline()
    
    return _rag_retrieval_instance

