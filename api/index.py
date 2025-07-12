from app import app

# This is the entry point for Vercel deployment
# Vercel will use this file to serve the Flask application

# For Vercel serverless functions, we need to export the app
# This allows Vercel to handle the Flask app as a serverless function
handler = app

if __name__ == "__main__":
    app.run(debug=False) 