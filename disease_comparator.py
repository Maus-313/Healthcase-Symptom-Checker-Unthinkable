import json
from symptom_checker import get_symptom_analysis

# Predefined diseases with their characteristic symptoms and test results
PREDEFINED_DISEASES = {
    "Viral Fever": {
        "symptoms": {
            "fever": True,
            "fatigue": True,
            "headache": True,
            "body_pain": True,
            "sore_throat": True,
            "appetite_change": True,
            "fever_duration": 3
        },
        "test_results": {
            "WBC": (4000, 11000),  # Normal range
            "Platelets": (150000, 450000),
            "Hemoglobin": (12, 16),
            "Blood_Sugar": (70, 140),
            "ALT": (7, 56),
            "Creatinine": (0.6, 1.2)
        },
        "basic_info": {
            "temperature": (37.5, 39.5),
            "duration": (1, 7)
        }
    },
    "Dengue": {
        "symptoms": {
            "fever": True,
            "fatigue": True,
            "headache": True,
            "body_pain": True,
            "nausea": True,
            "rash": True,
            "recent_travel": True,
            "fever_duration": 5
        },
        "test_results": {
            "WBC": (2000, 5000),  # Low WBC
            "Platelets": (20000, 100000),  # Low platelets
            "Hemoglobin": (10, 14),
            "Blood_Sugar": (70, 140),
            "ALT": (30, 100),  # Elevated
            "Creatinine": (0.6, 1.2),
            "Dengue": True
        },
        "basic_info": {
            "temperature": (38, 40),
            "duration": (3, 10)
        }
    },
    "Typhoid": {
        "symptoms": {
            "fever": True,
            "fatigue": True,
            "headache": True,
            "nausea": True,
            "vomiting": True,
            "diarrhea": True,
            "appetite_change": True,
            "fever_duration": 7
        },
        "test_results": {
            "WBC": (3000, 8000),
            "Platelets": (100000, 300000),
            "Hemoglobin": (10, 14),
            "Blood_Sugar": (70, 140),
            "ALT": (20, 80),
            "Creatinine": (0.6, 1.2),
            "Typhoid": True
        },
        "basic_info": {
            "temperature": (38, 40.5),
            "duration": (5, 14)
        }
    },
    "Malaria": {
        "symptoms": {
            "fever": True,
            "fatigue": True,
            "headache": True,
            "body_pain": True,
            "nausea": True,
            "vomiting": True,
            "recent_travel": True,
            "fever_duration": 4
        },
        "test_results": {
            "WBC": (4000, 12000),
            "Platelets": (50000, 150000),  # Low platelets
            "Hemoglobin": (8, 12),  # Anemia
            "Blood_Sugar": (70, 140),
            "ALT": (20, 60),
            "Creatinine": (0.6, 1.2),
            "Malaria": True
        },
        "basic_info": {
            "temperature": (38, 40),
            "duration": (2, 10)
        }
    },
    "COVID-19": {
        "symptoms": {
            "fever": True,
            "cough": True,
            "fatigue": True,
            "shortness_of_breath": True,
            "sore_throat": True,
            "headache": True,
            "body_pain": True,
            "loss_of_taste_smell": True,
            "fever_duration": 5,
            "cough_type": "dry"
        },
        "test_results": {
            "WBC": (3000, 10000),
            "Platelets": (100000, 400000),
            "Hemoglobin": (11, 15),
            "Blood_Sugar": (70, 140),
            "ALT": (10, 50),
            "Creatinine": (0.6, 1.2)
        },
        "basic_info": {
            "temperature": (37.5, 39),
            "duration": (3, 14)
        }
    }
}

def calculate_symptom_match(user_symptoms, disease_symptoms):
    """Calculate how well user symptoms match a disease's symptoms."""
    matches = 0
    total_checks = 0

    for symptom, expected in disease_symptoms.items():
        if symptom in user_symptoms:
            total_checks += 1
            if user_symptoms[symptom] == expected:
                matches += 1

    return matches / total_checks if total_checks > 0 else 0

