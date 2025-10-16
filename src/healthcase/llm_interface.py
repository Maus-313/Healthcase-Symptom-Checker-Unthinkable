"""
LLM Interface abstraction for Healthcase Symptom Checker.

Provides a clean interface for different LLM backends with fallback support.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, Optional
from .config import config
from .exceptions import APIError, AuthenticationError, RateLimitError, NetworkError
from .logger import get_logger

logger = get_logger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters

        Yields:
            Chunks of the response as strings

        Raises:
            APIError: If the API call fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the backend is available and properly configured."""
        pass


class OpenRouterBackend(LLMBackend):
    """OpenRouter-based LLM backend."""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client for OpenRouter."""
        try:
            from openai import OpenAI
            client_config = config.get_openai_client_config()
            self.client = OpenAI(**client_config)
            logger.info("OpenRouter backend initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter backend: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if OpenRouter backend is available."""
        return self.client is not None and config.validate_api_key()

    def generate_response(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate response using OpenRouter API.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (model, temperature, etc.)

        Yields:
            Response chunks

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            NetworkError: If network issues occur
            APIError: For other API errors
        """
        if not self.is_available():
            raise APIError("OpenRouter backend is not available")

        # Merge with default model config
        model_config = {**config.get_model_config(), **kwargs}

        try:
            logger.info(f"Sending request to OpenRouter with model: {model_config.get('model')}")

            stream = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for educational symptom checking. Always include a disclaimer that this is not medical advice."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                **model_config
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            self._handle_api_error(e)

    def _handle_api_error(self, error: Exception):
        """Handle different types of API errors."""
        error_msg = str(error).lower()

        if "authentication" in error_msg or "api key" in error_msg:
            raise AuthenticationError(f"Authentication failed: {error}")
        elif "rate limit" in error_msg or "quota" in error_msg:
            raise RateLimitError(f"Rate limit exceeded: {error}")
        elif "network" in error_msg or "connection" in error_msg:
            raise NetworkError(f"Network error: {error}")
        else:
            raise APIError(f"API request failed: {error}")


class MockBackend(LLMBackend):
    """Mock backend for testing and development."""

    def is_available(self) -> bool:
        """Mock backend is always available."""
        return True

    def generate_response(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate mock response for testing.

        Args:
            prompt: The input prompt (ignored)
            **kwargs: Additional parameters (ignored)

        Yields:
            Mock response chunks
        """
        mock_response = """Based on the provided symptoms and test results, here are the top 3 most likely conditions:

1. Viral Fever - 75% confidence
   Reasoning: High fever, fatigue, and headache are classic symptoms of viral infection.

2. Dengue Fever - 60% confidence
   Reasoning: Fever with rash and low platelet count suggests possible dengue.

3. Common Cold - 40% confidence
   Reasoning: Mild respiratory symptoms could indicate a common cold.

**Important Disclaimer:** This analysis is for educational purposes only and should not be used as a substitute for professional medical advice. Please consult a qualified healthcare provider for proper diagnosis and treatment.

Suggested next steps:
- Monitor your temperature regularly
- Stay hydrated and rest
- Consult a doctor if symptoms worsen
- Consider getting additional blood tests if recommended"""

        # Simulate streaming by yielding chunks
        for i in range(0, len(mock_response), 50):
            yield mock_response[i:i+50]


class LLMService:
    """Main LLM service with backend management and fallback support."""

    def __init__(self):
        self.backends = {
            'openrouter': OpenRouterBackend(),
            'mock': MockBackend()
        }
        self.primary_backend = 'openrouter'
        self.fallback_backend = 'mock'

        logger.info("LLM Service initialized with backends: OpenRouter, Mock")

    def generate_analysis(self, user_data: Dict[str, Any], use_mock: bool = False) -> Iterator[str]:
        """
        Generate symptom analysis using available LLM backend.

        Args:
            user_data: User symptom data
            use_mock: Force use of mock backend for testing

        Yields:
            Analysis response chunks

        Raises:
            APIError: If all backends fail
        """
        backend_name = self.fallback_backend if use_mock else self.primary_backend
        backend = self.backends.get(backend_name)

        if not backend or not backend.is_available():
            logger.warning(f"Backend {backend_name} not available, trying fallback")
            backend = self.backends.get(self.fallback_backend)
            if not backend or not backend.is_available():
                raise APIError("No LLM backends available")

        # Format prompt
        prompt = self._format_analysis_prompt(user_data)

        try:
            logger.info(f"Using backend: {backend_name}")
            yield from backend.generate_response(prompt)
        except APIError as e:
            logger.error(f"Backend {backend_name} failed: {e}")
            if backend_name != self.fallback_backend:
                logger.info("Trying fallback backend")
                fallback_backend = self.backends.get(self.fallback_backend)
                if fallback_backend and fallback_backend.is_available():
                    yield from fallback_backend.generate_response(prompt)
                else:
                    raise e
            else:
                raise e

    def _format_analysis_prompt(self, user_data: Dict[str, Any]) -> str:
        """Format user data into analysis prompt."""
        return f"""Based on the following user data, list the top 3 most likely diseases with confidence percentages and reasoning for each. Also suggest next steps.

User Data: {user_data}

Provide response in a clear, structured format with disclaimer that this is educational only."""


# Global LLM service instance
llm_service = LLMService()