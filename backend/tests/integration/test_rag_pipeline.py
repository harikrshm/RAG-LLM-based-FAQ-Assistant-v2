"""
Integration tests for RAG pipeline

Tests the complete RAG retrieval and generation pipeline.
"""

import pytest
from unittest.mock import Mock, patch

from backend.services.rag_retrieval import RAGRetrievalPipeline
from backend.services.llm_service import LLMService
from backend.services.response_generator import ResponseGenerator
from backend.models.knowledge import KnowledgeChunk, ChunkMetadata, RetrievalResult


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    mock_store = Mock()
    
    sample_chunks = [
        KnowledgeChunk(
            chunk_id="chunk1",
            content="HDFC Equity Fund expense ratio is 1.5% per annum.",
            source_url="https://groww.in/fund1",
            chunk_index=0,
            metadata=ChunkMetadata(
                source_url="https://groww.in/fund1",
                amc_name="HDFC Mutual Fund",
                title="HDFC Equity Fund",
                content_type="fund_page",
            ),
            groww_page_url="https://groww.in/mutual-funds/hdfc-equity-fund",
        ),
    ]
    
    mock_store.search.return_value = RetrievalResult(
        chunks=sample_chunks,
        similarity_scores=[0.9],
        total_retrieved=1,
        query="expense ratio",
        retrieval_time_ms=30.0,
    )
    return mock_store


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    mock_llm = Mock(spec=LLMService)
    mock_result = Mock()
    mock_result.text = "The expense ratio is 1.5% per annum."
    mock_result.provider = "gemini"
    mock_result.model = "gemini-pro"
    mock_llm.generate.return_value = mock_result
    return mock_llm


@pytest.fixture
def mock_groww_mapper():
    """Create mock Groww mapper."""
    mock_mapper = Mock()
    mock_mapper.map_query_to_groww_pages.return_value = []
    mock_mapper.map_chunks_to_groww_pages.return_value = {
        "chunk1": "https://groww.in/mutual-funds/hdfc-equity-fund",
    }
    return mock_mapper


class TestRAGPipelineIntegration:
    """Test RAG pipeline integration."""
    
    @patch("backend.services.rag_retrieval.get_vector_store")
    def test_rag_retrieval_pipeline(
        self,
        mock_get_store,
        mock_vector_store,
    ):
        """Test RAG retrieval pipeline."""
        mock_get_store.return_value = mock_vector_store
        
        pipeline = RAGRetrievalPipeline(top_k=5, similarity_threshold=0.5)
        
        result = pipeline.retrieve("What is the expense ratio of HDFC Equity Fund?")
        
        assert isinstance(result, RetrievalResult)
        assert len(result.chunks) > 0
        assert result.total_retrieved > 0
        assert result.retrieval_time_ms > 0
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    def test_response_generation_pipeline(
        self,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
        mock_groww_mapper,
    ):
        """Test complete response generation pipeline."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve.return_value = RetrievalResult(
            chunks=[
                KnowledgeChunk(
                    chunk_id="chunk1",
                    content="Expense ratio is 1.5%",
                    source_url="https://groww.in/fund1",
                    chunk_index=0,
                    metadata=ChunkMetadata(source_url="https://groww.in/fund1"),
                ),
            ],
            similarity_scores=[0.9],
            total_retrieved=1,
            query="expense ratio",
            retrieval_time_ms=30.0,
        )
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = mock_groww_mapper
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio?",
            session_id="test-session",
        )
        
        assert "response" in result
        assert "sources" in result
        assert "chunks_retrieved" in result
        assert result["chunks_retrieved"] > 0
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    def test_pipeline_with_groww_mapping(
        self,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
        mock_groww_mapper,
    ):
        """Test pipeline with Groww page mapping."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve.return_value = RetrievalResult(
            chunks=[
                KnowledgeChunk(
                    chunk_id="chunk1",
                    content="Test content",
                    source_url="https://example.com",
                    chunk_index=0,
                    metadata=ChunkMetadata(source_url="https://example.com"),
                ),
            ],
            similarity_scores=[0.9],
            total_retrieved=1,
            query="test",
            retrieval_time_ms=30.0,
        )
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = mock_groww_mapper
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="Test query",
            session_id="test-session",
        )
        
        # Verify Groww mapper was called
        assert mock_groww_mapper.map_chunks_to_groww_pages.called
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    def test_pipeline_fallback_mechanism(
        self,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_llm_service,
        mock_groww_mapper,
    ):
        """Test pipeline fallback mechanism when no chunks found."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve.return_value = RetrievalResult(
            chunks=[],
            similarity_scores=[],
            total_retrieved=0,
            query="unknown query",
            retrieval_time_ms=20.0,
        )
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = mock_groww_mapper
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="Unknown query",
            session_id="test-session",
        )
        
        assert result["is_fallback"] is True
        assert result["chunks_retrieved"] == 0
        assert result["fallback_level"] == "generic"

