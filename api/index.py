from app import app

# This is the entry point for Vercel deployment
# Vercel will use this file to serve the Flask application

if __name__ == "__main__":
    app.run(debug=False) 