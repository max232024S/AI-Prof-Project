"""
Flask REST API application for AI-Prof.

This module provides the REST API backend while maintaining
backward compatibility with the CLI interface in main.py.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from api.routes import auth_bp, api_bp
from database.database import db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# Configure file uploads
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB default
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'data/')

# Ensure database is initialized
db.construct_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Payload Too Large errors."""
    max_size = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)  # Convert to MB
    return jsonify({
        'error': 'File too large',
        'message': f'Maximum file size is {max_size:.0f}MB'
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500


# Request logging middleware
@app.before_request
def log_request():
    """Log incoming requests."""
    if app.debug:
        from flask import request
        print(f"[{request.method}] {request.path}")


# Root endpoint
@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'name': 'AI-Prof API',
        'version': '1.0.0',
        'description': 'REST API for AI-powered professor assistant',
        'endpoints': {
            'health': '/api/health',
            'auth': {
                'register': '/api/auth/register',
                'login': '/api/auth/login'
            },
            'api': {
                'chat': '/api/chat',
                'upload': '/api/upload',
                'conversations': '/api/conversations',
                'quiz': '/api/quiz',
                'documents': '/api/documents'
            }
        }
    }), 200


if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')

    print(f"Starting Flask API server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Max upload size: {app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024):.0f}MB")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

    app.run(host=host, port=port, debug=debug)
