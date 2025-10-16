# Healthcare Symptom Checker API

## Description

This API provides educational symptom checking using Large Language Models (LLMs). It accepts user symptoms and returns probable conditions and recommended next steps. **This is for educational purposes only and not a substitute for professional medical advice.**

## Features

- Accepts symptom input via POST request
- Uses deepseek-chat-v3.1:free via OpenRouter for reasoning
- Includes safety disclaimers in responses
- CORS enabled for frontend integration
- Standalone script available for command-line usage

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

6. Install Tkinter on system level:
   
   For Ubuntu: ```sudo apt install python3-tk -y```

   For Windows: ```pip install tk```

   For MacOS: ```brew install python-tk```

## Usage

### Standalone Script Usage

For command-line usage, run the standalone script:
```
python symptom_checker.py
```

Enter your symptoms when prompted, and the script will provide an analysis.

## Safety

- Always consult a healthcare professional for medical advice.
- This tool is not intended for diagnosis or treatment.

## Demo

[Link to demo video]