import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# testing the api
# api_key = os.getenv("OPENROUTER_API_KEY")
# print(api_key)

def get_symptom_analysis(symptoms):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY environment variable not set. Please set your OpenRouter API key in the .env file.\n\nDisclaimer: This is for educational purposes only. Consult a healthcare professional for medical advice."
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Healthcare Symptom Checker"
        }
    )
    
    prompt = f"Based on these symptoms: {symptoms}, suggest possible conditions and next steps with educational disclaimer."
    
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant for educational symptom checking. Always include a disclaimer that this is not medical advice."},
                {
                    "role": "user",
                    "content": prompt
                    }
            ],
            max_tokens=300,
            temperature=0.5
        )
        analysis = response.choices[0].message.content.strip()
    except Exception as e:
        analysis = f"Error querying LLM: {str(e)}. Please try again."
    
    # Add educational disclaimer
    disclaimer = "\n\nDisclaimer: This is for educational purposes only. Consult a healthcare professional for medical advice."
    return analysis + disclaimer

if __name__ == "__main__":
    symptoms = input("Enter your symptoms: ")
    analysis = get_symptom_analysis(symptoms)
    print("\nAnalysis:")
    print(analysis)