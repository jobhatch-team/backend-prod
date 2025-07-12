import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure CORS for both development and production
allowed_origins = [
    'http://localhost:5173',  # Vite dev server
    'http://localhost:3000',  # React dev server
]

# Add production frontend domain if specified
if os.environ.get('FRONTEND_URL'):
    allowed_origins.append(os.environ.get('FRONTEND_URL'))

# Add additional production domains from environment
if os.environ.get('ALLOWED_ORIGINS'):
    additional_origins = os.environ.get('ALLOWED_ORIGINS').split(',')
    allowed_origins.extend([origin.strip() for origin in additional_origins])

# Add common Vercel deployment patterns only if no specific domains are set
if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('ALLOWED_ORIGINS'):
    # Default fallback domains - replace with your actual domains
    vercel_domains = [
        'https://jobhatch-frontend.vercel.app',
        'https://jobhatch-prod.vercel.app',
        'https://frontend-prod.vercel.app'
    ]
    allowed_origins.extend(vercel_domains)

CORS(app, supports_credentials=True, origins=allowed_origins)

@app.route("/")
def health_check():
    """
    Health check endpoint for Vercel deployment
    """
    return jsonify({
        "status": "healthy",
        "message": "JobHatch API is running",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "version": "simplified"
    })

@app.route("/api/health")
def api_health():
    """
    API health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "message": "JobHatch API is running",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "version": "simplified"
    })

@app.route("/api/docs")
def api_help():
    """
    Returns basic API information
    """
    return jsonify({
        "message": "JobHatch API - Simplified Version",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Health check"},
            {"path": "/api/health", "method": "GET", "description": "API health check"},
            {"path": "/api/docs", "method": "GET", "description": "API documentation"}
        ]
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
