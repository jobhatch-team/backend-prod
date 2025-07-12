import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

# This is the entry point for Vercel deployment
# Vercel will use this file to serve the Flask application
application = app

if __name__ == "__main__":
    application.run(debug=False) 