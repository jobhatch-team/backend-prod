import os
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure CORS for both development and production
allowed_origins = [
    'http://localhost:5173',  # Vite dev server
    'http://localhost:3000',  # React dev server
    'https://backend-prod-team-jobhatchs-projects.vercel.app',  # Backend domain
    'https://frontend-prod-team-jobhatchs-projects.vercel.app',  # Frontend team domain
    'https://frontend-prod.vercel.app',  # Alternative frontend domain
    'https://frontend-prod-dun.vercel.app',  # Legacy frontend domain
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

# Basic routes for testing
@app.route("/")
def health_check():
    """Health check endpoint for Vercel deployment"""
    return jsonify({
        "status": "healthy",
        "message": "JobHatch API is running",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "version": "2.0"
    })

@app.route("/api/health")
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "JobHatch API is running",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "version": "2.0"
    })

@app.route("/api/test")
def api_test():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "timestamp": "2024-01-01",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "cors_origins": allowed_origins
    })

# === JOBS ENDPOINTS ===
@app.route("/api/jobs", methods=['GET', 'POST'])
@app.route("/api/jobs/", methods=['GET', 'POST'])
def jobs():
    """Jobs management endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Jobs endpoint working",
            "jobs": [
                {
                    "id": 1,
                    "title": "Frontend Developer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "description": "We are looking for a skilled frontend developer...",
                    "salary": "$80,000 - $120,000",
                    "posted_date": "2024-01-15"
                },
                {
                    "id": 2,
                    "title": "Backend Engineer",
                    "company": "StartupX",
                    "location": "Remote",
                    "description": "Join our backend team to build scalable systems...",
                    "salary": "$90,000 - $130,000",
                    "posted_date": "2024-01-20"
                }
            ],
            "status": "ready for implementation"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Job creation endpoint working",
            "status": "ready for implementation"
        })

@app.route("/api/jobs/<int:job_id>", methods=['GET', 'PUT', 'DELETE'])
def job_detail(job_id):
    """Individual job endpoint"""
    if request.method == 'GET':
        return jsonify({
            "id": job_id,
            "title": "Sample Job",
            "company": "Sample Company",
            "location": "Sample Location",
            "description": "Sample job description",
            "salary": "$50,000 - $80,000",
            "posted_date": "2024-01-15",
            "status": "ready for implementation"
        })
    elif request.method == 'PUT':
        return jsonify({
            "message": f"Job {job_id} update endpoint working",
            "status": "ready for implementation"
        })
    elif request.method == 'DELETE':
        return jsonify({
            "message": f"Job {job_id} deletion endpoint working",
            "status": "ready for implementation"
        })

# === RESUME ENDPOINTS ===
@app.route("/api/resumes", methods=['GET', 'POST'])
def resumes():
    """Resume management endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Resume endpoint working",
            "resumes": [],
            "status": "ready for implementation"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Resume upload endpoint working",
            "resume": {
                "id": 1,
                "filename": "sample_resume.pdf",
                "title": "Sample Resume"
            },
            "storage_type": "local",
            "status": "ready for implementation"
        })

@app.route("/api/resumes/all", methods=['GET'])
def all_resumes():
    """Get all resumes endpoint"""
    return jsonify({
        "message": "All resumes endpoint working",
        "resumes": [],
        "status": "ready for implementation"
    })

@app.route("/api/resumes/<int:resume_id>", methods=['GET', 'PUT', 'DELETE'])
def resume_detail(resume_id):
    """Individual resume endpoint"""
    if request.method == 'GET':
        return jsonify({
            "resume": {
                "id": resume_id,
                "filename": "sample_resume.pdf",
                "title": "Sample Resume"
            },
            "status": "ready for implementation"
        })
    elif request.method == 'PUT':
        return jsonify({
            "message": f"Resume {resume_id} update endpoint working",
            "status": "ready for implementation"
        })
    elif request.method == 'DELETE':
        return jsonify({
            "message": f"Resume {resume_id} deletion endpoint working",
            "status": "ready for implementation"
        })

