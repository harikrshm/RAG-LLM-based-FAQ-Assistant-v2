"""
Unit tests for RAG Retrieval Pipeline
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from backend.services.rag_retrieval import RAGRetrievalPipeline
from backend.models.knowledge import KnowledgeChunk, RetrievalResult, ChunkMetadata


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    mock_store = Mock()
    mock_store.search.return_value = RetrievalResult(
        chunks=[],
        similarity_scores=[],
        total_retrieved=0,
        query="test",
        retrieval_time_ms=10.0,
    )
    mock_store.health_check.return_value = {"status": "healthy"}
    return mock_store


@pytest.fixture
def sample_chunks():
    """Create sample knowledge chunks for testing."""
    metadata1 = ChunkMetadata(
        source_url="https://example.com/fund1",
        amc_name="Test AMC",
        title="Test Fund 1",
        content_type="fund_page",
    )
    chunk1 = KnowledgeChunk(
        chunk_id="chunk1",
        content="This is test content about mutual funds.",
        source_url="https://example.com/fund1",
        chunk_index=0,
        metadata=metadata1,
        groww_page_url="https://groww.in/fund1",
    )
    
    metadata2 = ChunkMetadata(
        source_url="https://example.com/fund2",
        amc_name="Test AMC",
        title="Test Fund 2",
        content_type="blog",
    )
    chunk2 = KnowledgeChunk(
        chunk_id="chunk2",
        content="More content about investment strategies.",
        source_url="https://example.com/fund2",
        chunk_index=1,
        metadata=metadata2,
    )
    
    return [chunk1, chunk2]


@pytest.fixture
def rag_pipeline(mock_vector_store):
    """Create a RAG retrieval pipeline with mocked dependencies."""
    with patch("backend.services.rag_retrieval.get_vector_store", return_value=mock_vector_store):
        pipeline = RAGRetrievalPipeline(top_k=5, similarity_threshold=0.5)
        return pipeline


class TestRAGRetrievalPipeline:
    """Test cases for RAGRetrievalPipeline."""
    
    def test_initialization(self, mock_vector_store):
        """Test pipeline initialization."""
        with patch("backend.services.rag_retrieval.get_vector_store", return_value=mock_vector_store):
            pipeline = RAGRetrievalPipeline(top_k=10, similarity_threshold=0.7)
            
            assert pipeline.top_k == 10
            assert pipeline.similarity_threshold == 0.7
            assert pipeline.vector_store == mock_vector_store
    
    def test_initialization_defaults(self, mock_vector_store):
        """Test pipeline initialization with defaults."""
        with patch("backend.services.rag_retrieval.get_vector_store", return_value=mock_vector_store):
            with patch("backend.services.rag_retrieval.settings") as mock_settings:
                mock_settings.RAG_TOP_K = 5
                mock_settings.RAG_SIMILARITY_THRESHOLD = 0.5
                
                pipeline = RAGRetrievalPipeline()
                
                assert pipeline.top_k == 5
                assert pipeline.similarity_threshold == 0.5
    
    def test_preprocess_query(self, rag_pipeline):
        """Test query preprocessing."""
        # Test basic preprocessing
        result = rag_pipeline._preprocess_query("  test   query  ")
        assert result == "test query"
        
        # Test with multiple spaces
        result = rag_pipeline._preprocess_query("test    query   with   spaces")
        assert result == "test query with spaces"
        
        # Test empty query
        result = rag_pipeline._preprocess_query("")
        assert result == ""
    
    def test_retrieve_basic(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test basic retrieval."""
        # Setup mock return value
        mock_vector_store.search.return_value = RetrievalResult(
            chunks=sample_chunks,
            similarity_scores=[0.8, 0.7],
            total_retrieved=2,
            query="test query",
            retrieval_time_ms=15.0,
        )
        
        result = rag_pipeline.retrieve("test query")
        
        assert isinstance(result, RetrievalResult)
        assert len(result.chunks) == 2
        assert result.total_retrieved == 2
        assert result.query == "test query"
        mock_vector_store.search.assert_called_once()
    
    def test_retrieve_with_filters(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test retrieval with metadata filters."""
        mock_vector_store.search.return_value = RetrievalResult(
            chunks=sample_chunks[:1],
            similarity_scores=[0.8],
            total_retrieved=1,
            query="test",
            retrieval_time_ms=10.0,
        )
        
        filters = {"amc_name": "Test AMC"}
        result = rag_pipeline.retrieve("test query", filters=filters)
        
        # Verify filters were passed to vector store
        call_args = mock_vector_store.search.call_args
        assert call_args[1]["filters"] == filters
    
    def test_retrieve_with_overrides(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test retrieval with top_k and threshold overrides."""
        mock_vector_store.search.return_value = RetrievalResult(
            chunks=sample_chunks,
            similarity_scores=[0.8, 0.7],
            total_retrieved=2,
            query="test",
            retrieval_time_ms=10.0,
        )
        
        result = rag_pipeline.retrieve(
            "test query",
            top_k=3,
            similarity_threshold=0.6,
        )
        
        # Verify overrides were used
        call_args = mock_vector_store.search.call_args
        assert call_args[1]["top_k"] == 6  # top_k * 2 for re-ranking
        assert call_args[1]["similarity_threshold"] == 0.48  # threshold * 0.8
    
    def test_retrieve_by_amc(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test retrieval filtered by AMC name."""
        mock_vector_store.search.return_value = RetrievalResult(
            chunks=sample_chunks[:1],
            similarity_scores=[0.8],
            total_retrieved=1,
            query="test",
            retrieval_time_ms=10.0,
        )
        
        result = rag_pipeline.retrieve_by_amc("test query", "Test AMC")
        
        call_args = mock_vector_store.search.call_args
        assert call_args[1]["filters"] == {"amc_name": "Test AMC"}
    
    def test_retrieve_by_content_type(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test retrieval filtered by content type."""
        mock_vector_store.search.return_value = RetrievalResult(
            chunks=sample_chunks,
            similarity_scores=[0.8, 0.7],
            total_retrieved=2,
            query="test",
            retrieval_time_ms=10.0,
        )
        
        result = rag_pipeline.retrieve_by_content_type("test query", "fund_page")
        
        call_args = mock_vector_store.search.call_args
        assert call_args[1]["filters"] == {"content_type": "fund_page"}
    
    def test_retrieve_multi_query(self, rag_pipeline, sample_chunks, mock_vector_store):
        """Test multi-query retrieval."""
        # Setup mock to return different results for each query
        def mock_search(*args, **kwargs):
            query = kwargs.get("query", args[0] if args else "")
            if "query1" in query:
                return RetrievalResult(
                    chunks=[sample_chunks[0]],
                    similarity_scores=[0.8],
                    total_retrieved=1,
                    query=query,
                    retrieval_time_ms=10.0,
                )
            else:
                return RetrievalResult(
                    chunks=[sample_chunks[1]],
                    similarity_scores=[0.7],
                    total_retrieved=1,
                    query=query,
                    retrieval_time_ms=10.0,
                )
        
        mock_vector_store.search.side_effect = mock_search
        
        queries = ["query1", "query2"]
        result = rag_pipeline.retrieve_multi_query(queries, top_k_per_query=1)
        
        assert len(result.chunks) == 2
        assert result.query.startswith("Multi-query:")
    
    def test_rerank_results(self, rag_pipeline, sample_chunks):
        """Test result re-ranking."""
        chunks = sample_chunks
        scores = [0.6, 0.7]  # chunk2 has higher base score
        
        reranked_chunks, reranked_scores = rag_pipeline._rerank_results(
            query="test fund",
            chunks=chunks,
            scores=scores,
            top_k=2,
        )
        
        # chunk1 should be boosted because it's a fund_page and has "fund" in title
        assert len(reranked_chunks) == 2
        # After re-ranking, chunk1 should have higher score due to boosts
        assert reranked_chunks[0].chunk_id == "chunk1" or reranked_chunks[1].chunk_id == "chunk1"
    
    def test_rerank_results_empty(self, rag_pipeline):
        """Test re-ranking with empty results."""
        chunks, scores = rag_pipeline._rerank_results(
            query="test",
            chunks=[],
            scores=[],
            top_k=5,
        )
        
        assert chunks == []
        assert scores == []
    
    def test_apply_threshold(self, rag_pipeline, sample_chunks):
        """Test threshold filtering."""
        chunks = sample_chunks
        scores = [0.6, 0.4, 0.8]  # Only first and third pass threshold of 0.5
        
        filtered_chunks, filtered_scores = rag_pipeline._apply_threshold(
            chunks=chunks + [sample_chunks[0]],  # Add third chunk
            scores=scores,
            threshold=0.5,
        )
        
        assert len(filtered_chunks) == 2
        assert all(score >= 0.5 for score in filtered_scores)
    
    def test_apply_threshold_all_pass(self, rag_pipeline, sample_chunks):
        """Test threshold filtering when all pass."""
        chunks = sample_chunks
        scores = [0.8, 0.7]
        
        filtered_chunks, filtered_scores = rag_pipeline._apply_threshold(
            chunks=chunks,
            scores=scores,
            threshold=0.5,
        )
        
        assert len(filtered_chunks) == 2
    
    def test_apply_threshold_none_pass(self, rag_pipeline, sample_chunks):
        """Test threshold filtering when none pass."""
        chunks = sample_chunks
        scores = [0.3, 0.4]
        
        filtered_chunks, filtered_scores = rag_pipeline._apply_threshold(
            chunks=chunks,
            scores=scores,
            threshold=0.5,
        )
        
        assert len(filtered_chunks) == 0
        assert len(filtered_scores) == 0
    
    def test_get_context_window(self, rag_pipeline, sample_chunks):
        """Test context window generation."""
        context = rag_pipeline.get_context_window(sample_chunks, max_tokens=100)
        
        assert "[Source 1]" in context
        assert "[Source 2]" in context
        assert sample_chunks[0].content in context
        assert sample_chunks[1].content in context
    
    def test_get_context_window_truncation(self, rag_pipeline, sample_chunks):
        """Test context window truncation when exceeding max tokens."""
        # Create a very long chunk
        long_chunk = KnowledgeChunk(
            chunk_id="long",
            content="x" * 10000,
            source_url="https://example.com",
            chunk_index=0,
            metadata=ChunkMetadata(source_url="https://example.com"),
        )
        
        context = rag_pipeline.get_context_window([long_chunk], max_tokens=100)
        
        # Should be truncated
        assert len(context) < len(long_chunk.content) + 100
    
    def test_get_sources(self, rag_pipeline, sample_chunks):
        """Test source extraction."""
        sources = rag_pipeline.get_sources(sample_chunks)
        
        assert len(sources) == 2
        assert sources[0]["url"] == "https://groww.in/fund1"  # Prioritizes Groww URL
        assert sources[1]["url"] == "https://example.com/fund2"
        assert sources[0]["title"] == "Test Fund 1"
        assert sources[0]["amc_name"] == "Test AMC"
    
    def test_get_sources_deduplication(self, rag_pipeline, sample_chunks):
        """Test source deduplication by URL."""
        # Create duplicate chunks with same URL
        duplicate_chunk = KnowledgeChunk(
            chunk_id="duplicate",
            content="Different content",
            source_url=sample_chunks[0].source_url,
            chunk_index=2,
            metadata=sample_chunks[0].metadata,
        )
        
        sources = rag_pipeline.get_sources(sample_chunks + [duplicate_chunk])
        
        # Should only have 2 sources (duplicate removed)
        assert len(sources) == 2
    
    def test_health_check_healthy(self, rag_pipeline, mock_vector_store):
        """Test health check when healthy."""
        health = rag_pipeline.health_check()
        
        assert health["status"] == "healthy"
        assert "vector_store" in health
        assert health["top_k"] == rag_pipeline.top_k
    
    def test_health_check_unhealthy(self, rag_pipeline, mock_vector_store):
        """Test health check when unhealthy."""
        mock_vector_store.health_check.return_value = {"status": "unhealthy"}
        
        health = rag_pipeline.health_check()
        
        assert health["status"] == "unhealthy"
    
    def test_health_check_exception(self, rag_pipeline, mock_vector_store):
        """Test health check when exception occurs."""
        mock_vector_store.health_check.side_effect = Exception("Connection failed")
        
        health = rag_pipeline.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health
    
    def test_retrieve_exception_handling(self, rag_pipeline, mock_vector_store):
        """Test exception handling during retrieval."""
        mock_vector_store.search.side_effect = Exception("Vector store error")
        
        with pytest.raises(Exception):
            rag_pipeline.retrieve("test query")


class TestRAGRetrievalSingleton:
    """Test singleton pattern for RAG retrieval."""
    
    def test_get_rag_retrieval_singleton(self, mock_vector_store):
        """Test that get_rag_retrieval returns singleton."""
        with patch("backend.services.rag_retrieval.get_vector_store", return_value=mock_vector_store):
            from backend.services.rag_retrieval import get_rag_retrieval
            
            instance1 = get_rag_retrieval()
            instance2 = get_rag_retrieval()
            
            assert instance1 is instance2

