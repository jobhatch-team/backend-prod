# JobHatch Backend Setup Guide

This guide will walk you through setting up the JobHatch Flask backend from scratch in a new environment.

## 📋 Prerequisites

- **Python 3.9+** installed on your system
- **Git** (to clone the repository)
- **PowerShell** or **Command Prompt** (Windows) / **Terminal** (macOS/Linux)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd backend-prod
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt):
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install additional required packages
pip install google-auth google-auth-oauthlib python-jose boto3 openai pymupdf
```

### 4. Set Environment Variables

#### Option A: Using .flaskenv file (Recommended)
Create a `.flaskenv` file in the project root:
```bash
FLASK_APP=app
FLASK_DEBUG=true
FLASK_RUN_PORT=8000
SECRET_KEY=your_secret_key_here_at_least_24_characters_long
```

#### Option B: Set in terminal session
```bash
# Windows (PowerShell):
$env:FLASK_APP = "app"
$env:SECRET_KEY = "your_secret_key_here_at_least_24_characters_long"

# Windows (Command Prompt):
set FLASK_APP=app
set SECRET_KEY=your_secret_key_here_at_least_24_characters_long

# macOS/Linux:
export FLASK_APP=app
export SECRET_KEY=your_secret_key_here_at_least_24_characters_long
```

### 5. Initialize Database
```bash
# Run database migrations to create tables
flask db upgrade
```

### 6. Run the Server
```bash
flask run
```

The server will start on `http://127.0.0.1:8000`

## 🔧 Detailed Setup Instructions

### Environment Variables Configuration

The following environment variables are required:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for CSRF protection | **Yes** | None |
| `FLASK_APP` | Flask application entry point | **Yes** | `app` |
| `FLASK_DEBUG` | Enable debug mode | No | `false` |
| `FLASK_RUN_PORT` | Port to run the server | No | `5000` |
| `DATABASE_URL` | Database connection string | No | SQLite (dev.db) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No* | None |
| `JWT_SECRET` | JWT signing secret | No | `dev-secret` |

*Required for Google OAuth functionality

### Database Setup

This project uses **SQLite** for development and **PostgreSQL** for production.

#### Development (SQLite)
The database file (`dev.db`) will be created automatically in the project root when you run migrations.

#### Production (PostgreSQL)
Set the `DATABASE_URL` environment variable:
```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Dependencies Breakdown

#### Core Flask Dependencies (requirements.txt)
- `flask==2.2.2` - Web framework
- `flask-sqlalchemy==3.0.2` - Database ORM
- `flask-migrate==4.0.2` - Database migrations
- `flask-login==0.6.2` - User session management
- `flask-wtf==1.1.1` - Form handling and CSRF protection
- `flask-cors==3.0.10` - Cross-origin resource sharing

#### Additional Required Dependencies
- `google-auth` & `google-auth-oauthlib` - Google OAuth authentication
- `python-jose` - JWT token handling
- `boto3` - AWS S3 integration
- `openai` - AI functionality
- `pymupdf` - PDF processing

## 🧪 Testing the Setup

### 1. Test Basic API
```bash
curl http://127.0.0.1:8000/api/docs
```

### 2. Test Authentication Endpoint
```bash
curl http://127.0.0.1:8000/api/auth/test
```

### 3. Test User Registration (No CSRF)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup-no-csrf \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

Expected response:
```json
{
  "avatar_url": null,
  "created_at": "Mon, 30 Jun 2025 08:37:06 GMT",
  "email": "test@example.com",
  "id": 1,
  "role": null,
  "username": "testuser"
}
```

## 📁 Project Structure

```
backend-prod/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── config.py            # Configuration settings
│   ├── api/                 # API route blueprints
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── user_routes.py   # User management
│   │   ├── job_routes.py    # Job-related endpoints
│   │   └── ...
│   ├── models/              # Database models
│   │   ├── user.py          # User model
│   │   ├── job.py           # Job model
│   │   └── ...
│   └── forms/               # WTForms validation
├── migrations/              # Database migration files
├── venv/                    # Virtual environment (created)
├── requirements.txt         # Python dependencies
├── .flaskenv               # Flask environment variables
└── README.md               # This file
```

## 🚨 Common Issues & Solutions

### Issue 1: "flask: command not found"
**Cause**: Virtual environment not activated or Flask not installed
**Solution**:
```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

# Then run flask commands
flask run
```

### Issue 2: "RuntimeError: A secret key is required to use CSRF"
**Cause**: SECRET_KEY environment variable not set
**Solution**:
```bash
# Set SECRET_KEY in .flaskenv file or environment
$env:SECRET_KEY = "your_secret_key_here"  # PowerShell
export SECRET_KEY="your_secret_key_here"  # bash/zsh
```

### Issue 3: "ModuleNotFoundError: No module named 'google'"
**Cause**: Missing additional dependencies
**Solution**:
```bash
pip install google-auth google-auth-oauthlib python-jose boto3 openai pymupdf
```

### Issue 4: "no such table: users"
**Cause**: Database migrations not run
**Solution**:
```bash
flask db upgrade
```

### Issue 5: Import errors with specific modules
**Common missing packages and solutions**:
```bash
# For Google OAuth
pip install google-auth google-auth-oauthlib

# For JWT handling
pip install python-jose

# For AWS S3
pip install boto3

# For AI functionality
pip install openai

# For PDF processing
pip install pymupdf
```

## 🔗 API Endpoints

### Authentication
- `GET /api/auth/` - Check authentication status
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration (with CSRF)
- `POST /api/auth/signup-no-csrf` - User registration (no CSRF, for testing)
- `POST /api/auth/google` - Google OAuth login
- `GET /api/auth/logout` - User logout
- `GET /api/auth/csrf/restore` - Get CSRF token

### Users & Profiles
- `GET /api/users/` - Get users
- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Create/update profile

### Jobs & Applications
- `GET /api/jobs/` - Get job listings
- `POST /api/applications/` - Submit job application
- `GET /api/companies/` - Get companies

### Resume & AI
- `POST /api/resumes/upload` - Upload resume
- `POST /api/ai/chat` - AI chat
- `POST /api/ai/resumes/<id>/analyze` - Analyze resume

### Documentation
- `GET /api/docs` - List all available endpoints

## 🔒 Security Notes

1. **Never commit** your `.env` file or actual secret keys to version control
2. **Use strong SECRET_KEY** (minimum 24 characters, preferably random)
3. **Enable HTTPS** in production
4. **Set secure cookies** in production environment
5. **Validate all inputs** on both client and server side

## 🚀 Production Deployment

### Environment Variables for Production
```bash
FLASK_ENV=production
SECRET_KEY=your_production_secret_key
DATABASE_URL=postgresql://user:pass@host:port/db
GOOGLE_CLIENT_ID=your_google_client_id
JWT_SECRET=your_jwt_secret
```

### Production Server
Consider using:
- **Gunicorn** as WSGI server
- **Nginx** as reverse proxy
- **PostgreSQL** as database
- **Redis** for caching/sessions

Example Gunicorn command:
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## 📞 Support

If you encounter issues not covered in this guide:

1. Check the **Common Issues** section above
2. Ensure all **dependencies** are installed
3. Verify **environment variables** are set correctly
4. Check **database migrations** are up to date
5. Review **Flask logs** for specific error messages

## 🔄 Development Workflow

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Make code changes

# 3. If models changed, create migration
flask db migrate -m "Description of changes"

# 4. Apply migrations
flask db upgrade

# 5. Run server
flask run

# 6. Test endpoints
curl http://127.0.0.1:8000/api/auth/test
```

---

**Happy coding!** 🚀

