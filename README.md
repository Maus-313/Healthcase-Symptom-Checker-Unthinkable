# Healthcare Symptom Checker API

## Description

This API provides educational symptom checking using Large Language Models (LLMs). It accepts user symptoms and returns probable conditions and recommended next steps. **This is for educational purposes only and not a substitute for professional medical advice.**

## Features

- Accepts symptom input via POST request
- Uses OpenAI's GPT model for reasoning
- Includes safety disclaimers in responses
- CORS enabled for frontend integration

## Setup

1. Clone the repository.

2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```
   . venv/bin/activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set your OpenRouter API key in the `.env` file:
   Replace `your-openrouter-api-key-here` with your actual OpenRouter API key in the `.env` file.

## Usage

Run the Flask app:
```
python flask_hello_api.py
```

The API will be available at `http://localhost:5000`

### Endpoint

- **POST /check_symptoms**

  Request body:
  ```json
  {
    "symptoms": "headache and fever"
  }
  ```

  Response:
  ```json
  {
    "analysis": "Possible conditions: Migraine or viral infection...\n\nDisclaimer: This is for educational purposes only. Consult a healthcare professional for medical advice."
  }
  ```

## Safety

- Always consult a healthcare professional for medical advice.
- This tool is not intended for diagnosis or treatment.

## License

[Add license if needed]

## Demo

[Link to demo video]