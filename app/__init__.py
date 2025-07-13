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
    'https://frontend-prod-tau.vercel.app',  # Current frontend domain
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
        "version": "3.0"
    })

@app.route("/api/health")
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is working",
        "version": "3.0"
    })

@app.route("/api/test")
def api_test():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "timestamp": "2024-01-01",
        "environment": os.environ.get('FLASK_ENV', 'development')
    })

# Jobs endpoints
@app.route("/api/jobs", methods=['GET', 'POST'])
@app.route("/api/jobs/", methods=['GET', 'POST'])
def jobs():
    """Handle job listings"""
    if request.method == 'GET':
        # Mock job listings
        mock_jobs = [
            {
                "id": 1,
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "salary": "$120,000 - $150,000",
                "type": "Full-time",
                "remote": True,
                "description": "We're looking for a senior software engineer to join our team."
            },
            {
                "id": 2,
                "title": "Product Manager",
                "company": "StartupXYZ",
                "location": "New York, NY",
                "salary": "$100,000 - $130,000",
                "type": "Full-time",
                "remote": False,
                "description": "Lead product development for our mobile app."
            }
        ]
        return jsonify({"jobs": mock_jobs, "total": len(mock_jobs)})
    
    elif request.method == 'POST':
        # Handle job creation
        job_data = request.get_json()
        return jsonify({"message": "Job created successfully", "job": job_data}), 201

@app.route("/api/jobs/<int:job_id>", methods=['GET', 'PUT', 'DELETE'])
def job_detail(job_id):
    """Handle individual job operations"""
    if request.method == 'GET':
        # Mock job detail
        mock_job = {
            "id": job_id,
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "salary": "$120,000 - $150,000",
            "type": "Full-time",
            "remote": True,
            "description": "We're looking for a senior software engineer to join our team.",
            "requirements": ["5+ years experience", "Python/JavaScript", "AWS knowledge"]
        }
        return jsonify(mock_job)
    
    elif request.method == 'PUT':
        # Handle job update
        job_data = request.get_json()
        return jsonify({"message": f"Job {job_id} updated successfully", "job": job_data})
    
    elif request.method == 'DELETE':
        # Handle job deletion
        return jsonify({"message": f"Job {job_id} deleted successfully"})

# Resume endpoints
@app.route("/api/resumes", methods=['GET', 'POST'])
def resumes():
    """Handle resume operations"""
    if request.method == 'GET':
        # Mock resume listings
        mock_resumes = [
            {"id": 1, "filename": "resume_v1.pdf", "uploaded_at": "2024-01-01"},
            {"id": 2, "filename": "resume_v2.pdf", "uploaded_at": "2024-01-02"}
        ]
        return jsonify({"resumes": mock_resumes})
    
    elif request.method == 'POST':
        # Handle resume upload
        return jsonify({"message": "Resume uploaded successfully", "id": 1})

@app.route("/api/resumes/all", methods=['GET'])
def all_resumes():
    """Get all resumes"""
    mock_resumes = [
        {"id": 1, "filename": "resume_v1.pdf", "uploaded_at": "2024-01-01"},
        {"id": 2, "filename": "resume_v2.pdf", "uploaded_at": "2024-01-02"}
    ]
    return jsonify({"resumes": mock_resumes})

@app.route("/api/resumes/<int:resume_id>", methods=['GET', 'PUT', 'DELETE'])
def resume_detail(resume_id):
    """Handle individual resume operations"""
    if request.method == 'GET':
        # Mock resume detail
        mock_resume = {
            "id": resume_id,
            "filename": "resume_v1.pdf",
            "uploaded_at": "2024-01-01",
            "size": "1.2MB",
            "status": "processed"
        }
        return jsonify(mock_resume)
    
    elif request.method == 'PUT':
        # Handle resume update
        resume_data = request.get_json()
        return jsonify({"message": f"Resume {resume_id} updated successfully"})
    
    elif request.method == 'DELETE':
        # Handle resume deletion
        return jsonify({"message": f"Resume {resume_id} deleted successfully"})

@app.route("/api/resumes/<int:resume_id>/analyze", methods=['POST'])
def analyze_resume(resume_id):
    """Analyze a resume"""
    return jsonify({
        "message": f"Resume {resume_id} analyzed successfully",
        "score": 85,
        "recommendations": ["Add more technical skills", "Improve formatting"]
    })

# Cover letter endpoints
@app.route("/api/cover_letters", methods=['GET', 'POST'])
def cover_letters():
    """Handle cover letter operations"""
    if request.method == 'GET':
        mock_cover_letters = [
            {"id": 1, "title": "Cover Letter for Tech Corp", "created_at": "2024-01-01"}
        ]
        return jsonify({"cover_letters": mock_cover_letters})
    
    elif request.method == 'POST':
        # Handle cover letter creation
        return jsonify({"message": "Cover letter created successfully", "id": 1})

