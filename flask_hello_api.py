from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from symptom_checker import get_symptom_analysis

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def hello():
    return 'helloword'

@app.route('/apple')
def apple():
    return 'apple'

@app.route('/check_symptoms', methods=['POST'])
def check_symptoms():
    data = request.get_json()
    symptoms = data.get('symptoms', '')
    if not symptoms:
        return jsonify({'error': 'Symptoms are required'}), 400
    analysis = get_symptom_analysis(symptoms)
    return jsonify({'analysis': analysis})

if __name__ == '__main__':
    app.run(debug=True)