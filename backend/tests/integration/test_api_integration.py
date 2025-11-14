"""
Integration tests for API endpoints

Tests API endpoints with mocked services.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIIntegration:
    """Test API endpoint integration."""
    
    @patch("backend.api.routes.chat.get_response_generator")
    def test_chat_api_integration(self, mock_get_gen, client):
        """Test chat API endpoint integration."""
        mock_gen = Mock()
        mock_gen.generate_response.return_value = {
            "response": "Test answer",
            "sources": [{"url": "https://example.com", "title": "Test"}],
            "chunks_retrieved": 2,
            "fallback_level": "groww",
            "is_fallback": False,
            "generation_time_ms": 100.0,
        }
        mock_get_gen.return_value = mock_gen
        
        response = client.post("/chat", json={
            "query": "Test question",
            "session_id": "test-session",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Test question"
        assert "answer" in data
        assert "sources" in data
    
    def test_health_endpoint_integration(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch("backend.main.get_vector_store")
    @patch("backend.main.get_llm_service")
    @patch("backend.main.get_rag_retrieval")
    @patch("backend.main.get_response_generator")
    def test_readiness_endpoint_integration(
        self,
        mock_get_gen,
        mock_get_rag,
        mock_get_llm,
        mock_get_store,
        client,
    ):
        """Test readiness endpoint with all services."""
        # Mock all services as healthy
        mock_store = Mock()
        mock_store.health_check.return_value = {"status": "healthy", "document_count": 100}
        mock_get_store.return_value = mock_store
        
        mock_llm = Mock()
        mock_llm.health_check.return_value = {"status": "healthy"}
        mock_get_llm.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag.health_check.return_value = {"status": "healthy"}
        mock_get_rag.return_value = mock_rag
        
        mock_gen = Mock()
        mock_gen.health_check.return_value = {"status": "healthy"}
        mock_get_gen.return_value = mock_gen
        
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["vector_store"] == "healthy"
        assert data["checks"]["llm_service"] == "healthy"
    
    @patch("backend.api.routes.health.get_vector_store")
    def test_vector_store_health_integration(self, mock_get_store, client):
        """Test vector store health endpoint."""
        mock_store = Mock()
        mock_store.health_check.return_value = {
            "status": "healthy",
            "document_count": 100,
        }
        mock_store.get_collection_stats.return_value = {
            "total_chunks": 100,
            "embedding_dimension": 384,
        }
        mock_get_store.return_value = mock_store
        
        response = client.get("/health/vector-store")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "statistics" in data
    
    @patch("backend.api.routes.health.get_llm_service")
    def test_llm_health_integration(self, mock_get_llm, client):
        """Test LLM health endpoint."""
        mock_llm = Mock()
        mock_llm.health_check.return_value = {
            "status": "healthy",
            "provider": "gemini",
            "model": "gemini-pro",
        }
        mock_get_llm.return_value = mock_llm
        
        response = client.get("/health/llm")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["provider"] == "gemini"
    
    @patch("backend.api.routes.health.get_rag_retrieval")
    def test_rag_pipeline_health_integration(self, mock_get_rag, client):
        """Test RAG pipeline health endpoint."""
        mock_rag = Mock()
        mock_rag.health_check.return_value = {
            "status": "healthy",
            "top_k": 5,
        }
        mock_get_rag.return_value = mock_rag
        
        response = client.get("/health/rag-pipeline")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "details" in data