# Authentication endpoints
@app.route("/api/auth", methods=['GET', 'POST'])
@app.route("/api/auth/", methods=['GET', 'POST'])
def auth():
    """Handle authentication"""
    if request.method == 'GET':
        return jsonify({"message": "Authentication endpoint", "authenticated": False})
    
    elif request.method == 'POST':
        # Handle authentication
        return jsonify({"message": "Authentication successful", "token": "mock-token"})

@app.route("/api/auth/csrf/restore", methods=['GET'])
def csrf_restore():
    """Restore CSRF token"""
    return jsonify({"csrf_token": "mock-csrf-token"})

@app.route("/api/auth/login", methods=['POST'])
def login():
    """Handle login"""
    user_data = request.get_json()
    return jsonify({
        "message": "Login successful",
        "user": {"id": 1, "email": user_data.get("email", "user@example.com")}
    })

@app.route("/api/auth/signup", methods=['POST'])
def signup():
    """Handle signup"""
    user_data = request.get_json()
    return jsonify({
        "message": "Signup successful",
        "user": {"id": 1, "email": user_data.get("email", "user@example.com")}
    })

@app.route("/api/auth/logout", methods=['POST'])
def logout():
    """Handle logout"""
    return jsonify({"message": "Logout successful"})

@app.route("/api/auth/google", methods=['POST'])
def google_auth():
    """Handle Google authentication"""
    return jsonify({
        "message": "Google authentication successful",
        "user": {"id": 1, "email": "user@gmail.com", "name": "John Doe"}
    })

# Onboarding endpoints
@app.route("/api/onboarding", methods=['GET', 'POST'])
def onboarding():
    """Handle onboarding"""
    if request.method == 'GET':
        return jsonify({"steps": ["user-type", "preferences", "complete"]})
    
    elif request.method == 'POST':
        return jsonify({"message": "Onboarding step completed"})

@app.route("/api/onboarding/user-type", methods=['POST'])
def onboarding_user_type():
    """Handle user type selection"""
    return jsonify({"message": "User type saved"})

@app.route("/api/onboarding/preferences", methods=['POST'])
def onboarding_preferences():
    """Handle preferences setup"""
    return jsonify({"message": "Preferences saved"})

@app.route("/api/onboarding/complete", methods=['POST'])
def onboarding_complete():
    """Complete onboarding"""
    return jsonify({"message": "Onboarding completed successfully"})

# Profile endpoints
@app.route("/api/profiles", methods=['GET', 'POST', 'PUT'])
@app.route("/api/profile", methods=['GET', 'POST', 'PUT'])
def profiles():
    """Handle profile operations"""
    mock_profile = {"id": 1, "name": "John Doe", "email": "john@example.com"}
    return jsonify({"profile": mock_profile})

# AI endpoints
@app.route("/api/ai_resume", methods=['POST'])
def ai_resume():
    """Generate AI resume"""
    return jsonify({"message": "AI resume generated", "content": "Generated resume content"})

@app.route("/api/ai_cover_letter", methods=['POST'])
def ai_cover_letter():
    """Generate AI cover letter"""
    return jsonify({"message": "AI cover letter generated", "content": "Generated cover letter content"})

@app.route("/api/ai", methods=['GET', 'POST'])
@app.route("/api/ai/<path:subpath>", methods=['GET', 'POST'])
def ai_general(subpath=None):
    """Handle AI-related requests"""
    return jsonify({"message": "AI endpoint", "subpath": subpath})

# Waitlist endpoint
@app.route("/api/waitlist", methods=['GET', 'POST', 'OPTIONS'])
def waitlist():
    """Handle waitlist operations"""
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight"})
    
    elif request.method == 'GET':
        return jsonify({"waitlist_count": 100})
    
    elif request.method == 'POST':
        email_data = request.get_json()
        return jsonify({
            "message": "Successfully added to waitlist",
            "email": email_data.get("email")
        })

@app.route("/api/deployment-test", methods=['GET'])
def deployment_test():
    """Test deployment endpoint"""
    return jsonify({
        "message": "Deployment test successful",
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "timestamp": "2024-01-01"
    })

@app.route("/api/docs")
def api_help():
    """API documentation"""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'url': str(rule)
            })
    
    return jsonify({
        "message": "JobHatch API Documentation",
        "version": "3.0",
        "routes": routes
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.before_request
def force_https():
    """Force HTTPS in production"""
    if os.environ.get('FLASK_ENV') == 'production':
        if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
            return redirect(request.url.replace('http://', 'https://'))
