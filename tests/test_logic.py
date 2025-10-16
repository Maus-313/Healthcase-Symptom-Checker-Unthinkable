"""
Tests for core business logic.
"""

import pytest
from unittest.mock import patch, MagicMock
from healthcase.logic import SymptomAnalyzer, MockAnalyzer
from healthcase.exceptions import EmergencyDetectedError


class TestSymptomAnalyzer:
    """Test symptom analysis logic."""

    def test_check_emergency_no_emergency(self):
        """Test emergency check with normal symptoms."""
        user_data = {
            "symptoms": {
                "fever": True,
                "fatigue": True,
                "headache": True
            },
            "basic_info": {
                "temperature": 38.0
            }
        }

        result = SymptomAnalyzer.check_emergency(user_data)
        assert result.is_emergency is False
        assert result.reasons == []

    def test_check_emergency_high_fever(self):
        """Test emergency check with high fever."""
        user_data = {
            "symptoms": {
                "fever": True
            },
            "basic_info": {
                "temperature": 41.0
            }
        }

        result = SymptomAnalyzer.check_emergency(user_data)
        assert result.is_emergency is True
        assert "High fever (>40°C)" in result.reasons

    def test_check_emergency_fever_with_confusion(self):
        """Test emergency check with fever and confusion."""
        user_data = {
            "symptoms": {
                "fever": True,
                "confusion": True
            },
            "basic_info": {}
        }

        result = SymptomAnalyzer.check_emergency(user_data)
        assert result.is_emergency is True
        assert "Fever with confusion" in result.reasons

    def test_check_emergency_shortness_breath_chest_pain(self):
        """Test emergency check with shortness of breath and chest pain."""
        user_data = {
            "symptoms": {
                "shortness_of_breath": True,
                "chest_pain": True
            },
            "basic_info": {}
        }

        result = SymptomAnalyzer.check_emergency(user_data)
        assert result.is_emergency is True
        assert "Shortness of breath with chest pain" in result.reasons

    @patch('healthcase.logic.llm_service')
    def test_analyze_symptoms_normal(self, mock_llm_service):
        """Test symptom analysis with normal symptoms."""
        mock_llm_service.generate_analysis.return_value = iter(["Analysis result"])

        user_data = {
            "basic_info": {"age": 25},
            "symptoms": {"fever": True},
            "test_results": {}
        }

        result = list(SymptomAnalyzer.analyze_symptoms(user_data))
        assert result == ["Analysis result"]
        mock_llm_service.generate_analysis.assert_called_once()

    def test_analyze_symptoms_emergency(self):
        """Test symptom analysis with emergency symptoms."""
        user_data = {
            "basic_info": {"temperature": 41.0},
            "symptoms": {"fever": True},
            "test_results": {}
        }

        with pytest.raises(EmergencyDetectedError):
            list(SymptomAnalyzer.analyze_symptoms(user_data))

    @patch('healthcase.logic.llm_service')
    def test_analyze_symptoms_with_mock(self, mock_llm_service):
        """Test symptom analysis using mock backend."""
        mock_llm_service.generate_analysis.return_value = iter(["Mock analysis"])

        user_data = {
            "basic_info": {"age": 25},
            "symptoms": {"fever": True},
            "test_results": {}
        }

        result = list(SymptomAnalyzer.analyze_symptoms(user_data, use_mock=True))
        assert result == ["Mock analysis"]
        mock_llm_service.generate_analysis.assert_called_once()


class TestMockAnalyzer:
    """Test mock analyzer functionality."""

    def test_get_mock_analysis_viral_fever(self):
        """Test mock analysis for viral fever symptoms."""
        user_data = {
            "basic_info": {"temperature": 38.5},
            "symptoms": {
                "fever": True,
                "fatigue": True,
                "headache": True
            },
            "test_results": {}
        }

        result = MockAnalyzer.get_mock_analysis(user_data)
        assert "Viral Fever" in result
        assert "75%" in result
        assert "Suggested Actions" in result

    def test_get_mock_analysis_dengue(self):
        """Test mock analysis for dengue symptoms."""
        user_data = {
            "basic_info": {},
            "symptoms": {
                "fever": True,
                "rash": True,
                "recent_travel": True
            },
            "test_results": {
                "Dengue": True,
                "Platelets": 80000
            }
        }

        result = MockAnalyzer.get_mock_analysis(user_data)
        assert "Dengue" in result
        assert "75%" in result

    def test_get_mock_analysis_malaria(self):
        """Test mock analysis for malaria symptoms."""
        user_data = {
            "basic_info": {},
            "symptoms": {
                "fever": True,
                "recent_travel": True
            },
            "test_results": {
                "Malaria": True
            }
        }

        result = MockAnalyzer.get_mock_analysis(user_data)
        assert "Malaria" in result
        assert "70%" in result

    def test_get_mock_analysis_typhoid(self):
        """Test mock analysis for typhoid symptoms."""
        user_data = {
            "basic_info": {},
            "symptoms": {
                "fever": True,
                "nausea": True,
                "diarrhea": True
            },
            "test_results": {
                "Typhoid": True
            }
        }

        result = MockAnalyzer.get_mock_analysis(user_data)
        assert "Typhoid" in result
        assert "65%" in result

    def test_get_mock_analysis_default(self):
        """Test mock analysis for unspecified symptoms."""
        user_data = {
            "basic_info": {},
            "symptoms": {
                "cough": True
            },
            "test_results": {}
        }

        result = MockAnalyzer.get_mock_analysis(user_data)
        assert "Common Cold" in result
        assert "40%" in result