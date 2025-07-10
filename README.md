# Flask Backend

This is the Flask backend for JobHatch, a comprehensive job search and career management platform.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed
- Git installed

### 1. Navigate to Backend Directory
```bash
cd backend-prod
```

### 2. Create & Activate Virtual Environment

**On Windows (PowerShell):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the backend-prod directory with the following variables:

```bash
# Required Environment Variables
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///app.db
FLASK_ENV=development
OPENAI_API_KEY=your-openai-api-key

# Optional: Google OAuth (for authentication)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: AWS (for file uploads)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1
```

### 5. Database Setup
```bash
# Apply database migrations
flask db upgrade
```

### 6. (Optional) Seed Database
```bash
# Add sample data
flask seed all
```

### 7. Start the Server
```bash
# Start development server
flask run
```

The backend will be available at: **http://localhost:8000**

## 📚 API Documentation

Once the server is running, you can view all available API endpoints at:
```
http://localhost:8000/api/docs
```

## 🗂️ API Routes Overview

- **Authentication**: `/api/auth/*`
- **Users**: `/api/users/*`
- **Jobs**: `/api/jobs/*`
- **Resumes**: `/api/resumes/*`
- **Applications**: `/api/applications/*`
- **AI Features**: `/api/ai/*`
- **Companies**: `/api/companies/*`
- **Conversations**: `/api/conversations/*`
- **Messages**: `/api/messages/*`
- **Subscription Plans**: `/api/plans/*`

## 🛠️ Development Tips

### Restarting After Changes
When you make code changes, Flask will automatically reload in debug mode.

### Database Changes
If you modify models, create and apply new migrations:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Deactivating Virtual Environment
```bash
deactivate
```

## 🚨 Troubleshooting

### Common Issues:

1. **Permission Denied Error**
   - Make sure you activated the virtual environment
   - On Windows, you might need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

2. **Module Not Found Error**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

3. **Database Error**
   - Delete `instance/app.db` and run `flask db upgrade` again

4. **Environment Variable Error**
   - Make sure `.env` file exists and has proper encoding (UTF-8)
   - Check that all required variables are set

