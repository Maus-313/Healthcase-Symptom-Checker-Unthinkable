"""
Input validation and sanitization utilities.

Provides functions to validate and sanitize user inputs for security.
"""

import re
from typing import Any, Dict, Optional, Union
from .config import config
from .exceptions import ValidationError, SecurityError
from .logger import get_logger

logger = get_logger(__name__)


class InputValidator:
    """Handles input validation and sanitization."""

    # Regex patterns for validation
    ALPHA_ONLY = re.compile(r'^[a-zA-Z\s]+$')
    ALPHANUMERIC = re.compile(r'^[a-zA-Z0-9\s\-_.]+$')
    NUMERIC = re.compile(r'^\d*\.?\d+$')
    GENDER = re.compile(r'^(M|F|m|f)$', re.IGNORECASE)
    COUGH_TYPE = re.compile(r'^(dry|productive)$', re.IGNORECASE)

    @staticmethod
    def sanitize_string(input_str: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input by removing potentially harmful characters.

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            SecurityError: If input contains suspicious patterns
        """
        if not isinstance(input_str, str):
            raise ValidationError("Input must be a string")

        # Check for suspicious patterns
        suspicious_patterns = [
            r'<[^>]*>',  # HTML tags
            r'javascript:',  # JavaScript injection
            r'on\w+\s*=',  # Event handlers
            r'[\x00-\x1f\x7f-\x9f]',  # Control characters
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                logger.warning(f"Potentially malicious input detected: {input_str[:50]}...")
                raise SecurityError("Invalid input detected")

        # Remove extra whitespace
        sanitized = ' '.join(input_str.split())

        # Apply length limit
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    @staticmethod
    def validate_age(age: Any) -> Optional[int]:
        """
        Validate and convert age input.

        Args:
            age: Age value to validate

        Returns:
            Validated age as integer or None

        Raises:
            ValidationError: If age is invalid
        """
        if age is None or age == "":
            return None

        try:
            age_int = int(float(age))
            if not (config.MIN_AGE <= age_int <= config.MAX_AGE):
                raise ValidationError(f"Age must be between {config.MIN_AGE} and {config.MAX_AGE}")
            return age_int
        except (ValueError, TypeError):
            raise ValidationError("Age must be a valid number")

    @staticmethod
    def validate_weight(weight: Any) -> Optional[float]:
        """
        Validate and convert weight input.

        Args:
            weight: Weight value to validate

        Returns:
            Validated weight as float or None

        Raises:
            ValidationError: If weight is invalid
        """
        if weight is None or weight == "":
            return None

        try:
            weight_float = float(weight)
            if not (config.MIN_WEIGHT <= weight_float <= config.MAX_WEIGHT):
                raise ValidationError(f"Weight must be between {config.MIN_WEIGHT} and {config.MAX_WEIGHT} kg")
            return weight_float
        except (ValueError, TypeError):
            raise ValidationError("Weight must be a valid number")

    @staticmethod
    def validate_temperature(temp: Any) -> Optional[float]:
        """
        Validate and convert temperature input.

        Args:
            temp: Temperature value to validate

        Returns:
            Validated temperature as float or None

        Raises:
            ValidationError: If temperature is invalid
        """
        if temp is None or temp == "":
            return None

        try:
            temp_float = float(temp)
            if not (config.MIN_TEMPERATURE <= temp_float <= config.MAX_TEMPERATURE):
                raise ValidationError(f"Temperature must be between {config.MIN_TEMPERATURE} and {config.MAX_TEMPERATURE}°C")
            return temp_float
        except (ValueError, TypeError):
            raise ValidationError("Temperature must be a valid number")

    @staticmethod
    def validate_gender(gender: Any) -> Optional[str]:
        """
        Validate gender input.

        Args:
            gender: Gender value to validate

        Returns:
            Validated gender as uppercase string or None

        Raises:
            ValidationError: If gender is invalid
        """
        if gender is None or gender == "":
            return None

        gender_str = str(gender).strip().upper()
        if not InputValidator.GENDER.match(gender_str):
            raise ValidationError("Gender must be 'M' or 'F'")

        return gender_str

    @staticmethod
    def validate_duration(duration: Any) -> Optional[str]:
        """
        Validate duration input.

        Args:
            duration: Duration value to validate

        Returns:
            Validated duration string or None

        Raises:
            ValidationError: If duration is invalid
        """
        if duration is None or duration == "":
            return None

        duration_str = InputValidator.sanitize_string(str(duration), 50)

        # Check if it's a valid duration format (e.g., "3 days", "2 weeks", just numbers)
        if not re.match(r'^(\d+\s*(days?|weeks?|months?|hours?)?)$', duration_str, re.IGNORECASE):
            # Allow just numeric input
            if not duration_str.isdigit():
                raise ValidationError("Duration must be a number or include time units (days, weeks, etc.)")

        return duration_str

    @staticmethod
    def validate_cough_type(cough_type: Any) -> Optional[str]:
        """
        Validate cough type input.

        Args:
            cough_type: Cough type value to validate

        Returns:
            Validated cough type as lowercase string or None

        Raises:
            ValidationError: If cough type is invalid
        """
        if cough_type is None or cough_type == "":
            return None

        cough_str = str(cough_type).strip().lower()
        if not InputValidator.COUGH_TYPE.match(cough_str):
            raise ValidationError("Cough type must be 'dry' or 'productive'")

        return cough_str

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """
        Validate and convert boolean input.

        Args:
            value: Value to validate as boolean

        Returns:
            Boolean value

        Raises:
            ValidationError: If value cannot be converted to boolean
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.strip().lower()
            if value in ('y', 'yes', 'true', '1'):
                return True
            elif value in ('n', 'no', 'false', '0'):
                return False

        raise ValidationError("Value must be a valid boolean (y/n, yes/no, true/false, 1/0)")

    @staticmethod
    def validate_test_result(value: Any, test_name: str) -> Optional[Union[float, bool]]:
        """
        Validate test result input.

        Args:
            value: Test result value to validate
            test_name: Name of the test

        Returns:
            Validated test result or None

        Raises:
            ValidationError: If test result is invalid
        """
        if value is None or value == "":
            return None

        # Boolean tests
        if test_name in ["Malaria", "Dengue", "Typhoid"]:
            if isinstance(value, str):
                value = value.strip().lower()
                if value in ("positive", "true", "1", "yes"):
                    return True
                elif value in ("negative", "false", "0", "no"):
                    return False
            elif isinstance(value, bool):
                return value
            raise ValidationError(f"{test_name} must be positive/negative")

        # Numeric tests
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{test_name} must be a valid number")

    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete user data dictionary.

        Args:
            data: User data dictionary to validate

        Returns:
            Validated and sanitized user data

        Raises:
            ValidationError: If any data is invalid
        """
        validated = {}

        # Validate basic info
        basic_info = data.get("basic_info", {})
        validated["basic_info"] = {
            "age": InputValidator.validate_age(basic_info.get("age")),
            "gender": InputValidator.validate_gender(basic_info.get("gender")),
            "weight": InputValidator.validate_weight(basic_info.get("weight")),
            "temperature": InputValidator.validate_temperature(basic_info.get("temperature")),
            "duration": InputValidator.validate_duration(basic_info.get("duration")),
            "chronic_diseases": InputValidator.validate_boolean(basic_info.get("chronic_diseases", False)),
        }

        # Validate symptoms
        symptoms = data.get("symptoms", {})
        validated["symptoms"] = {
            "fever": InputValidator.validate_boolean(symptoms.get("fever", False)),
            "fatigue": InputValidator.validate_boolean(symptoms.get("fatigue", False)),
            "cough": InputValidator.validate_boolean(symptoms.get("cough", False)),
            "headache": InputValidator.validate_boolean(symptoms.get("headache", False)),
            "body_pain": InputValidator.validate_boolean(symptoms.get("body_pain", False)),
            "nausea": InputValidator.validate_boolean(symptoms.get("nausea", False)),
            "vomiting": InputValidator.validate_boolean(symptoms.get("vomiting", False)),
            "diarrhea": InputValidator.validate_boolean(symptoms.get("diarrhea", False)),
            "rash": InputValidator.validate_boolean(symptoms.get("rash", False)),
            "sore_throat": InputValidator.validate_boolean(symptoms.get("sore_throat", False)),
            "shortness_of_breath": InputValidator.validate_boolean(symptoms.get("shortness_of_breath", False)),
            "chest_pain": InputValidator.validate_boolean(symptoms.get("chest_pain", False)),
            "confusion": InputValidator.validate_boolean(symptoms.get("confusion", False)),
            "recent_travel": InputValidator.validate_boolean(symptoms.get("recent_travel", False)),
            "medication": InputValidator.validate_boolean(symptoms.get("medication", False)),
            "appetite_change": InputValidator.validate_boolean(symptoms.get("appetite_change", False)),
            "urine_change": InputValidator.validate_boolean(symptoms.get("urine_change", False)),
            "weight_loss": InputValidator.validate_boolean(symptoms.get("weight_loss", False)),
            "night_sweats": InputValidator.validate_boolean(symptoms.get("night_sweats", False)),
            "exposure": InputValidator.validate_boolean(symptoms.get("exposure", False)),
            "fever_duration": InputValidator.validate_age(symptoms.get("fever_duration")),  # Reuse age validation for positive int
            "cough_type": InputValidator.validate_cough_type(symptoms.get("cough_type")),
        }

        # Validate test results
        test_results = data.get("test_results", {})
        validated["test_results"] = {}
        for test_name in ["WBC", "Platelets", "Hemoglobin", "Blood_Sugar", "ALT", "Creatinine", "Malaria", "Dengue", "Typhoid"]:
            validated["test_results"][test_name] = InputValidator.validate_test_result(
                test_results.get(test_name), test_name
            )

        return validated