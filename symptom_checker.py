import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# testing the api key access
# api_key = os.getenv("KEY")
# print(api_key)


def get_basic_info():
    """Collect basic user information."""
    print("Welcome to the Smart Diagnosis Assistant")
    print("-----------------------------------------")

    try:
        age = int(input("Enter your age: "))
    except ValueError:
        age = None
        print("Invalid age entered. Skipping.")

    gender = input("Gender (M/F): ").strip().upper()
    if gender not in ["M", "F"]:
        gender = None
        print("Invalid gender. Skipping.")

    try:
        weight = float(input("Enter your weight (kg): "))
    except ValueError:
        weight = None
        print("Invalid weight. Skipping.")

    try:
        temperature = float(input("Enter your temperature (°C): "))
    except ValueError:
        temperature = None
        print("Invalid temperature. Skipping.")

    duration = input("Duration of symptoms (in days): ").strip()
    if not duration.isdigit():
        duration = None
        print("Invalid duration. Skipping.")

    chronic_diseases = (
        input("Any chronic diseases (e.g., diabetes, hypertension)? (y/n): ")
        .strip()
        .lower()
    )
    chronic_diseases = chronic_diseases == "y"

    return {
        "age": age,
        "gender": gender,
        "weight": weight,
        "temperature": temperature,
        "duration": duration,
        "chronic_diseases": chronic_diseases,
    }


def get_symptoms():
    """Ask for symptoms with yes/no questions."""
    symptoms = {}
    symptom_questions = {
        "fever": "Do you have fever? (y/n): ",
        "fatigue": "Do you have fatigue? (y/n): ",
        "cough": "Do you have cough? (y/n): ",
        "headache": "Do you have headache? (y/n): ",
        "body_pain": "Do you have body pain? (y/n): ",
        "nausea": "Do you have nausea? (y/n): ",
        "vomiting": "Do you have vomiting? (y/n): ",
        "diarrhea": "Do you have diarrhea? (y/n): ",
        "rash": "Do you have rash? (y/n): ",
        "sore_throat": "Do you have sore throat? (y/n): ",
        "shortness_of_breath": "Do you have shortness of breath? (y/n): ",
        "chest_pain": "Do you have chest pain? (y/n): ",
        "confusion": "Do you have confusion? (y/n): ",
        "recent_travel": "Recent travel or mosquito bites? (y/n): ",
        "medication": "Any medication taken recently? (y/n): ",
        "appetite_change": "Appetite changes? (y/n): ",
        "urine_change": "Urine changes? (y/n): ",
        "weight_loss": "Weight loss? (y/n): ",
        "night_sweats": "Night sweats? (y/n): ",
        "exposure": "Recent exposure to someone sick? (y/n): ",
    }

    for symptom, question in symptom_questions.items():
        answer = input(question).strip().lower()
        symptoms[symptom] = answer == "y"

    # Additional details for some symptoms
    if symptoms.get("fever"):
        try:
            duration_fever = int(input("Duration of fever (in days): "))
            symptoms["fever_duration"] = duration_fever
        except ValueError:
            symptoms["fever_duration"] = None

    if symptoms.get("cough"):
        cough_type = input("Cough type (dry/productive): ").strip().lower()
        symptoms["cough_type"] = (
            cough_type if cough_type in ["dry", "productive"] else None
        )

    return symptoms


def get_test_results():
    """Ask for diagnostic test results."""
    test_results = {}
    has_tests = input("Do you have blood test results? (y/n): ").strip().lower()
    if has_tests != "y":
        return test_results

    test_questions = {
        "WBC": "Enter WBC count: ",
        "Platelets": "Enter Platelet count: ",
        "Hemoglobin": "Enter Hemoglobin level: ",
        "Blood_Sugar": "Enter Blood Sugar level: ",
        "ALT": "Enter ALT (Liver) level: ",
        "Creatinine": "Enter Creatinine (Kidney) level: ",
        "Malaria": "Malaria test result (positive/negative): ",
        "Dengue": "Dengue test result (positive/negative): ",
        "Typhoid": "Typhoid test result (positive/negative): ",
    }

    for test, question in test_questions.items():
        value = input(question).strip()
        if value:
            if test in ["Malaria", "Dengue", "Typhoid"]:
                test_results[test] = value.lower() == "positive"
            else:
                try:
                    test_results[test] = float(value)
                except ValueError:
                    print(f"Invalid value for {test}. Skipping.")
        else:
            test_results[test] = None

    return test_results