@app.route("/api/resumes/<int:resume_id>/analyze", methods=['POST'])
def analyze_resume(resume_id):
    """Resume analysis endpoint"""
    return jsonify({
        "message": f"Resume {resume_id} analysis endpoint working",
        "analysis": {
            "score": 85,
            "strengths": ["Strong technical skills", "Good experience"],
            "improvements": ["Add more keywords", "Improve formatting"]
        },
        "job_matches": [],
        "status": "ready for implementation"
    })

# === COVER LETTERS ENDPOINTS ===
@app.route("/api/cover_letters", methods=['GET', 'POST'])
def cover_letters():
    """Cover letter management endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Cover letter endpoint working",
            "cover_letters": [],
            "status": "ready for implementation"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Cover letter creation endpoint working",
            "status": "ready for implementation"
        })

# === AUTH ENDPOINTS ===
@app.route("/api/auth", methods=['GET', 'POST'])
@app.route("/api/auth/", methods=['GET', 'POST'])
def auth():
    """Authentication endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Auth endpoint working",
            "user": None,
            "authenticated": False,
            "status": "ready for implementation"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Auth submission endpoint working",
            "status": "ready for implementation"
        })

@app.route("/api/auth/csrf/restore", methods=['GET'])
def csrf_restore():
    """CSRF token restore endpoint"""
    return jsonify({
        "message": "CSRF restore endpoint working",
        "csrf_token": "sample-csrf-token",
        "status": "ready for implementation"
    })

@app.route("/api/auth/login", methods=['POST'])
def login():
    """Login endpoint"""
    return jsonify({
        "message": "Login endpoint working",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "testuser"
        },
        "status": "ready for implementation"
    })

@app.route("/api/auth/signup", methods=['POST'])
def signup():
    """Signup endpoint"""
    return jsonify({
        "message": "Signup endpoint working",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "testuser"
        },
        "status": "ready for implementation"
    })

@app.route("/api/auth/logout", methods=['POST'])
def logout():
    """Logout endpoint"""
    return jsonify({
        "message": "Logout endpoint working",
        "status": "ready for implementation"
    })

@app.route("/api/auth/google", methods=['POST'])
def google_auth():
    """Google authentication endpoint"""
    return jsonify({
        "message": "Google auth endpoint working",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "testuser"
        },
        "token": "sample-jwt-token",
        "status": "ready for implementation"
    })

# === ONBOARDING ENDPOINTS ===
@app.route("/api/onboarding", methods=['GET', 'POST'])
def onboarding():
    """Onboarding endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Onboarding endpoint working",
            "status": "ready for implementation"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Onboarding submission endpoint working",
            "status": "ready for implementation"
        })

@app.route("/api/onboarding/user-type", methods=['POST'])
def onboarding_user_type():
    """Onboarding user type endpoint"""
    return jsonify({
        "message": "User type saved successfully",
        "status": "ready for implementation"
    })

@app.route("/api/onboarding/preferences", methods=['POST'])
def onboarding_preferences():
    """Onboarding preferences endpoint"""
    return jsonify({
        "message": "Preferences saved successfully",
        "status": "ready for implementation"
    })

@app.route("/api/onboarding/complete", methods=['POST'])
def onboarding_complete():
    """Onboarding completion endpoint"""
    return jsonify({
        "message": "Onboarding completed successfully",
        "redirect_url": "/webapp",
        "status": "ready for implementation"
    })

# === PROFILE ENDPOINTS ===
@app.route("/api/profiles", methods=['GET', 'POST', 'PUT'])
@app.route("/api/profile", methods=['GET', 'POST', 'PUT'])
def profiles():
    """Profile management endpoint"""
    return jsonify({
        "message": "Profile endpoint working",
        "method": request.method,
        "status": "ready for implementation"
    })

# === AI ENDPOINTS ===
@app.route("/api/ai_resume", methods=['POST'])
def ai_resume():
    """AI resume generation endpoint"""
    return jsonify({
        "message": "AI resume endpoint working",
        "status": "ready for implementation"
    })

@app.route("/api/ai_cover_letter", methods=['POST'])
def ai_cover_letter():
    """AI cover letter generation endpoint"""
    return jsonify({
        "message": "AI cover letter endpoint working",
        "status": "ready for implementation"
    })

@app.route("/api/ai", methods=['GET', 'POST'])
@app.route("/api/ai/<path:subpath>", methods=['GET', 'POST'])
def ai_general(subpath=None):
    """General AI endpoint"""
    return jsonify({
        "message": "AI endpoint working",
        "subpath": subpath,
        "method": request.method,
        "status": "ready for implementation"
    })

# === WAITLIST ENDPOINT ===
@app.route("/api/waitlist", methods=['GET', 'POST', 'OPTIONS'])
def waitlist():
    """Waitlist endpoint"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    elif request.method == 'GET':
        return jsonify({
            "message": "Waitlist endpoint working",
            "status": "ready for implementation",
            "timestamp": "2024-01-11T12:00:00Z"
        })
    elif request.method == 'POST':
        return jsonify({
            "message": "Waitlist submission successful",
            "status": "ready for implementation",
            "timestamp": "2024-01-11T12:00:00Z"
        })

