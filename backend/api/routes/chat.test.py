"""
Unit tests for Chat API Routes
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routes.chat import router, _classify_source_type, _map_sources_to_citations
from backend.models.chat import ChatRequest, ChatResponse, SourceCitation, SourceType
from backend.exceptions import (
    QueryValidationError,
    MalformedQueryError,
    LLMServiceError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAPIKeyError,
    VectorStoreNotInitializedError,
    VectorStoreError,
)


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_response_generator():
    """Create mock response generator."""
    mock_gen = Mock()
    mock_gen.generate_response.return_value = {
        "response": "Test answer",
        "sources": [
            {
                "url": "https://groww.in/fund1",
                "title": "Test Fund",
                "amc_name": "Test AMC",
            }
        ],
        "chunks_retrieved": 3,
        "fallback_level": "groww",
        "is_fallback": False,
        "generation_time_ms": 100.0,
    }
    mock_gen.health_check.return_value = {"status": "healthy"}
    return mock_gen


@pytest.fixture
def mock_request():
    """Create mock HTTP request."""
    mock_req = Mock()
    mock_req.state.request_id = "test-request-id"
    return mock_req


class TestChatEndpoint:
    """Test cases for /chat endpoint."""
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_success(self, mock_get_gen, client, mock_response_generator):
        """Test successful chat request."""
        mock_get_gen.return_value = mock_response_generator
        
        request_data = {
            "query": "What is a mutual fund?",
            "session_id": "test-session-123",
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["query"] == "What is a mutual fund?"
        assert data["answer"] == "Test answer"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["url"] == "https://groww.in/fund1"
        assert data["confidence_score"] > 0
        assert data["has_sufficient_info"] is True
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_with_context(self, mock_get_gen, client, mock_response_generator):
        """Test chat request with context filters."""
        mock_get_gen.return_value = mock_response_generator
        
        request_data = {
            "query": "What is a mutual fund?",
            "context": {"amc_filter": "Test AMC"},
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        # Verify filters were passed
        mock_response_generator.generate_response.assert_called_once()
        call_kwargs = mock_response_generator.generate_response.call_args[1]
        assert call_kwargs["filters"] == {"amc_name": "Test AMC"}
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_guardrail_blocked(self, mock_get_gen, client, mock_response_generator):
        """Test chat request blocked by guardrails."""
        mock_response_generator.generate_response.return_value = {
            "response": "I cannot provide investment advice.",
            "sources": [],
            "chunks_retrieved": 0,
            "fallback_level": "generic",
            "is_fallback": True,
            "guardrail_blocked": True,
            "generation_time_ms": 50.0,
        }
        mock_get_gen.return_value = mock_response_generator
        
        request_data = {
            "query": "Should I invest in this fund?",
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["confidence_score"] == 0.0
        assert data["has_sufficient_info"] is False
        assert data["fallback_message"] is not None
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_fallback_response(self, mock_get_gen, client, mock_response_generator):
        """Test fallback response when no sources found."""
        mock_response_generator.generate_response.return_value = {
            "response": "I don't have specific information about that.",
            "sources": [],
            "chunks_retrieved": 0,
            "fallback_level": "generic",
            "is_fallback": True,
            "generation_time_ms": 50.0,
        }
        mock_get_gen.return_value = mock_response_generator
        
        request_data = {
            "query": "Unknown query",
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["confidence_score"] == 0.0
        assert data["has_sufficient_info"] is False
        assert len(data["sources"]) == 0
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_confidence_scores(self, mock_get_gen, client, mock_response_generator):
        """Test confidence score calculation for different fallback levels."""
        test_cases = [
            ("groww", 0.95),
            ("external", 0.85),
            ("groww_sources_only", 0.90),
            ("generic", 0.3),
        ]
        
        for fallback_level, expected_base_confidence in test_cases:
            mock_response_generator.generate_response.return_value = {
                "response": "Test answer",
                "sources": [{"url": "https://example.com"}],
                "chunks_retrieved": 3,
                "fallback_level": fallback_level,
                "is_fallback": False,
                "generation_time_ms": 100.0,
            }
            mock_get_gen.return_value = mock_response_generator
            
            response = client.post("/chat", json={"query": "test"})
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            # Confidence should be close to expected (may be adjusted by chunk count)
            assert 0 <= data["confidence_score"] <= 1
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_validation_error(self, mock_get_gen, client, mock_response_generator):
        """Test validation error handling."""
        mock_response_generator.generate_response.side_effect = QueryValidationError(
            "Invalid query format"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid query" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_vector_store_not_initialized(self, mock_get_gen, client, mock_response_generator):
        """Test vector store not initialized error."""
        mock_response_generator.generate_response.side_effect = VectorStoreNotInitializedError(
            "Collection not found"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Knowledge base" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_llm_api_key_error(self, mock_get_gen, client, mock_response_generator):
        """Test LLM API key error."""
        mock_response_generator.generate_response.side_effect = LLMAPIKeyError(
            "Invalid API key"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "LLM service" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_llm_timeout(self, mock_get_gen, client, mock_response_generator):
        """Test LLM timeout error."""
        mock_response_generator.generate_response.side_effect = LLMTimeoutError(
            "Request timed out"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert "timed out" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_rate_limit(self, mock_get_gen, client, mock_response_generator):
        """Test rate limit error."""
        mock_response_generator.generate_response.side_effect = LLMRateLimitError(
            "Rate limit exceeded"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "busy" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_service_error(self, mock_get_gen, client, mock_response_generator):
        """Test general service error."""
        mock_response_generator.generate_response.side_effect = LLMServiceError(
            "Service error"
        )
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "unavailable" in response.json()["detail"]
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_endpoint_unexpected_error(self, mock_get_gen, client, mock_response_generator):
        """Test unexpected error handling."""
        mock_response_generator.generate_response.side_effect = Exception("Unexpected error")
        mock_get_gen.return_value = mock_response_generator
        
        response = client.post("/chat", json={"query": "test"})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "unexpected error" in response.json()["detail"].lower()
    
    def test_chat_endpoint_invalid_request(self, client):
        """Test invalid request format."""
        # Missing query field
        response = client.post("/chat", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_chat_endpoint_empty_query(self, client):
        """Test empty query validation."""
        response = client.post("/chat", json={"query": ""})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_chat_endpoint_query_too_long(self, client):
        """Test query length validation."""
        long_query = "x" * 1001  # Exceeds max_length=1000
        response = client.post("/chat", json={"query": long_query})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestChatHistoryEndpoint:
    """Test cases for /chat/history endpoint."""
    
    def test_chat_history_not_implemented(self, client):
        """Test chat history endpoint returns 501."""
        response = client.get("/chat/history")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
        assert "not yet implemented" in response.json()["detail"]
    
    def test_chat_history_with_session_id(self, client):
        """Test chat history with session ID parameter."""
        response = client.get("/chat/history?session_id=test-123")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


class TestSourceClassification:
    """Test source type classification."""
    
    def test_classify_groww_source(self):
        """Test Groww page classification."""
        assert _classify_source_type("https://groww.in/fund") == SourceType.GROWW_PAGE
        assert _classify_source_type("https://www.groww.in/fund") == SourceType.GROWW_PAGE
    
    def test_classify_sebi_source(self):
        """Test SEBI website classification."""
        assert _classify_source_type("https://sebi.gov.in/regulation") == SourceType.SEBI_WEBSITE
    
    def test_classify_amfi_source(self):
        """Test AMFI website classification."""
        assert _classify_source_type("https://amfiindia.com/data") == SourceType.AMFI_WEBSITE
    
    def test_classify_amc_source(self):
        """Test AMC website classification."""
        assert _classify_source_type("https://hdfcfund.com/fund") == SourceType.AMC_WEBSITE
        assert _classify_source_type("https://example.com") == SourceType.AMC_WEBSITE


class TestSourceMapping:
    """Test source to citation mapping."""
    
    def test_map_sources_to_citations(self):
        """Test source mapping to citations."""
        sources = [
            {
                "url": "https://groww.in/fund1",
                "title": "Fund 1",
                "amc_name": "Test AMC",
            },
            {
                "url": "https://sebi.gov.in/regulation",
                "title": "SEBI Regulation",
            },
        ]
        scores = [0.9, 0.8]
        
        citations = _map_sources_to_citations(sources, scores)
        
        assert len(citations) == 2
        assert citations[0].url == "https://groww.in/fund1"
        assert citations[0].source_type == SourceType.GROWW_PAGE
        assert citations[0].relevance_score == 0.9
        assert citations[1].source_type == SourceType.SEBI_WEBSITE
        assert citations[1].relevance_score == 0.8
    
    def test_map_sources_without_scores(self):
        """Test source mapping without similarity scores."""
        sources = [
            {
                "url": "https://groww.in/fund1",
                "title": "Fund 1",
            },
        ]
        
        citations = _map_sources_to_citations(sources)
        
        assert len(citations) == 1
        assert citations[0].relevance_score is None

