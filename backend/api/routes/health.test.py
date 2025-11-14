"""
Unit tests for Health Check API Routes
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.api.routes.health import router


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    mock_store = Mock()
    mock_store.health_check.return_value = {
        "status": "healthy",
        "collection_accessible": True,
        "document_count": 100,
        "embedding_model_loaded": True,
    }
    mock_store.get_collection_stats.return_value = {
        "collection_name": "test_collection",
        "total_chunks": 100,
        "embedding_dimension": 384,
        "embedding_model": "test-model",
        "metadata_fields": ["source_url", "amc_name"],
    }
    return mock_store


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    mock_llm = Mock()
    mock_llm.health_check.return_value = {
        "status": "healthy",
        "provider": "gemini",
        "model": "gemini-pro",
        "temperature": 0.1,
        "max_tokens": 500,
    }
    return mock_llm


@pytest.fixture
def mock_rag_retrieval():
    """Create mock RAG retrieval."""
    mock_rag = Mock()
    mock_rag.health_check.return_value = {
        "status": "healthy",
        "vector_store": {"status": "healthy"},
        "top_k": 5,
        "similarity_threshold": 0.5,
    }
    return mock_rag


@pytest.fixture
def mock_response_generator():
    """Create mock response generator."""
    mock_gen = Mock()
    mock_gen.health_check.return_value = {
        "status": "healthy",
    }
    return mock_gen


@pytest.fixture
def mock_metrics():
    """Create mock metrics."""
    mock_met = Mock()
    mock_met.get_metrics.return_value = {
        "total_requests": 100,
        "successful_requests": 95,
        "failed_requests": 5,
        "average_response_time_ms": 250.0,
    }
    return mock_met


class TestVectorStoreHealth:
    """Test cases for /health/vector-store endpoint."""
    
    @patch("backend.api.routes.health.get_vector_store")
    def test_vector_store_health_healthy(self, mock_get_store, client, mock_vector_store):
        """Test vector store health check when healthy."""
        mock_get_store.return_value = mock_vector_store
        
        response = client.get("/health/vector-store")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "details" in data
        assert "statistics" in data
        assert data["details"]["document_count"] == 100
    
    @patch("backend.api.routes.health.get_vector_store")
    def test_vector_store_health_unhealthy(self, mock_get_store, client):
        """Test vector store health check when unhealthy."""
        mock_store = Mock()
        mock_store.health_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
        }
        mock_get_store.return_value = mock_store
        
        response = client.get("/health/vector-store")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
    
    @patch("backend.api.routes.health.get_vector_store")
    def test_vector_store_health_exception(self, mock_get_store, client):
        """Test vector store health check with exception."""
        mock_get_store.side_effect = Exception("Service unavailable")
        
        response = client.get("/health/vector-store")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


class TestLLMHealth:
    """Test cases for /health/llm endpoint."""
    
    @patch("backend.api.routes.health.get_llm_service")
    def test_llm_health_healthy(self, mock_get_llm, client, mock_llm_service):
        """Test LLM health check when healthy."""
        mock_get_llm.return_value = mock_llm_service
        
        response = client.get("/health/llm")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["provider"] == "gemini"
        assert data["model"] == "gemini-pro"
        assert "details" in data
    
    @patch("backend.api.routes.health.get_llm_service")
    def test_llm_health_unhealthy(self, mock_get_llm, client):
        """Test LLM health check when unhealthy."""
        mock_llm = Mock()
        mock_llm.health_check.return_value = {
            "status": "unhealthy",
            "error": "API key missing",
        }
        mock_get_llm.return_value = mock_llm
        
        response = client.get("/health/llm")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
    
    @patch("backend.api.routes.health.get_llm_service")
    def test_llm_health_exception(self, mock_get_llm, client):
        """Test LLM health check with exception."""
        mock_get_llm.side_effect = Exception("Service error")
        
        response = client.get("/health/llm")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


class TestRAGPipelineHealth:
    """Test cases for /health/rag-pipeline endpoint."""
    
    @patch("backend.api.routes.health.get_rag_retrieval")
    def test_rag_pipeline_health_healthy(self, mock_get_rag, client, mock_rag_retrieval):
        """Test RAG pipeline health check when healthy."""
        mock_get_rag.return_value = mock_rag_retrieval
        
        response = client.get("/health/rag-pipeline")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "details" in data
        assert data["details"]["top_k"] == 5
    
    @patch("backend.api.routes.health.get_rag_retrieval")
    def test_rag_pipeline_health_unhealthy(self, mock_get_rag, client):
        """Test RAG pipeline health check when unhealthy."""
        mock_rag = Mock()
        mock_rag.health_check.return_value = {
            "status": "unhealthy",
            "error": "Vector store unavailable",
        }
        mock_get_rag.return_value = mock_rag
        
        response = client.get("/health/rag-pipeline")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
    
    @patch("backend.api.routes.health.get_rag_retrieval")
    def test_rag_pipeline_health_exception(self, mock_get_rag, client):
        """Test RAG pipeline health check with exception."""
        mock_get_rag.side_effect = Exception("Service error")
        
        response = client.get("/health/rag-pipeline")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


class TestDetailedHealth:
    """Test cases for /health/detailed endpoint."""
    
    @patch("backend.api.routes.health.get_metrics")
    @patch("backend.api.routes.health.get_response_generator")
    @patch("backend.api.routes.health.get_rag_retrieval")
    @patch("backend.api.routes.health.get_llm_service")
    @patch("backend.api.routes.health.get_vector_store")
    @patch("backend.api.routes.health.settings")
    def test_detailed_health_all_healthy(
        self,
        mock_settings,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
        mock_vector_store,
        mock_llm_service,
        mock_rag_retrieval,
        mock_response_generator,
        mock_metrics,
    ):
        """Test detailed health check when all components are healthy."""
        mock_settings.ENVIRONMENT = "test"
        mock_settings.VERSION = "1.0.0"
        mock_get_store.return_value = mock_vector_store
        mock_get_llm.return_value = mock_llm_service
        mock_get_rag.return_value = mock_rag_retrieval
        mock_get_gen.return_value = mock_response_generator
        mock_get_metrics.return_value = mock_metrics
        
        response = client.get("/health/detailed")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["all_systems_operational"] is True
        assert "components" in data
        assert "vector_store" in data["components"]
        assert "llm_service" in data["components"]
        assert "rag_retrieval" in data["components"]
        assert "response_generator" in data["components"]
        assert "metrics" in data["components"]
    
    @patch("backend.api.routes.health.get_metrics")
    @patch("backend.api.routes.health.get_response_generator")
    @patch("backend.api.routes.health.get_rag_retrieval")
    @patch("backend.api.routes.health.get_llm_service")
    @patch("backend.api.routes.health.get_vector_store")
    @patch("backend.api.routes.health.settings")
    def test_detailed_health_degraded(
        self,
        mock_settings,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
    ):
        """Test detailed health check when some components are unhealthy."""
        mock_settings.ENVIRONMENT = "test"
        mock_settings.VERSION = "1.0.0"
        
        # One component unhealthy
        mock_store = Mock()
        mock_store.health_check.return_value = {"status": "unhealthy"}
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
        
        mock_met = Mock()
        mock_met.get_metrics.return_value = {}
        mock_get_metrics.return_value = mock_met
        
        response = client.get("/health/detailed")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "degraded"
        assert data["all_systems_operational"] is False
    
    @patch("backend.api.routes.health.get_metrics")
    @patch("backend.api.routes.health.get_response_generator")
    @patch("backend.api.routes.health.get_rag_retrieval")
    @patch("backend.api.routes.health.get_llm_service")
    @patch("backend.api.routes.health.get_vector_store")
    @patch("backend.api.routes.health.settings")
    def test_detailed_health_with_exceptions(
        self,
        mock_settings,
        mock_get_store,
        mock_get_llm,
        mock_get_rag,
        mock_get_gen,
        mock_get_metrics,
        client,
    ):
        """Test detailed health check with component exceptions."""
        mock_settings.ENVIRONMENT = "test"
        mock_settings.VERSION = "1.0.0"
        
        # One component raises exception
        mock_get_store.side_effect = Exception("Connection failed")
        mock_get_llm.return_value = Mock(health_check=lambda: {"status": "healthy"})
        mock_get_rag.return_value = Mock(health_check=lambda: {"status": "healthy"})
        mock_get_gen.return_value = Mock(health_check=lambda: {"status": "healthy"})
        mock_get_metrics.return_value = Mock(get_metrics=lambda: {})
        
        response = client.get("/health/detailed")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["vector_store"]["status"] == "unhealthy"
        assert "error" in data["components"]["vector_store"]

