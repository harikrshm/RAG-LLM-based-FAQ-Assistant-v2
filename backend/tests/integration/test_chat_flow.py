"""
Integration tests for end-to-end chat flow

Tests the complete flow from API request to response generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.chat import ChatRequest, ChatResponse
from backend.models.knowledge import KnowledgeChunk, ChunkMetadata, RetrievalResult


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    mock_store = Mock()
    
    # Mock search to return sample chunks
    sample_chunks = [
        KnowledgeChunk(
            chunk_id="chunk1",
            content="HDFC Equity Fund has an expense ratio of 1.5% per annum.",
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
        KnowledgeChunk(
            chunk_id="chunk2",
            content="The minimum SIP amount for HDFC Equity Fund is Rs. 500 per month.",
            source_url="https://groww.in/fund1",
            chunk_index=1,
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
        similarity_scores=[0.9, 0.85],
        total_retrieved=2,
        query="expense ratio",
        retrieval_time_ms=50.0,
    )
    mock_store.health_check.return_value = {"status": "healthy"}
    return mock_store


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    mock_llm = Mock()
    mock_llm.generate.return_value = Mock(
        provider="gemini",
        model="gemini-pro",
        text="The expense ratio of HDFC Equity Fund is 1.5% per annum. This is the annual fee charged by the fund for managing your investment.",
        finish_reason="STOP",
        prompt_tokens=100,
        completion_tokens=25,
        total_tokens=125,
    )
    mock_llm.health_check.return_value = {"status": "healthy"}
    return mock_llm


@pytest.fixture
def mock_response_generator(mock_vector_store, mock_llm_service):
    """Create mock response generator."""
    with patch("backend.services.response_generator.get_rag_retrieval", return_value=mock_vector_store):
        with patch("backend.services.response_generator.get_llm_service", return_value=mock_llm_service):
            with patch("backend.services.response_generator.get_groww_mapper") as mock_mapper:
                mock_mapper.return_value = Mock()
                from backend.services.response_generator import ResponseGenerator
                generator = ResponseGenerator()
                return generator


class TestEndToEndChatFlow:
    """Test end-to-end chat flow."""
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_complete_chat_flow_success(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test successful end-to-end chat flow."""
        # Setup mocks
        mock_get_gen.return_value = mock_response_generator
        
        # Mock response generator
        mock_response_generator.generate_response.return_value = {
            "response": "The expense ratio of HDFC Equity Fund is 1.5% per annum.",
            "sources": [
                {
                    "url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                    "title": "HDFC Equity Fund",
                    "amc_name": "HDFC Mutual Fund",
                }
            ],
            "chunks_retrieved": 2,
            "fallback_level": "groww",
            "is_fallback": False,
            "generation_time_ms": 150.0,
        }
        
        # Send chat request
        request_data = {
            "query": "What is the expense ratio of HDFC Equity Fund?",
            "session_id": "test-session-123",
        }
        
        response = client.post("/chat", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What is the expense ratio of HDFC Equity Fund?"
        assert "expense ratio" in data["answer"].lower()
        assert len(data["sources"]) > 0
        assert data["confidence_score"] > 0
        assert data["has_sufficient_info"] is True
        assert data["retrieved_chunks_count"] == 2
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_with_sources(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test chat flow with source citations."""
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "HDFC Equity Fund has an expense ratio of 1.5%.",
            "sources": [
                {
                    "url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                    "title": "HDFC Equity Fund",
                    "amc_name": "HDFC Mutual Fund",
                },
                {
                    "url": "https://example.com/fund-info",
                    "title": "Fund Information",
                    "amc_name": "HDFC Mutual Fund",
                },
            ],
            "chunks_retrieved": 3,
            "fallback_level": "groww",
            "is_fallback": False,
            "generation_time_ms": 120.0,
        }
        
        response = client.post("/chat", json={
            "query": "Tell me about HDFC Equity Fund",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) == 2
        assert data["sources"][0]["source_type"] == "groww_page"
        assert data["sources"][0]["url"] == "https://groww.in/mutual-funds/hdfc-equity-fund"
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_fallback_response(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test chat flow with fallback response."""
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "I don't have specific information about that topic.",
            "sources": [],
            "chunks_retrieved": 0,
            "fallback_level": "generic",
            "is_fallback": True,
            "generation_time_ms": 50.0,
        }
        
        response = client.post("/chat", json={
            "query": "Unknown query about something",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["confidence_score"] == 0.0
        assert data["has_sufficient_info"] is False
        assert len(data["sources"]) == 0
        assert data["fallback_message"] is not None
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_with_context_filter(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test chat flow with AMC context filter."""
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "Test response",
            "sources": [],
            "chunks_retrieved": 1,
            "fallback_level": "external",
            "is_fallback": False,
            "generation_time_ms": 100.0,
        }
        
        response = client.post("/chat", json={
            "query": "What is the expense ratio?",
            "context": {"amc_filter": "HDFC Mutual Fund"},
        })
        
        assert response.status_code == 200
        # Verify filters were passed
        call_args = mock_response_generator.generate_response.call_args
        assert call_args[1]["filters"] == {"amc_name": "HDFC Mutual Fund"}
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_error_handling(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test error handling in chat flow."""
        mock_get_gen.return_value = mock_response_generator
        
        # Simulate service error
        mock_response_generator.generate_response.side_effect = Exception("Service error")
        
        response = client.post("/chat", json={
            "query": "Test query",
        })
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_validation_error(
        self,
        mock_get_gen,
        client,
    ):
        """Test validation error handling."""
        # Empty query
        response = client.post("/chat", json={
            "query": "",
        })
        
        assert response.status_code == 422
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_timeout_error(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test timeout error handling."""
        from backend.exceptions import LLMTimeoutError
        
        mock_get_gen.return_value = mock_response_generator
        mock_response_generator.generate_response.side_effect = LLMTimeoutError(
            "Request timed out"
        )
        
        response = client.post("/chat", json={
            "query": "Test query",
        })
        
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_rate_limit_error(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test rate limit error handling."""
        from backend.exceptions import LLMRateLimitError
        
        mock_get_gen.return_value = mock_response_generator
        mock_response_generator.generate_response.side_effect = LLMRateLimitError(
            "Rate limit exceeded"
        )
        
        response = client.post("/chat", json={
            "query": "Test query",
        })
        
        assert response.status_code == 429
        assert "busy" in response.json()["detail"].lower()
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_vector_store_error(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test vector store error handling."""
        from backend.exceptions import VectorStoreNotInitializedError
        
        mock_get_gen.return_value = mock_response_generator
        mock_response_generator.generate_response.side_effect = VectorStoreNotInitializedError(
            "Collection not found"
        )
        
        response = client.post("/chat", json={
            "query": "Test query",
        })
        
        assert response.status_code == 503
        assert "knowledge base" in response.json()["detail"].lower()
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_flow_guardrail_blocking(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test guardrail blocking investment advice."""
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "I cannot provide investment advice.",
            "sources": [],
            "chunks_retrieved": 0,
            "fallback_level": "generic",
            "is_fallback": True,
            "guardrail_blocked": True,
            "generation_time_ms": 30.0,
        }
        
        response = client.post("/chat", json={
            "query": "Should I invest in this fund?",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["confidence_score"] == 0.0
        assert data["has_sufficient_info"] is False
        assert "investment advice" in data["fallback_message"].lower()


class TestChatFlowWithRealServices:
    """Integration tests with real service instances (requires setup)."""
    
    @pytest.mark.skip(reason="Requires real vector store and LLM setup")
    def test_real_chat_flow(self, client):
        """Test chat flow with real services (requires data ingestion)."""
        response = client.post("/chat", json={
            "query": "What is a mutual fund?",
            "session_id": "integration-test-session",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0
    
    @pytest.mark.skip(reason="Requires real services")
    def test_real_chat_flow_with_sources(self, client):
        """Test chat flow with real sources."""
        response = client.post("/chat", json={
            "query": "What is the expense ratio of HDFC Equity Fund?",
        })
        
        assert response.status_code == 200
        data = response.json()
        if data["has_sufficient_info"]:
            assert len(data["sources"]) > 0


class TestChatFlowPerformance:
    """Test chat flow performance characteristics."""
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_response_time_tracking(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test that response time is tracked."""
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "Test answer",
            "sources": [],
            "chunks_retrieved": 1,
            "fallback_level": "groww",
            "is_fallback": False,
            "generation_time_ms": 150.0,
        }
        
        response = client.post("/chat", json={
            "query": "Test query",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response_time_ms" in data
        assert data["response_time_ms"] > 0
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_concurrent_requests(
        self,
        mock_get_gen,
        client,
        mock_response_generator,
    ):
        """Test handling of concurrent requests."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        mock_get_gen.return_value = mock_response_generator
        
        mock_response_generator.generate_response.return_value = {
            "response": "Test answer",
            "sources": [],
            "chunks_retrieved": 1,
            "fallback_level": "groww",
            "is_fallback": False,
            "generation_time_ms": 100.0,
        }
        
        def send_request():
            return client.post("/chat", json={
                "query": "Test query",
            })
        
        # Send 5 concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        assert len(results) == 5

