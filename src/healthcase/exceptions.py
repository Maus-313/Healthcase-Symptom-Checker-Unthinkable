"""
Custom exceptions for Healthcase Symptom Checker.

Defines specific exception types for better error handling and debugging.
"""


class HealthcaseError(Exception):
    """Base exception class for Healthcase application."""
    pass


class ConfigurationError(HealthcaseError):
    """Raised when there's a configuration issue."""
    pass


class ValidationError(HealthcaseError):
    """Raised when input validation fails."""
    pass


class APIError(HealthcaseError):
    """Raised when there's an issue with external API calls."""
    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class NetworkError(APIError):
    """Raised when network connectivity issues occur."""
    pass


class EmergencyDetectedError(HealthcaseError):
    """Raised when emergency symptoms are detected."""
    pass


class DataProcessingError(HealthcaseError):
    """Raised when data processing fails."""
    pass


class SecurityError(HealthcaseError):
    """Raised when security violations are detected."""
    pass