import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app import app
    application = app
except Exception as e:
    # If the main app fails, create a minimal Flask app
    from flask import Flask, jsonify
    
    minimal_app = Flask(__name__)
    
    @minimal_app.route('/')
    def health():
        return jsonify({
            "status": "healthy",
            "message": "Minimal JobHatch API is running",
            "error": str(e) if e else None
        })
    
    @minimal_app.route('/api/health')
    def api_health():
        return jsonify({
            "status": "healthy", 
            "message": "Minimal JobHatch API is running",
            "error": str(e) if e else None
        })
    
    application = minimal_app

if __name__ == "__main__":
    application.run(debug=False) 