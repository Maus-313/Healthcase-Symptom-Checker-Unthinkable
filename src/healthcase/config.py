"""
Configuration management for Healthcase Symptom Checker.

Centralizes all configuration settings, environment variables, and constants.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the application."""

    # API Configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "deepseek/deepseek-chat-v3.1:free"

    # Application Settings
    APP_NAME: str = "Healthcare Symptom Checker"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # UI Settings
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 850

    # Validation Settings
    MAX_AGE: int = 150
    MIN_AGE: int = 0
    MAX_WEIGHT: float = 500.0
    MIN_WEIGHT: float = 1.0
    MAX_TEMPERATURE: float = 50.0
    MIN_TEMPERATURE: float = 30.0

    # Test Result Ranges (normal values)
    NORMAL_RANGES: Dict[str, Dict[str, float]] = {
        "WBC": {"min": 4000, "max": 11000},
        "Platelets": {"min": 150000, "max": 450000},
        "Hemoglobin": {"min": 12.0, "max": 16.0},  # General, varies by gender
        "Blood_Sugar": {"min": 70, "max": 140},
        "ALT": {"min": 7, "max": 56},
        "Creatinine": {"min": 0.6, "max": 1.2},
    }

    # Security Settings
    MAX_INPUT_LENGTH: int = 1000
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def validate_api_key(cls) -> bool:
        """Validate that the API key is present and properly formatted."""
        if not cls.OPENROUTER_API_KEY:
            return False
        # Basic validation - should start with 'sk-or-v1-'
        return cls.OPENROUTER_API_KEY.startswith("sk-or-v1-")

    @classmethod
    def get_openai_client_config(cls) -> Dict[str, Any]:
        """Get configuration for OpenAI client."""
        if not cls.validate_api_key():
            raise ValueError("Invalid or missing OpenRouter API key")

        return {
            "base_url": cls.OPENROUTER_BASE_URL,
            "api_key": cls.OPENROUTER_API_KEY,
        }

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.DEBUG

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration for API calls."""
        return {
            "model": cls.DEFAULT_MODEL,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
        }


# Global config instance
config = Config()