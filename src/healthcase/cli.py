"""
Command Line Interface for Healthcase Symptom Checker.

Provides CLI functionality for symptom analysis.
"""

import argparse
from typing import Dict, Any
from .logic import SymptomAnalyzer, MockAnalyzer
from .validators import InputValidator
from .exceptions import ValidationError, EmergencyDetectedError
from .logger import get_logger
from .config import config

logger = get_logger(__name__)


class SymptomCLI:
    """Command line interface for symptom checking."""

    def __init__(self):
        self.analyzer = SymptomAnalyzer()

    def run(self):
        """Run the CLI application."""
        print(f"Welcome to {config.APP_NAME}")
        print("=" * 50)
        print("Educational Symptom Checker")
        print("NOT for medical diagnosis or treatment")
        print("=" * 50)

        try:
            # Collect user data
            user_data = self._collect_user_data()

            # Validate data
            validated_data = InputValidator.validate_user_data(user_data)

            # Check for emergency
            emergency = self.analyzer.check_emergency(validated_data)
            if emergency.is_emergency:
                print("\n" + "!" * 50)
                print("EMERGENCY ALERT!")
                print("Based on your symptoms, seek immediate medical attention!")
                print(f"Reasons: {', '.join(emergency.reasons)}")
                print("Call emergency services or go to the nearest hospital.")
                print("!" * 50)
                return

            # Perform analysis
            print("\nAnalyzing symptoms...")
            print("-" * 30)

            analysis_result = ""
            try:
                for chunk in self.analyzer.analyze_symptoms(validated_data):
                    print(chunk, end="", flush=True)
                    analysis_result += chunk
                print("\n" + "-" * 30)
                print("Analysis complete.")
            except Exception as e:
                logger.warning(f"LLM analysis failed, using mock analysis: {e}")
                print("Using fallback analysis...")
                analysis_result = MockAnalyzer.get_mock_analysis(validated_data)
                print(analysis_result)

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except ValidationError as e:
            print(f"\nError: Invalid input - {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\nAn unexpected error occurred: {e}")

    def _collect_user_data(self) -> Dict[str, Any]:
        """Collect user data through CLI prompts."""
        print("\nPlease provide the following information:")

        # Basic info
        print("\n--- Basic Information ---")
        basic_info = {}

        basic_info["age"] = self._get_input("Age: ", validator=InputValidator.validate_age)
        basic_info["gender"] = self._get_input("Gender (M/F): ", validator=InputValidator.validate_gender)
        basic_info["weight"] = self._get_input("Weight (kg): ", validator=InputValidator.validate_weight)
        basic_info["temperature"] = self._get_input("Temperature (°C): ", validator=InputValidator.validate_temperature)
        basic_info["duration"] = self._get_input("Duration of symptoms (days): ", validator=InputValidator.validate_duration)
        basic_info["chronic_diseases"] = self._get_yes_no("Any chronic diseases? (y/n): ")

        # Symptoms
        print("\n--- Symptoms ---")
        symptoms = {}

        symptom_list = [
            ("fever", "Do you have fever?"),
            ("fatigue", "Do you have fatigue?"),
            ("cough", "Do you have cough?"),
            ("headache", "Do you have headache?"),
            ("body_pain", "Do you have body pain?"),
            ("nausea", "Do you have nausea?"),
            ("vomiting", "Do you have vomiting?"),
            ("diarrhea", "Do you have diarrhea?"),
            ("rash", "Do you have rash?"),
            ("sore_throat", "Do you have sore throat?"),
            ("shortness_of_breath", "Do you have shortness of breath?"),
            ("chest_pain", "Do you have chest pain?"),
            ("confusion", "Do you have confusion?"),
            ("recent_travel", "Recent travel or mosquito bites?"),
            ("medication", "Any medication taken recently?"),
            ("appetite_change", "Appetite changes?"),
            ("urine_change", "Urine changes?"),
            ("weight_loss", "Weight loss?"),
            ("night_sweats", "Night sweats?"),
            ("exposure", "Recent exposure to someone sick?"),
        ]

        for symptom_key, question in symptom_list:
            symptoms[symptom_key] = self._get_yes_no(f"{question} (y/n): ")

        # Additional symptom details
        if symptoms.get("fever"):
            symptoms["fever_duration"] = self._get_input(
                "Duration of fever (in days): ",
                validator=lambda x: InputValidator.validate_age(x)  # Reuse age validation
            )

        if symptoms.get("cough"):
            symptoms["cough_type"] = self._get_input(
                "Cough type (dry/productive): ",
                validator=InputValidator.validate_cough_type
            )

        # Test results
        print("\n--- Test Results ---")
        test_results = {}

        has_tests = self._get_yes_no("Do you have blood test results? (y/n): ")
        if has_tests:
            test_list = [
                ("WBC", "WBC count: "),
                ("Platelets", "Platelet count: "),
                ("Hemoglobin", "Hemoglobin level: "),
                ("Blood_Sugar", "Blood Sugar level: "),
                ("ALT", "ALT (Liver) level: "),
                ("Creatinine", "Creatinine (Kidney) level: "),
            ]

            for test_key, question in test_list:
                test_results[test_key] = self._get_input(
                    question,
                    validator=lambda x, tk=test_key: InputValidator.validate_test_result(x, tk)
                )

            # Boolean tests
            boolean_tests = [
                ("Malaria", "Malaria test result (positive/negative): "),
                ("Dengue", "Dengue test result (positive/negative): "),
                ("Typhoid", "Typhoid test result (positive/negative): "),
            ]

            for test_key, question in boolean_tests:
                result = self._get_input(question, required=False)
                if result:
                    test_results[test_key] = InputValidator.validate_test_result(result, test_key)

        return {
            "basic_info": basic_info,
            "symptoms": symptoms,
            "test_results": test_results
        }

    def _get_input(self, prompt: str, validator=None, required: bool = False) -> Any:
        """Get validated input from user."""
        while True:
            try:
                value = input(prompt).strip()
                if not value and not required:
                    return None

                if validator:
                    return validator(value)
                return value

            except ValidationError as e:
                print(f"Invalid input: {e}. Please try again.")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error: {e}. Please try again.")

    def _get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user."""
        while True:
            try:
                response = input(prompt).strip().lower()
                return InputValidator.validate_boolean(response)
            except ValidationError:
                print("Please enter 'y' for yes or 'n' for no.")
            except KeyboardInterrupt:
                raise


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description=config.APP_NAME)
    parser.add_argument('--mock', action='store_true', help='Use mock analysis for testing')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Setup logging
    if args.debug:
        from .logger import setup_logging
        setup_logging(level='DEBUG')

    # Run CLI
    cli = SymptomCLI()
    cli.run()


if __name__ == '__main__':
    main()