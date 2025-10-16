"""
Tests for configuration management.
"""

import os
from unittest.mock import patch
from healthcase.config import Config, config


class TestConfig:
    """Test configuration functionality."""

    def test_config_defaults(self):
        """Test default configuration values."""
        assert config.APP_NAME == "Healthcare Symptom Checker"
        assert config.VERSION == "1.0.0"
        assert config.DEBUG is False
        assert config.MAX_AGE == 150
        assert config.MIN_AGE == 0

    def test_config_validation_ranges(self):
        """Test configuration validation ranges."""
        assert config.NORMAL_RANGES["WBC"]["min"] == 4000
        assert config.NORMAL_RANGES["WBC"]["max"] == 11000
        assert config.NORMAL_RANGES["Hemoglobin"]["min"] == 12.0
        assert config.NORMAL_RANGES["Hemoglobin"]["max"] == 16.0

    @patch.dict(os.environ, {"KEY": "sk-or-v1-test-key"})
    def test_validate_api_key_valid(self):
        """Test API key validation with valid key."""
        test_config = Config()
        test_config.OPENROUTER_API_KEY = "sk-or-v1-test-key"
        assert test_config.validate_api_key() is True

    def test_validate_api_key_invalid(self):
        """Test API key validation with invalid key."""
        test_config = Config()
        test_config.OPENROUTER_API_KEY = "invalid-key"
        assert test_config.validate_api_key() is False

    def test_validate_api_key_missing(self):
        """Test API key validation with missing key."""
        test_config = Config()
        test_config.OPENROUTER_API_KEY = None
        assert test_config.validate_api_key() is False

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_is_development_true(self):
        """Test development mode detection."""
        test_config = Config()
        test_config.DEBUG = True
        assert test_config.is_development() is True

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_is_development_false(self):
        """Test production mode detection."""
        test_config = Config()
        test_config.DEBUG = False
        assert test_config.is_development() is False

    def test_get_openai_client_config(self):
        """Test OpenAI client configuration generation."""
        test_config = Config()
        test_config.OPENROUTER_API_KEY = "sk-or-v1-test-key"

        client_config = test_config.get_openai_client_config()
        assert client_config["api_key"] == "sk-or-v1-test-key"
        assert client_config["base_url"] == "https://openrouter.ai/api/v1"

    def test_get_openai_client_config_invalid_key(self):
        """Test OpenAI client configuration with invalid key."""
        test_config = Config()
        test_config.OPENROUTER_API_KEY = None

        with pytest.raises(ValueError):
            test_config.get_openai_client_config()

    def test_get_model_config(self):
        """Test model configuration generation."""
        test_config = Config()
        model_config = test_config.get_model_config()

        assert model_config["model"] == "deepseek/deepseek-chat-v3.1:free"
        assert model_config["temperature"] == 0.7
        assert model_config["max_tokens"] == 2000
        assert model_config["stream"] is True