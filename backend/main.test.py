"""
Unit tests for Main Application Endpoints
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for /health endpoint."""
    
    @patch("backend.main.settings")
    def test_health_endpoint(self, mock_settings, client):
        """Test basic health check endpoint."""
        mock_settings.ENVIRONMENT = "test"
        mock_settings.VERSION = "1.0.0"
        
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["environment"] == "test"
        assert data["version"] == "1.0.0"
        assert data["service"] == "mutual-funds-faq-assistant"
        assert "timestamp" in data


class TestReadinessEndpoint:
    """Test cases for /ready endpoint."""
    
    @patch("backend.main.get_metrics")
    @patch("backend.main.get_response_generator")
    @patch("backend.main.get_rag_retrieval")
    @patch("backend.main.get_llm_service")
    @patch("backend.main.get_vector_store")
    def test_readiness_all_healthy(
        self,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
    ):
        """Test readiness check when all components are healthy."""
        # Mock vector store
        mock_store = Mock()
        mock_store.health_check.return_value = {
            "status": "healthy",
            "document_count": 100,
            "collection_accessible": True,
        }
        mock_get_store.return_value = mock_store
        
        # Mock LLM service
        mock_llm = Mock()
        mock_llm.health_check.return_value = {
            "status": "healthy",
            "client_initialized": True,
        }
        mock_get_llm.return_value = mock_llm
        
        # Mock RAG retrieval
        mock_rag = Mock()
        mock_rag.health_check.return_value = {"status": "healthy"}
        mock_get_rag.return_value = mock_rag
        
        # Mock response generator
        mock_gen = Mock()
        mock_gen.health_check.return_value = {"status": "healthy"}
        mock_get_gen.return_value = mock_gen
        
        # Mock metrics
        mock_met = Mock()
        mock_get_metrics.return_value = mock_met
        
        response = client.get("/ready")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["vector_store"] == "healthy"
        assert data["checks"]["llm_service"] == "healthy"
    
    @patch("backend.main.get_metrics")
    @patch("backend.main.get_response_generator")
    @patch("backend.main.get_rag_retrieval")
    @patch("backend.main.get_llm_service")
    @patch("backend.main.get_vector_store")
    def test_readiness_unhealthy(
        self,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
    ):
        """Test readiness check when components are unhealthy."""
        # Mock vector store as unhealthy
        mock_store = Mock()
        mock_store.health_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
        }
        mock_get_store.return_value = mock_store
        
        # Mock other components as healthy
        mock_llm = Mock()
        mock_llm.health_check.return_value = {"status": "healthy"}
        mock_get_llm.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag.health_check.return_value = {"status": "healthy"}
        mock_get_rag.return_value = mock_rag
        
        mock_gen = Mock()
        mock_gen.health_check.return_value = {"status": "healthy"}
        mock_get_gen.return_value = mock_gen
        
        mock_met = Mock()
        mock_get_metrics.return_value = mock_met
        
        response = client.get("/ready")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "not_ready"
        assert "checks" in data
        assert data["checks"]["vector_store"] == "unhealthy"
    
    @patch("backend.main.get_metrics")
    @patch("backend.main.get_response_generator")
    @patch("backend.main.get_rag_retrieval")
    @patch("backend.main.get_llm_service")
    @patch("backend.main.get_vector_store")
    def test_readiness_with_exceptions(
        self,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
    ):
        """Test readiness check with component exceptions."""
        # Vector store raises exception
        mock_get_store.side_effect = Exception("Connection error")
        
        # Other components healthy
        mock_llm = Mock()
        mock_llm.health_check.return_value = {"status": "healthy"}
        mock_get_llm.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag.health_check.return_value = {"status": "healthy"}
        mock_get_rag.return_value = mock_rag
        
        mock_gen = Mock()
        mock_gen.health_check.return_value = {"status": "healthy"}
        mock_get_gen.return_value = mock_gen
        
        mock_met = Mock()
        mock_get_metrics.return_value = mock_met
        
        response = client.get("/ready")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["checks"]["vector_store"] == "unhealthy"

