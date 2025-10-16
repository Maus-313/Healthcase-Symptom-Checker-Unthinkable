"""
REST API for Healthcase Symptom Checker.

Provides web API endpoints for symptom analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from typing import Dict, Any
from .logic import SymptomAnalyzer
from .validators import InputValidator
from .exceptions import ValidationError, EmergencyDetectedError, APIError
from .logger import get_logger
from .config import config

logger = get_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limits."""
        current_time = time.time()
        window_start = current_time - config.RATE_LIMIT_WINDOW

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]

        # Check current request count
        current_requests = len(self.requests.get(client_id, []))
        if current_requests >= config.RATE_LIMIT_REQUESTS:
            return False

        # Add current request
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id].append(current_time)

        return True


class SymptomCheckerAPI:
    """Flask-based API for symptom checking."""

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend integration

        self.rate_limiter = RateLimiter()

        # Register routes
        self._register_routes()

        logger.info("Symptom Checker API initialized")

    def _register_routes(self):
        """Register API routes."""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": config.APP_NAME,
                "version": config.VERSION
            })

        @self.app.route('/analyze', methods=['POST'])
        def analyze_symptoms():
            """Analyze symptoms endpoint."""
            try:
                # Rate limiting
                client_id = request.remote_addr or "unknown"
                if not self.rate_limiter.is_allowed(client_id):
                    logger.warning(f"Rate limit exceeded for client: {client_id}")
                    return jsonify({
                        "success": False,
                        "error": "Rate limit exceeded. Please try again later.",
                        "message": "Too many requests"
                    }), 429

                # Get and validate input
                data = request.get_json()
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "No data provided",
                        "message": "Request body is required"
                    }), 400

                # Validate input data
                validated_data = InputValidator.validate_user_data(data)

                # Check for emergency
                emergency = SymptomAnalyzer.check_emergency(validated_data)
                if emergency.is_emergency:
                    return jsonify({
                        "success": False,
                        "error": "Emergency symptoms detected",
                        "message": f"Seek immediate medical attention. Reasons: {', '.join(emergency.reasons)}",
                        "emergency": True,
                        "reasons": emergency.reasons
                    }), 200  # Return 200 but with error flag for emergencies

                # Perform analysis (non-streaming for API)
                analysis_result = ""
                for chunk in SymptomAnalyzer.analyze_symptoms(validated_data):
                    analysis_result += chunk

                logger.info(f"Analysis completed for client: {client_id}")

                return jsonify({
                    "success": True,
                    "data": {
                        "analysis": analysis_result,
                        "disclaimer": "This is for educational purposes only. Consult a healthcare professional for medical advice."
                    },
                    "message": "Analysis completed successfully"
                })

            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "success": False,
                    "error": "Invalid input data",
                    "message": str(e)
                }), 400

            except EmergencyDetectedError as e:
                logger.warning(f"Emergency detected: {e}")
                return jsonify({
                    "success": False,
                    "error": "Emergency symptoms detected",
                    "message": str(e),
                    "emergency": True
                }), 200

            except APIError as e:
                logger.error(f"API error: {e}")
                return jsonify({
                    "success": False,
                    "error": "Service temporarily unavailable",
                    "message": "Please try again later"
                }), 503

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }), 500

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = None):
        """
        Run the Flask application.

        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Debug mode (defaults to config.DEBUG)
        """
        debug = debug if debug is not None else config.is_development()
        logger.info(f"Starting API server on {host}:{port} (debug={debug})")

        self.app.run(host=host, port=port, debug=debug)


# Global API instance
api = SymptomCheckerAPI()


if __name__ == '__main__':
    api.run()