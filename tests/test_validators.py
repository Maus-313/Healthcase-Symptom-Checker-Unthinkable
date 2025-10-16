"""
Tests for input validation and sanitization.
"""

import pytest
from healthcase.validators import InputValidator, ValidationError, SecurityError


class TestInputValidator:
    """Test input validation functionality."""

    def test_sanitize_string_valid(self):
        """Test sanitizing valid strings."""
        result = InputValidator.sanitize_string("Hello World")
        assert result == "Hello World"

    def test_sanitize_string_with_whitespace(self):
        """Test sanitizing strings with extra whitespace."""
        result = InputValidator.sanitize_string("  Hello   World  ")
        assert result == "Hello World"

    def test_sanitize_string_max_length(self):
        """Test sanitizing with max length."""
        long_string = "A" * 200
        result = InputValidator.sanitize_string(long_string, max_length=50)
        assert len(result) == 50
        assert result == "A" * 50

    def test_sanitize_string_security(self):
        """Test sanitizing strings with potential security issues."""
        with pytest.raises(SecurityError):
            InputValidator.sanitize_string("<script>alert('xss')</script>")

    def test_validate_age_valid(self):
        """Test validating valid ages."""
        assert InputValidator.validate_age(25) == 25
        assert InputValidator.validate_age("30") == 30
        assert InputValidator.validate_age(0) == 0
        assert InputValidator.validate_age(150) == 150

    def test_validate_age_invalid(self):
        """Test validating invalid ages."""
        with pytest.raises(ValidationError):
            InputValidator.validate_age(-1)

        with pytest.raises(ValidationError):
            InputValidator.validate_age(151)

        with pytest.raises(ValidationError):
            InputValidator.validate_age("not_a_number")

    def test_validate_age_none(self):
        """Test validating None age."""
        assert InputValidator.validate_age(None) is None
        assert InputValidator.validate_age("") is None

    def test_validate_weight_valid(self):
        """Test validating valid weights."""
        assert InputValidator.validate_weight(70.5) == 70.5
        assert InputValidator.validate_weight("60") == 60.0

    def test_validate_weight_invalid(self):
        """Test validating invalid weights."""
        with pytest.raises(ValidationError):
            InputValidator.validate_weight(0.5)

        with pytest.raises(ValidationError):
            InputValidator.validate_weight(600)

    def test_validate_temperature_valid(self):
        """Test validating valid temperatures."""
        assert InputValidator.validate_temperature(37.5) == 37.5
        assert InputValidator.validate_temperature("36.8") == 36.8

    def test_validate_temperature_invalid(self):
        """Test validating invalid temperatures."""
        with pytest.raises(ValidationError):
            InputValidator.validate_temperature(25.0)

        with pytest.raises(ValidationError):
            InputValidator.validate_temperature(55.0)

    def test_validate_gender_valid(self):
        """Test validating valid genders."""
        assert InputValidator.validate_gender("M") == "M"
        assert InputValidator.validate_gender("F") == "F"
        assert InputValidator.validate_gender("m") == "M"
        assert InputValidator.validate_gender("f") == "F"

    def test_validate_gender_invalid(self):
        """Test validating invalid genders."""
        with pytest.raises(ValidationError):
            InputValidator.validate_gender("X")

        with pytest.raises(ValidationError):
            InputValidator.validate_gender("Male")

    def test_validate_duration_valid(self):
        """Test validating valid durations."""
        assert InputValidator.validate_duration("3 days") == "3 days"
        assert InputValidator.validate_duration("2 weeks") == "2 weeks"
        assert InputValidator.validate_duration("5") == "5"

    def test_validate_duration_invalid(self):
        """Test validating invalid durations."""
        with pytest.raises(ValidationError):
            InputValidator.validate_duration("three days")

    def test_validate_cough_type_valid(self):
        """Test validating valid cough types."""
        assert InputValidator.validate_cough_type("dry") == "dry"
        assert InputValidator.validate_cough_type("productive") == "productive"

    def test_validate_cough_type_invalid(self):
        """Test validating invalid cough types."""
        with pytest.raises(ValidationError):
            InputValidator.validate_cough_type("wet")

    def test_validate_boolean_valid(self):
        """Test validating valid booleans."""
        assert InputValidator.validate_boolean(True) is True
        assert InputValidator.validate_boolean(False) is False
        assert InputValidator.validate_boolean("y") is True
        assert InputValidator.validate_boolean("yes") is True
        assert InputValidator.validate_boolean("n") is False
        assert InputValidator.validate_boolean("no") is False

    def test_validate_boolean_invalid(self):
        """Test validating invalid booleans."""
        with pytest.raises(ValidationError):
            InputValidator.validate_boolean("maybe")

    def test_validate_test_result_numeric(self):
        """Test validating numeric test results."""
        assert InputValidator.validate_test_result(5000, "WBC") == 5000
        assert InputValidator.validate_test_result("120", "Blood_Sugar") == 120

    def test_validate_test_result_boolean(self):
        """Test validating boolean test results."""
        assert InputValidator.validate_test_result(True, "Malaria") is True
        assert InputValidator.validate_test_result("positive", "Dengue") is True
        assert InputValidator.validate_test_result("negative", "Typhoid") is False

    def test_validate_test_result_invalid(self):
        """Test validating invalid test results."""
        with pytest.raises(ValidationError):
            InputValidator.validate_test_result("maybe", "Malaria")

    def test_validate_user_data_valid(self):
        """Test validating complete valid user data."""
        valid_data = {
            "basic_info": {
                "age": 25,
                "gender": "M",
                "weight": 70.0,
                "temperature": 37.5,
                "duration": "3 days",
                "chronic_diseases": False
            },
            "symptoms": {
                "fever": True,
                "fatigue": False,
                "cough": True,
                "cough_type": "dry"
            },
            "test_results": {
                "WBC": 6500,
                "Malaria": False
            }
        }

        result = InputValidator.validate_user_data(valid_data)
        assert result["basic_info"]["age"] == 25
        assert result["symptoms"]["fever"] is True
        assert result["test_results"]["WBC"] == 6500

    def test_validate_user_data_invalid(self):
        """Test validating user data with invalid fields."""
        invalid_data = {
            "basic_info": {
                "age": 200,  # Invalid age
                "gender": "X",  # Invalid gender
            },
            "symptoms": {},
            "test_results": {}
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_user_data(invalid_data)