# === DEPLOYMENT TEST ENDPOINT ===
@app.route("/api/deployment-test", methods=['GET'])
def deployment_test():
    """Test endpoint to verify latest deployment"""
    return jsonify({
        "message": "Deployment test successful",
        "timestamp": "2024-01-11T12:00:00Z",
        "version": "2.1",
        "status": "latest deployment active"
    })

@app.route("/api/docs")
def api_help():
    """Returns API information and available endpoints"""
    return jsonify({
        "message": "JobHatch API - Working Version",
        "version": "2.0",
        "status": "operational",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Health check"},
            {"path": "/api/health", "method": "GET", "description": "API health check"},
            {"path": "/api/test", "method": "GET", "description": "Test endpoint"},
            {"path": "/api/jobs", "methods": ["GET", "POST"], "description": "Jobs management"},
            {"path": "/api/jobs/{id}", "methods": ["GET", "PUT", "DELETE"], "description": "Individual job"},
            {"path": "/api/resumes", "methods": ["GET", "POST"], "description": "Resume management"},
            {"path": "/api/resumes/all", "methods": ["GET"], "description": "Get all resumes"},
            {"path": "/api/resumes/{id}", "methods": ["GET", "PUT", "DELETE"], "description": "Individual resume"},
            {"path": "/api/resumes/{id}/analyze", "methods": ["POST"], "description": "Resume analysis"},
            {"path": "/api/cover_letters", "methods": ["GET", "POST"], "description": "Cover letter management"},
            {"path": "/api/auth", "methods": ["GET", "POST"], "description": "Authentication"},
            {"path": "/api/auth/csrf/restore", "methods": ["GET"], "description": "CSRF token restore"},
            {"path": "/api/auth/login", "methods": ["POST"], "description": "User login"},
            {"path": "/api/auth/signup", "methods": ["POST"], "description": "User signup"},
            {"path": "/api/auth/logout", "methods": ["POST"], "description": "User logout"},
            {"path": "/api/auth/google", "methods": ["POST"], "description": "Google authentication"},
            {"path": "/api/onboarding", "methods": ["GET", "POST"], "description": "User onboarding"},
            {"path": "/api/onboarding/user-type", "methods": ["POST"], "description": "Save user type"},
            {"path": "/api/onboarding/preferences", "methods": ["POST"], "description": "Save preferences"},
            {"path": "/api/onboarding/complete", "methods": ["POST"], "description": "Complete onboarding"},
            {"path": "/api/profiles", "methods": ["GET", "POST", "PUT"], "description": "Profile management"},
            {"path": "/api/ai_resume", "methods": ["POST"], "description": "AI resume generation"},
            {"path": "/api/ai_cover_letter", "methods": ["POST"], "description": "AI cover letter generation"},
            {"path": "/api/ai", "methods": ["GET", "POST"], "description": "General AI endpoints"},
            {"path": "/api/waitlist", "methods": ["GET", "POST"], "description": "Waitlist management"},
            {"path": "/api/docs", "method": "GET", "description": "API documentation"}
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# Optional: Add HTTPS redirect for production
@app.before_request
def force_https():
    if os.environ.get('FLASK_ENV') == 'production':
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
