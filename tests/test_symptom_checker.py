import os
import json

try:
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()
except ImportError as e:
    print(f"Error: Required dependencies not installed. {e}")
    print("Please install required dependencies: pip install python-dotenv openai")
    exit(1)

# Import functions from symptom_checker.py
from src.healthcase.symptom_checker import get_symptom_analysis, check_emergency

def simulate_user_input(sample_data):
    """Simulate user input with sample data."""
    basic_info = sample_data["basic_info"]
    symptoms = sample_data["symptoms"]
    test_results = sample_data["test_results"]

    # Compile data
    user_data = {
        "basic_info": basic_info,
        "symptoms": symptoms,
        "test_results": test_results
    }

    # print("Sample User Data:")
    # print(json.dumps(user_data, indent=2))
    # print("\n" + "="*50)

    # Check for emergency
    emergency, reason = check_emergency(symptoms, basic_info)

    if not emergency:
        # Get AI analysis
        analysis = ""
        for chunk in get_symptom_analysis(user_data):
            analysis += chunk
            print(chunk, end="", flush=True)
        print("\n---\nEnd!")
    else:
        print("Emergency detected. Analysis skipped.\n")
        print(f"Reasons: {reason}")

# Sample data for testing
sample_viral_fever = {
    "basic_info": {
        "age": 25,
        "gender": "M",
        "weight": 70.0,
        "temperature": 38.5,
        "duration": "3",
        "chronic_diseases": False
    },
    "symptoms": {
        "fever": True,
        "fatigue": True,
        "cough": False,
        "headache": True,
        "body_pain": True,
        "nausea": False,
        "vomiting": False,
        "diarrhea": False,
        "rash": False,
        "sore_throat": True,
        "shortness_of_breath": False,
        "chest_pain": False,
        "confusion": False,
        "recent_travel": False,
        "medication": False,
        "appetite_change": True,
        "urine_change": False,
        "weight_loss": False,
        "night_sweats": False,
        "exposure": False,
        "fever_duration": 3,
        "cough_type": None
    },
    "test_results": {
        "WBC": 6500,
        "Platelets": 180000,
        "Hemoglobin": 14.0,
        "Blood_Sugar": 90,
        "ALT": 25,
        "Creatinine": 0.8,
        "Malaria": False,
        "Dengue": False,
        "Typhoid": False
    }
}

sample_dengue = {
    "basic_info": {
        "age": 30,
        "gender": "F",
        "weight": 60.0,
        "temperature": 39.2,
        "duration": "5",
        "chronic_diseases": False
    },
    "symptoms": {
        "fever": True,
        "fatigue": True,
        "cough": False,
        "headache": True,
        "body_pain": True,
        "nausea": True,
        "vomiting": False,
        "diarrhea": False,
        "rash": True,
        "sore_throat": False,
        "shortness_of_breath": False,
        "chest_pain": False,
        "confusion": False,
        "recent_travel": True,
        "medication": False,
        "appetite_change": True,
        "urine_change": False,
        "weight_loss": False,
        "night_sweats": False,
        "exposure": False,
        "fever_duration": 5,
        "cough_type": None
    },
    "test_results": {
        "WBC": 3000,
        "Platelets": 80000,
        "Hemoglobin": 12.5,
        "Blood_Sugar": 95,
        "ALT": 45,
        "Creatinine": 0.9,
        "Malaria": False,
        "Dengue": True,
        "Typhoid": False
    }
}

sample_emergency = {
    "basic_info": {
        "age": 45,
        "gender": "M",
        "weight": 80.0,
        "temperature": 40.5,
        "duration": "2",
        "chronic_diseases": True
    },
    "symptoms": {
        "fever": True,
        "fatigue": True,
        "cough": False,
        "headache": True,
        "body_pain": True,
        "nausea": False,
        "vomiting": False,
        "diarrhea": False,
        "rash": False,
        "sore_throat": False,
        "shortness_of_breath": True,
        "chest_pain": True,
        "confusion": True,
        "recent_travel": False,
        "medication": True,
        "appetite_change": False,
        "urine_change": False,
        "weight_loss": False,
        "night_sweats": False,
        "exposure": False,
        "fever_duration": 2,
        "cough_type": None
    },
    "test_results": {}
}

if __name__ == "__main__":
    print("Testing Symptom Checker with Sample Data\n")

    print("Test 1: Viral Fever Case")
    simulate_user_input(sample_viral_fever)

    # print("\n" + "="*80 + "\n")

    # print("Test 2: Dengue Case")
    # simulate_user_input(sample_dengue)

    # print("\n" + "="*80 + "\n")

    # print("Test 3: Emergency Case")
    # simulate_user_input(sample_emergency)