def calculate_test_match(user_tests, disease_tests):
    """Calculate how well user test results match a disease's test ranges."""
    matches = 0
    total_checks = 0

    for test, expected_range in disease_tests.items():
        if test in user_tests and user_tests[test] is not None:
            total_checks += 1
            if isinstance(expected_range, tuple):
                if expected_range[0] <= user_tests[test] <= expected_range[1]:
                    matches += 1
            else:
                if user_tests[test] == expected_range:
                    matches += 1

    return matches / total_checks if total_checks > 0 else 0

def calculate_basic_info_match(user_basic, disease_basic):
    """Calculate how well user basic info matches disease characteristics."""
    matches = 0
    total_checks = 0

    for info, expected_range in disease_basic.items():
        if info in user_basic and user_basic[info] is not None:
            total_checks += 1
            if isinstance(expected_range, tuple):
                try:
                    # Convert to float for comparison if needed
                    user_value = float(user_basic[info]) if isinstance(user_basic[info], str) else user_basic[info]
                    if expected_range[0] <= user_value <= expected_range[1]:
                        matches += 1
                except (ValueError, TypeError):
                    # If conversion fails, skip this check
                    total_checks -= 1
            else:
                if user_basic[info] == expected_range:
                    matches += 1

    return matches / total_checks if total_checks > 0 else 0

def compare_with_diseases(user_data):
    """Compare user data with predefined diseases and rank matches."""
    results = []

    for disease_name, disease_data in PREDEFINED_DISEASES.items():
        symptom_match = calculate_symptom_match(user_data["symptoms"], disease_data["symptoms"])
        test_match = calculate_test_match(user_data["test_results"], disease_data["test_results"])
        basic_match = calculate_basic_info_match(user_data["basic_info"], disease_data["basic_info"])

        # Weighted average: symptoms 50%, tests 30%, basic info 20%
        overall_match = (symptom_match * 0.5) + (test_match * 0.3) + (basic_match * 0.2)

        results.append({
            "disease": disease_name,
            "overall_match": overall_match,
            "symptom_match": symptom_match,
            "test_match": test_match,
            "basic_match": basic_match
        })

    # Sort by overall match descending
    results.sort(key=lambda x: x["overall_match"], reverse=True)

    return results

def get_ai_analysis_comparison(user_data, predefined_results):
    """Get AI analysis and compare with predefined disease matching."""
    print("User Data:")
    print(json.dumps(user_data, indent=2))
    print("\n" + "="*50)

    # Get AI analysis
    ai_analysis = get_symptom_analysis(user_data)
    print("AI Analysis:")
    print(ai_analysis)
    print("\n" + "="*50)

    # Compare with predefined diseases
    print("Comparison with Predefined Diseases:")
    for i, result in enumerate(predefined_results[:3], 1):  # Top 3 matches
        print(f"{i}. {result['disease']}: {result['overall_match']:.2%} match")
        print(f"   Symptom match: {result['symptom_match']:.2%}")
        print(f"   Test match: {result['test_match']:.2%}")
        print(f"   Basic info match: {result['basic_match']:.2%}")
        print()

if __name__ == "__main__":
    # Example usage with sample data
    sample_data = {
        "basic_info": {
            "age": 28,
            "gender": "M",
            "weight": 75.0,
            "temperature": 39.0,
            "duration": "4",
            "chronic_diseases": False
        },
        "symptoms": {
            "fever": True,
            "fatigue": True,
            "cough": True,
            "headache": True,
            "body_pain": True,
            "nausea": True,
            "rash": True,
            "recent_travel": True,
            "fever_duration": 4,
            "cough_type": "dry"
        },
        "test_results": {
            "WBC": 3500,
            "Platelets": 90000,
            "Hemoglobin": 11.5,
            "ALT": 55,
            "Dengue": True
        }
    }

    # Compare with predefined diseases
    comparison_results = compare_with_diseases(sample_data)

    # Get AI analysis and show comparison
    get_ai_analysis_comparison(sample_data, comparison_results)