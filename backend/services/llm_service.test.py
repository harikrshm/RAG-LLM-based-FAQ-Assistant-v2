"""
Unit tests for LLM Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from backend.services.llm_service import LLMService, LLMGenerationResult
from backend.exceptions import LLMServiceError


@pytest.fixture
def mock_gemini_client():
    """Create a mock Gemini client."""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Test response from Gemini"
    mock_response.candidates = [Mock()]
    mock_response.candidates[0].content.parts = [Mock(text="Test response from Gemini")]
    mock_response.candidates[0].finish_reason = "STOP"
    mock_response.usage_metadata = Mock()
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 20
    mock_response.usage_metadata.total_token_count = 30
    
    mock_model.generate_content.return_value = mock_response
    return mock_model


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    with patch("backend.services.llm_service.settings") as mock:
        mock.LLM_PROVIDER = "gemini"
        mock.LLM_MODEL = "gemini-pro"
        mock.LLM_TEMPERATURE = 0.1
        mock.LLM_MAX_TOKENS = 500
        mock.LLM_REQUEST_TIMEOUT = 30
        mock.GEMINI_API_KEY = "test-api-key"
        mock.LOCAL_LLM_URL = None
        mock.LOCAL_LLM_API_KEY = None
        yield mock


class TestLLMServiceInitialization:
    """Test LLM service initialization."""
    
    def test_init_with_defaults(self, mock_settings):
        """Test initialization with default settings."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=Mock())
            
            service = LLMService()
            
            assert service.provider == "gemini"
            assert service.model == "gemini-pro"
            assert service.temperature == 0.1
            assert service.max_tokens == 500
    
    def test_init_with_overrides(self, mock_settings):
        """Test initialization with parameter overrides."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=Mock())
            
            service = LLMService(
                provider="gemini",
                model="gemini-ultra",
                temperature=0.5,
                max_tokens=1000,
            )
            
            assert service.provider == "gemini"
            assert service.model == "gemini-ultra"
            assert service.temperature == 0.5
            assert service.max_tokens == 1000
    
    def test_init_gemini_client(self, mock_settings):
        """Test Gemini client initialization."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel = Mock(return_value=mock_model)
            
            service = LLMService(provider="gemini")
            
            mock_genai.configure.assert_called_once_with(api_key="test-api-key")
            assert service._client == mock_model
    
    def test_init_gemini_missing_api_key(self, mock_settings):
        """Test Gemini initialization without API key."""
        mock_settings.GEMINI_API_KEY = ""
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            LLMService(provider="gemini")
    
    def test_init_local_provider(self, mock_settings):
        """Test local provider initialization."""
        mock_settings.LOCAL_LLM_URL = "http://localhost:8000"
        
        service = LLMService(provider="local")
        
        assert service.provider == "local"
        assert service._client is None
    
    def test_init_local_missing_url(self, mock_settings):
        """Test local provider without URL (should warn but not fail)."""
        mock_settings.LOCAL_LLM_URL = None
        
        service = LLMService(provider="local")
        
        assert service.provider == "local"
        # Should not raise, just warn
    
    def test_init_unsupported_provider(self, mock_settings):
        """Test initialization with unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMService(provider="unsupported")


class TestLLMServicePromptBuilding:
    """Test prompt building functionality."""
    
    @pytest.fixture
    def llm_service(self, mock_settings):
        """Create LLM service instance."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=Mock())
            return LLMService()
    
    def test_build_prompt_basic(self, llm_service):
        """Test basic prompt building."""
        prompt = llm_service.build_prompt("What is a mutual fund?")
        
        assert "What is a mutual fund?" in prompt
        assert "User Question:" in prompt
    
    def test_build_prompt_with_context(self, llm_service):
        """Test prompt building with context."""
        prompt = llm_service.build_prompt(
            "What is a mutual fund?",
            context="Mutual funds are investment vehicles..."
        )
        
        assert "Reference Context:" in prompt
        assert "Mutual funds are investment vehicles" in prompt
    
    def test_build_prompt_with_system_prompt(self, llm_service):
        """Test prompt building with system prompt."""
        prompt = llm_service.build_prompt(
            "What is a mutual fund?",
            system_prompt="You are a helpful assistant."
        )
        
        assert "System Instructions:" in prompt
        assert "You are a helpful assistant." in prompt
    
    def test_build_prompt_with_guardrails(self, llm_service):
        """Test prompt building with guardrails."""
        guardrails = [
            "Do not provide investment advice",
            "Only provide factual information",
        ]
        
        prompt = llm_service.build_prompt(
            "What is a mutual fund?",
            guardrails=guardrails,
        )
        
        assert "Guardrails:" in prompt
        assert "Do not provide investment advice" in prompt
        assert "Only provide factual information" in prompt
    
    def test_build_prompt_all_components(self, llm_service):
        """Test prompt building with all components."""
        prompt = llm_service.build_prompt(
            user_query="What is a mutual fund?",
            context="Context here",
            system_prompt="System prompt",
            guardrails=["Guardrail 1", "Guardrail 2"],
        )
        
        assert "System Instructions:" in prompt
        assert "Guardrails:" in prompt
        assert "Reference Context:" in prompt
        assert "User Question:" in prompt
        assert "Response Guidelines:" in prompt


