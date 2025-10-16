"""
Core business logic for Healthcase Symptom Checker.

Contains symptom analysis, emergency detection, and data processing logic.
"""

from typing import Dict, Any, List, Tuple, Iterator
from .models import UserData, EmergencyAlert, AnalysisResult, DiseasePrediction
from .validators import InputValidator
from .llm_interface import llm_service
from .exceptions import ValidationError, EmergencyDetectedError, DataProcessingError
from .logger import get_logger

logger = get_logger(__name__)


class SymptomAnalyzer:
    """Handles symptom analysis and emergency detection."""

    # Emergency symptom combinations
    EMERGENCY_RULES = [
        {
            "conditions": ["temperature", ">", 40],
            "reason": "High fever (>40°C)"
        },
        {
            "conditions": ["symptoms.confusion", "==", True, "symptoms.fever", "==", True],
            "reason": "Fever with confusion"
        },
        {
            "conditions": ["symptoms.shortness_of_breath", "==", True, "symptoms.chest_pain", "==", True],
            "reason": "Shortness of breath with chest pain"
        }
    ]

    @staticmethod
    def check_emergency(user_data: Dict[str, Any]) -> EmergencyAlert:
        """
        Check for emergency symptoms requiring immediate attention.

        Args:
            user_data: User symptom data

        Returns:
            EmergencyAlert with detection results
        """
        try:
            symptoms = user_data.get("symptoms", {})
            basic_info = user_data.get("basic_info", {})

            emergency_reasons = []

            for rule in SymptomAnalyzer.EMERGENCY_RULES:
                conditions = rule["conditions"]
                reason = rule["reason"]

                if SymptomAnalyzer._evaluate_conditions(conditions, symptoms, basic_info):
                    emergency_reasons.append(reason)

            is_emergency = len(emergency_reasons) > 0

            if is_emergency:
                logger.warning(f"Emergency symptoms detected: {emergency_reasons}")

            return EmergencyAlert(
                is_emergency=is_emergency,
                reasons=emergency_reasons,
                message="Seek immediate medical attention" if is_emergency else ""
            )

        except Exception as e:
            logger.error(f"Error checking emergency symptoms: {e}")
            raise DataProcessingError(f"Failed to check emergency symptoms: {e}")

    @staticmethod
    def _evaluate_conditions(conditions: List, symptoms: Dict, basic_info: Dict) -> bool:
        """Evaluate a list of conditions for emergency detection."""
        i = 0
        while i < len(conditions):
            if i + 2 >= len(conditions):
                break

            field_path = conditions[i]
            operator = conditions[i + 1]
            expected_value = conditions[i + 2]

            # Handle nested fields (e.g., "symptoms.fever")
            if "." in field_path:
                obj_name, field_name = field_path.split(".", 1)
                obj = symptoms if obj_name == "symptoms" else basic_info
                actual_value = obj.get(field_name)
            else:
                actual_value = basic_info.get(field_path)

            if not SymptomAnalyzer._check_condition(actual_value, operator, expected_value):
                return False

            i += 3

        return True

    @staticmethod
    def _check_condition(actual_value, operator: str, expected_value) -> bool:
        """Check a single condition."""
        if operator == "==":
            return actual_value == expected_value
        elif operator == "!=":
            return actual_value != expected_value
        elif operator == ">":
            return actual_value is not None and actual_value > expected_value
        elif operator == "<":
            return actual_value is not None and actual_value < expected_value
        elif operator == ">=":
            return actual_value is not None and actual_value >= expected_value
        elif operator == "<=":
            return actual_value is not None and actual_value <= expected_value
        return False

    @staticmethod
    def analyze_symptoms(user_data: Dict[str, Any], use_mock: bool = False) -> Iterator[str]:
        """
        Analyze user symptoms using LLM.

        Args:
            user_data: Validated user symptom data
            use_mock: Use mock backend for testing

        Yields:
            Analysis response chunks

        Raises:
            EmergencyDetectedError: If emergency symptoms detected
            ValidationError: If data validation fails
        """
        try:
            # Validate input data
            validated_data = InputValidator.validate_user_data(user_data)

            # Check for emergency symptoms
            emergency = SymptomAnalyzer.check_emergency(validated_data)
            if emergency.is_emergency:
                raise EmergencyDetectedError(f"Emergency symptoms detected: {emergency.reasons}")

            # Generate analysis using LLM
            logger.info("Starting symptom analysis")
            yield from llm_service.generate_analysis(validated_data, use_mock=use_mock)

        except EmergencyDetectedError:
            raise  # Re-raise emergency errors
        except ValidationError as e:
            logger.error(f"Data validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Symptom analysis failed: {e}")
            raise DataProcessingError(f"Failed to analyze symptoms: {e}")


class MockAnalyzer:
    """Mock analyzer for testing and fallback scenarios."""

    @staticmethod
    def get_mock_analysis(user_data: Dict[str, Any]) -> str:
        """
        Generate mock analysis based on symptoms and test results.

        Args:
            user_data: User symptom data

        Returns:
            Formatted analysis string
        """
        symptoms = user_data.get("symptoms", {})
        test_results = user_data.get("test_results", {})
        basic_info = user_data.get("basic_info", {})

        # Simple rule-based analysis
        diseases = MockAnalyzer._get_rule_based_predictions(symptoms, test_results, basic_info)

        # Sort by confidence
        diseases.sort(key=lambda x: x[1], reverse=True)

        # Format response
        response = "Top Possible Conditions:\n"
        for i, (disease, confidence, reasoning) in enumerate(diseases[:3], 1):
            response += f"{i}. {disease} – {confidence}%\n"
            response += f"   Reasoning: {reasoning}\n"

        # Add suggestions
        response += "\nSuggested Actions:\n"
        if basic_info.get("temperature", 0) > 39:
            response += "- Monitor temperature closely\n"
        if symptoms.get("fever"):
            response += "- Stay hydrated and rest\n"
        response += "- Consult a healthcare professional for proper diagnosis\n"
        if test_results:
            response += "- Follow up with additional tests if recommended\n"

        return response

    @staticmethod
    def _get_rule_based_predictions(symptoms: Dict, test_results: Dict, basic_info: Dict) -> List[Tuple[str, int, str]]:
        """Get rule-based disease predictions."""
        diseases = []

        # Dengue rules
        if (symptoms.get("fever") and symptoms.get("rash") and symptoms.get("recent_travel") and
            test_results.get("Dengue") and test_results.get("Platelets", 200000) < 100000):
            diseases.append(("Dengue", 75, "High fever, rash, low platelets, positive dengue test"))

        # Viral Fever rules
        if (symptoms.get("fever") and symptoms.get("fatigue") and symptoms.get("headache") and
            not test_results.get("Dengue") and not test_results.get("Malaria")):
            diseases.append(("Viral Fever", 60, "Common flu-like symptoms with normal test results"))

        # Malaria rules
        if (symptoms.get("fever") and symptoms.get("recent_travel") and test_results.get("Malaria")):
            diseases.append(("Malaria", 70, "Fever with travel history and positive malaria test"))

        # Typhoid rules
        if (symptoms.get("fever") and symptoms.get("nausea") and symptoms.get("diarrhea") and
            test_results.get("Typhoid")):
            diseases.append(("Typhoid", 65, "Fever with gastrointestinal symptoms and positive test"))

        # Default fallback
        if not diseases:
            diseases.append(("Common Cold", 40, "Mild symptoms, could be various causes"))

        return diseases