def check_emergency(symptoms, basic_info):
    """Check for severe symptoms and alert."""
    severe = False
    reasons = []

    if basic_info.get("temperature") and basic_info["temperature"] > 40:
        severe = True
        reasons.append("High fever (>40°C)")

    if symptoms.get("confusion") and symptoms.get("fever"):
        severe = True
        reasons.append("Fever with confusion")

    if symptoms.get("shortness_of_breath") and symptoms.get("chest_pain"):
        severe = True
        reasons.append("Shortness of breath with chest pain")

    if severe:
        print(
            "\n⚠️ EMERGENCY ALERT: Based on your symptoms, seek immediate medical attention!"
        )
        print("Reasons:", ", ".join(reasons))
        print("Call emergency services or go to the nearest hospital.\n")

    return severe, reasons


def get_symptom_analysis(user_data):
    api_key = os.getenv("KEY")
    if not api_key:
        print("Error: KEY not found. Please install required dependencies and set the environment variable.")
        exit(1)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    prompt = f"""Based on the following user data, list the top 3 most likely diseases with confidence percentages and reasoning for each. Also suggest next steps.

    User Data: {user_data}

    Provide response in a clear, structured format."""

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant for educational symptom checking. Always include a disclaimer that this is not medical advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # max_tokens=300,
            # temperature=0.5,
        )
        analysis = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API response failed: {e}")
        print("Please check your API key and internet connection.")
        exit(1)

    # Add educational disclaimer
    # disclaimer = "\n\nDisclaimer: This is for educational purposes only. Consult a healthcare professional for medical advice."
    # return analysis + disclaimer
    return analysis


def get_mock_analysis(user_data):
    """Generate mock analysis based on symptoms and test results for testing purposes."""
    symptoms = user_data.get("symptoms", {})
    test_results = user_data.get("test_results", {})
    basic_info = user_data.get("basic_info", {})

    # Simple rule-based analysis
    diseases = []

    # Check for Dengue
    if (
        symptoms.get("fever")
        and symptoms.get("rash")
        and symptoms.get("recent_travel")
        and test_results.get("Dengue")
        and test_results.get("Platelets", 200000) < 100000
    ):
        diseases.append(
            ("Dengue", 75, "High fever, rash, low platelets, positive dengue test")
        )

    # Check for Viral Fever
    if (
        symptoms.get("fever")
        and symptoms.get("fatigue")
        and symptoms.get("headache")
        and not test_results.get("Dengue")
        and not test_results.get("Malaria")
    ):
        diseases.append(
            ("Viral Fever", 60, "Common flu-like symptoms with normal test results")
        )

    # Check for Malaria
    if (
        symptoms.get("fever")
        and symptoms.get("recent_travel")
        and test_results.get("Malaria")
    ):
        diseases.append(
            ("Malaria", 70, "Fever with travel history and positive malaria test")
        )

    # Check for Typhoid
    if (
        symptoms.get("fever")
        and symptoms.get("nausea")
        and symptoms.get("diarrhea")
        and test_results.get("Typhoid")
    ):
        diseases.append(
            ("Typhoid", 65, "Fever with gastrointestinal symptoms and positive test")
        )

    # Default fallback
    if not diseases:
        diseases.append(("Common Cold", 40, "Mild symptoms, could be various causes"))

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


if __name__ == "__main__":
    # Step 1: Collect basic information
    basic_info = get_basic_info()

    # Step 2: Ask for symptoms
    symptoms = get_symptoms()

    # Step 3: Ask for test results
    test_results = get_test_results()

    # Step 4: Compile data
    user_data = {
        "basic_info": basic_info,
        "symptoms": symptoms,
        "test_results": test_results,
    }

    # Step 5: Check for emergency
    emergency = check_emergency(symptoms, basic_info)

    if not emergency:
        # Step 6: Get AI analysis
        analysis = get_symptom_analysis(user_data)
        print("\nAnalysis:")
        print(analysis)
    else:
        print(
            "Due to emergency symptoms, analysis skipped. Please seek immediate medical help."
        )
