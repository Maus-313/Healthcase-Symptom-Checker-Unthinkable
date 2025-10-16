"""
Tests for LLM interface and backends.
"""

import pytest
from unittest.mock import patch, MagicMock
from healthcase.llm_interface import LLMService, OpenRouterBackend, MockBackend
from healthcase.exceptions import APIError, AuthenticationError


class TestOpenRouterBackend:
    """Test OpenRouter backend functionality."""

    def test_is_available_with_valid_key(self):
        """Test backend availability with valid API key."""
        backend = OpenRouterBackend()
        backend.client = MagicMock()  # Mock client as available

        with patch.object(backend, '_initialize_client'):
            backend._initialize_client()
            assert backend.is_available() is True

    def test_is_available_without_client(self):
        """Test backend availability without client."""
        backend = OpenRouterBackend()
        backend.client = None
        assert backend.is_available() is False

    @patch('healthcase.llm_interface.OpenAI')
    def test_generate_response_success(self, mock_openai):
        """Test successful response generation."""
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = "Test response"
        mock_stream.__iter__.return_value = [mock_chunk]
        mock_client.chat.completions.create.return_value = mock_stream

        backend = OpenRouterBackend()
        backend.client = mock_client

        result = list(backend.generate_response("Test prompt"))
        assert result == ["Test response"]

    @patch('healthcase.llm_interface.OpenAI')
    def test_generate_response_api_error(self, mock_openai):
        """Test API error handling."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        backend = OpenRouterBackend()
        backend.client = mock_client

        with pytest.raises(APIError):
            list(backend.generate_response("Test prompt"))


class TestMockBackend:
    """Test mock backend functionality."""

    def test_is_available(self):
        """Test mock backend is always available."""
        backend = MockBackend()
        assert backend.is_available() is True

    def test_generate_response(self):
        """Test mock response generation."""
        backend = MockBackend()
        result = list(backend.generate_response("Test prompt"))
        assert len(result) > 0
        assert "Disclaimer" in "".join(result)


class TestLLMService:
    """Test LLM service functionality."""

    def test_service_initialization(self):
        """Test LLM service initialization."""
        service = LLMService()
        assert 'openrouter' in service.backends
        assert 'mock' in service.backends

    @patch('healthcase.llm_interface.OpenRouterBackend')
    def test_generate_analysis_primary_backend(self, mock_openrouter):
        """Test analysis generation with primary backend."""
        mock_backend = MagicMock()
        mock_backend.is_available.return_value = True
        mock_backend.generate_response.return_value = iter(["Analysis"])
        mock_openrouter.return_value = mock_backend

        service = LLMService()
        service.backends['openrouter'] = mock_backend

        result = list(service.generate_analysis({"test": "data"}))
        assert result == ["Analysis"]

    @patch('healthcase.llm_interface.MockBackend')
    def test_generate_analysis_fallback_backend(self, mock_mock_backend):
        """Test analysis generation with fallback backend."""
        mock_backend = MagicMock()
        mock_backend.is_available.return_value = True
        mock_backend.generate_response.return_value = iter(["Mock Analysis"])
        mock_mock_backend.return_value = mock_backend

        service = LLMService()
        service.backends['mock'] = mock_backend

        result = list(service.generate_analysis({"test": "data"}, use_mock=True))
        assert result == ["Mock Analysis"]

    def test_generate_analysis_no_backends(self):
        """Test analysis generation when no backends available."""
        service = LLMService()
        # Make all backends unavailable
        for backend in service.backends.values():
            backend.is_available.return_value = False

        with pytest.raises(APIError):
            list(service.generate_analysis({"test": "data"}))

    def test_format_analysis_prompt(self):
        """Test prompt formatting."""
        service = LLMService()
        user_data = {
            "basic_info": {"age": 25},
            "symptoms": {"fever": True},
            "test_results": {}
        }

        prompt = service._format_analysis_prompt(user_data)
        assert "Based on the following user data" in prompt
        assert "age" in prompt
        assert "fever" in prompt