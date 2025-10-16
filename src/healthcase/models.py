"""
Data models for Healthcase Symptom Checker.

Defines Pydantic models for data validation and serialization.
"""

from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, validator
from .config import config


class BasicInfo(BaseModel):
    """Model for basic user information."""
    age: Optional[int] = Field(None, ge=config.MIN_AGE, le=config.MAX_AGE)
    gender: Optional[str] = Field(None, regex=r"^(M|F)$")
    weight: Optional[float] = Field(None, gt=config.MIN_WEIGHT, le=config.MAX_WEIGHT)
    temperature: Optional[float] = Field(None, ge=config.MIN_TEMPERATURE, le=config.MAX_TEMPERATURE)
    duration: Optional[str] = Field(None, max_length=50)
    chronic_diseases: bool = False

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            return v.upper()
        return v


class Symptoms(BaseModel):
    """Model for user symptoms."""
    fever: bool = False
    fatigue: bool = False
    cough: bool = False
    headache: bool = False
    body_pain: bool = False
    nausea: bool = False
    vomiting: bool = False
    diarrhea: bool = False
    rash: bool = False
    sore_throat: bool = False
    shortness_of_breath: bool = False
    chest_pain: bool = False
    confusion: bool = False
    recent_travel: bool = False
    medication: bool = False
    appetite_change: bool = False
    urine_change: bool = False
    weight_loss: bool = False
    night_sweats: bool = False
    exposure: bool = False

    # Additional symptom details
    fever_duration: Optional[int] = Field(None, ge=0)
    cough_type: Optional[str] = Field(None, regex=r"^(dry|productive)$")


class TestResults(BaseModel):
    """Model for diagnostic test results."""
    WBC: Optional[float] = Field(None, ge=0)
    Platelets: Optional[float] = Field(None, ge=0)
    Hemoglobin: Optional[float] = Field(None, ge=0)
    Blood_Sugar: Optional[float] = Field(None, ge=0)
    ALT: Optional[float] = Field(None, ge=0)
    Creatinine: Optional[float] = Field(None, ge=0)
    Malaria: Optional[bool] = None
    Dengue: Optional[bool] = None
    Typhoid: Optional[bool] = None


class UserData(BaseModel):
    """Complete user data model."""
    basic_info: BasicInfo
    symptoms: Symptoms
    test_results: TestResults


class DiseasePrediction(BaseModel):
    """Model for disease prediction results."""
    disease: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=100)
    reasoning: str = Field(..., min_length=1)


class AnalysisResult(BaseModel):
    """Model for analysis results."""
    predictions: List[DiseasePrediction] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    disclaimer: str = "This is for educational purposes only. Consult a healthcare professional for medical advice."


class EmergencyAlert(BaseModel):
    """Model for emergency alerts."""
    is_emergency: bool = False
    reasons: List[str] = Field(default_factory=list)
    message: str = "Seek immediate medical attention"


class APIResponse(BaseModel):
    """Model for API responses."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None