class TestLLMServiceGeneration:
    """Test LLM generation functionality."""
    
    @pytest.fixture
    def gemini_service(self, mock_settings, mock_gemini_client):
        """Create Gemini LLM service."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=mock_gemini_client)
            service = LLMService(provider="gemini")
            service._client = mock_gemini_client
            return service
    
    def test_generate_with_gemini(self, gemini_service, mock_gemini_client):
        """Test generation with Gemini provider."""
        result = gemini_service.generate("What is a mutual fund?")
        
        assert isinstance(result, LLMGenerationResult)
        assert result.provider == "gemini"
        assert result.text == "Test response from Gemini"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_tokens == 30
        mock_gemini_client.generate_content.assert_called_once()
    
    def test_generate_with_context(self, gemini_service, mock_gemini_client):
        """Test generation with context."""
        result = gemini_service.generate(
            "What is a mutual fund?",
            context="Mutual funds are...",
        )
        
        call_args = mock_gemini_client.generate_content.call_args
        prompt = call_args[0][0]
        assert "Mutual funds are" in prompt
    
    def test_generate_with_temperature_override(self, gemini_service, mock_gemini_client):
        """Test generation with temperature override."""
        gemini_service.generate("test", temperature=0.5)
        
        call_args = mock_gemini_client.generate_content.call_args
        config = call_args[1]["generation_config"]
        assert config["temperature"] == 0.5
    
    def test_generate_with_max_tokens_override(self, gemini_service, mock_gemini_client):
        """Test generation with max_tokens override."""
        gemini_service.generate("test", max_tokens=1000)
        
        call_args = mock_gemini_client.generate_content.call_args
        config = call_args[1]["generation_config"]
        assert config["max_output_tokens"] == 1000
    
    def test_generate_gemini_exception(self, gemini_service, mock_gemini_client):
        """Test Gemini generation exception handling."""
        mock_gemini_client.generate_content.side_effect = Exception("API error")
        
        with pytest.raises(Exception):
            gemini_service.generate("test")
    
    def test_generate_gemini_no_client(self, mock_settings):
        """Test generation when Gemini client is not initialized."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=None)
            service = LLMService(provider="gemini")
            service._client = None
        
        with pytest.raises(RuntimeError, match="Gemini client is not initialized"):
            service.generate("test")
    
    @pytest.fixture
    def local_service(self, mock_settings):
        """Create local LLM service."""
        mock_settings.LOCAL_LLM_URL = "http://localhost:8000"
        return LLMService(provider="local")
    
    def test_generate_with_local(self, local_service, mock_settings):
        """Test generation with local provider."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "text": "Local LLM response",
            "model": "local-model",
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15,
            },
        }
        mock_response.raise_for_status = Mock()
        
        with patch("backend.services.llm_service.requests.post", return_value=mock_response):
            result = local_service.generate("test query")
            
            assert isinstance(result, LLMGenerationResult)
            assert result.provider == "local"
            assert result.text == "Local LLM response"
            assert result.prompt_tokens == 5
    
    def test_generate_local_request_exception(self, local_service, mock_settings):
        """Test local generation with request exception."""
        with patch("backend.services.llm_service.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Connection error")
            
            with pytest.raises(requests.RequestException):
                local_service.generate("test")
    
    def test_generate_local_invalid_json(self, local_service, mock_settings):
        """Test local generation with invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Not JSON"
        mock_response.raise_for_status = Mock()
        
        with patch("backend.services.llm_service.requests.post", return_value=mock_response):
            with pytest.raises(ValueError):
                local_service.generate("test")
    
    def test_generate_unsupported_provider(self, mock_settings):
        """Test generation with unsupported provider."""
        service = LLMService(provider="unsupported")
        
        with pytest.raises(NotImplementedError):
            service.generate("test")


class TestLLMServiceAsync:
    """Test async generation."""
    
    @pytest.fixture
    def gemini_service(self, mock_settings, mock_gemini_client):
        """Create Gemini LLM service."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=mock_gemini_client)
            service = LLMService(provider="gemini")
            service._client = mock_gemini_client
            return service
    
    @pytest.mark.asyncio
    async def test_agenerate(self, gemini_service, mock_gemini_client):
        """Test async generation."""
        result = await gemini_service.agenerate("test query")
        
        assert isinstance(result, LLMGenerationResult)
        assert result.provider == "gemini"
        mock_gemini_client.generate_content.assert_called_once()


class TestLLMServiceHealthCheck:
    """Test health check functionality."""
    
    def test_health_check_gemini_healthy(self, mock_settings):
        """Test Gemini health check when healthy."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=Mock())
            service = LLMService(provider="gemini")
            
            health = service.health_check()
            
            assert health["status"] == "healthy"
            assert health["details"]["provider"] == "gemini"
            assert health["details"]["client_initialized"] is True
    
    def test_health_check_gemini_unhealthy(self, mock_settings):
        """Test Gemini health check when unhealthy."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=None)
            service = LLMService(provider="gemini")
            service._client = None
            
            health = service.health_check()
            
            assert health["status"] == "unhealthy"
    
    def test_health_check_local_healthy(self, mock_settings):
        """Test local health check when healthy."""
        mock_settings.LOCAL_LLM_URL = "http://localhost:8000"
        service = LLMService(provider="local")
        
        health = service.health_check()
        
        assert health["status"] == "healthy"
        assert health["details"]["endpoint"] == "http://localhost:8000"
    
    def test_health_check_local_unhealthy(self, mock_settings):
        """Test local health check when unhealthy."""
        mock_settings.LOCAL_LLM_URL = None
        service = LLMService(provider="local")
        
        health = service.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health["details"]


class TestLLMServiceSingleton:
    """Test singleton pattern."""
    
    def test_get_llm_service_singleton(self, mock_settings):
        """Test that get_llm_service returns singleton."""
        with patch("backend.services.llm_service.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock(return_value=Mock())
            
            from backend.services.llm_service import get_llm_service
            
            instance1 = get_llm_service()
            instance2 = get_llm_service()
            
            assert instance1 is instance2

