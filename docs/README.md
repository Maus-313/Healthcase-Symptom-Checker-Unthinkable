# Healthcase Documentation

## Overview

Healthcase is an educational symptom checker that uses AI to provide possible disease predictions based on user symptoms and basic health information. **This tool is for educational purposes only and should not be used as a substitute for professional medical advice.**

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **Core Logic** (`logic.py`): Business logic for symptom analysis and emergency detection
- **LLM Interface** (`llm_interface.py`): Abstraction layer for different AI backends
- **Data Models** (`models.py`): Pydantic models for data validation
- **Validators** (`validators.py`): Input validation and sanitization
- **Configuration** (`config.py`): Centralized configuration management
- **Logging** (`logger.py`): Structured logging setup
- **API** (`api.py`): REST API endpoints
- **CLI** (`cli.py`): Command-line interface
- **GUI** (`ui.py`): Tkinter-based graphical interface

## Installation

### From Source

```bash
git clone <repository-url>
cd healthcase
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

```bash
# Run CLI
healthcase-cli

# Or directly
python -m healthcase.cli
```

### Graphical User Interface

```bash
# Run GUI
healthcase-gui

# Or directly
python -m healthcase.ui
```

### REST API

```bash
# Run API server
healthcase-api

# Or directly
python -m healthcase.api
```

API will be available at `http://localhost:5000`

## API Documentation

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Healthcare Symptom Checker",
  "version": "1.0.0"
}
```

#### POST /analyze
Analyze symptoms.

**Request Body:**
```json
{
  "basic_info": {
    "age": 25,
    "gender": "M",
    "weight": 70.0,
    "temperature": 38.5,
    "duration": "3",
    "chronic_diseases": false
  },
  "symptoms": {
    "fever": true,
    "fatigue": true,
    "headache": true,
    "body_pain": true,
    "sore_throat": true,
    "appetite_change": true
  },
  "test_results": {
    "WBC": 6500,
    "Platelets": 180000,
    "Hemoglobin": 14.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis": "Analysis text...",
    "disclaimer": "This is for educational purposes only..."
  }
}
```

## Configuration

The application uses environment variables for configuration:

- `KEY`: OpenRouter API key
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

Create a `.env` file in the project root:

```env
KEY=sk-or-v1-your-api-key-here
DEBUG=false
LOG_LEVEL=INFO
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Building Documentation

```bash
# Generate API docs
sphinx-build docs/ docs/_build/
```

## Security

- All user inputs are validated and sanitized
- Rate limiting is implemented on API endpoints
- Sensitive data is not stored
- HTTPS should be used in production deployments

## License

MIT License - see LICENSE file for details.

## Disclaimer

**IMPORTANT:** This application is for educational purposes only. The analysis provided should not be considered medical advice. Always consult qualified healthcare professionals for medical concerns, diagnosis, or treatment.