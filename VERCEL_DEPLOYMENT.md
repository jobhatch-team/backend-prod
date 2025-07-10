# 🚀 Vercel Deployment Guide - Flask Backend

This guide covers deploying the JobHatch Flask backend to Vercel.

## 📋 Prerequisites

- Vercel account (sign up at [vercel.com](https://vercel.com))
- GitHub repository with your Flask backend code
- Python 3.8+ (for local development and testing)

## 🛠️ Pre-Deployment Setup

### 1. Create Vercel Configuration

Create a `vercel.json` file in your `backend-prod` directory:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/__init__.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/__init__.py"
    }
  ],
  "env": {
    "FLASK_APP": "app",
    "FLASK_ENV": "production"
  }
}
```

### 2. Create Requirements File

Ensure your `requirements.txt` is up to date:

```bash
# Generate current requirements
pip freeze > requirements.txt
```

### 3. Create Vercel Entry Point

Create a `api/index.py` file in your `backend-prod` directory:

```python
from app import app

# This is the entry point for Vercel
if __name__ == "__main__":
    app.run()
```

### 4. Update Flask Configuration

Update your `app/config.py` to handle production environment:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Handle both local and production database URLs
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'
```

## 🌐 Deploying to Vercel

### Method 1: Via Vercel Dashboard

1. **Connect GitHub Repository**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `backend-prod` folder as the root directory

2. **Configure Build Settings**
   - Framework Preset: "Other"
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

3. **Set Environment Variables**
   In the Vercel dashboard, add these environment variables:
   ```
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=your-production-database-url
   FLASK_ENV=production
   OPENAI_API_KEY=your-openai-api-key
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_S3_BUCKET=your-s3-bucket-name
   AWS_REGION=us-east-1
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete

### Method 2: Via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Backend Directory**
   ```bash
   cd backend-prod
   vercel --prod
   ```

## 🗄️ Database Setup for Production

### Option 1: PostgreSQL (Recommended)

1. **Create PostgreSQL Database**
   - Use services like [Neon](https://neon.tech/), [Supabase](https://supabase.com/), or [Heroku Postgres](https://www.heroku.com/postgres)
   - Get the connection string

2. **Update Environment Variables**
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

3. **Run Migrations** (One-time setup)
   ```bash
   # Set environment variable locally
   export DATABASE_URL=your-production-database-url
   
   # Run migrations
   flask db upgrade
   ```

### Option 2: SQLite (Development only)

For testing purposes, you can use SQLite, but it's not recommended for production:
```
DATABASE_URL=sqlite:///app.db
```

## ⚙️ Environment Variables Guide

### Required Variables:
```
SECRET_KEY=your-32-character-random-string
DATABASE_URL=your-database-connection-string
FLASK_ENV=production
```

### Optional Variables:
```
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1
```

## 🔍 Testing Your Deployment

1. **Check Deployment Status**
   - Go to your Vercel dashboard
   - Click on your project
   - Check the "Functions" tab for any errors

2. **Test API Endpoints**
   ```bash
   # Test basic endpoint
   curl https://your-vercel-domain.vercel.app/api/docs
   
   # Test specific routes
   curl https://your-vercel-domain.vercel.app/api/users
   ```

3. **Check Logs**
   - In Vercel dashboard, go to "Functions" tab
   - Click on any function to see real-time logs

## 🚨 Common Issues & Solutions

### 1. **Build Fails - Dependencies**
```
Error: No module named 'your-module'
```
**Solution:** Ensure all dependencies are in `requirements.txt`
```bash
pip freeze > requirements.txt
```

### 2. **Database Connection Error**
```
Error: No such table
```
**Solution:** Run database migrations
```bash
flask db upgrade
```

### 3. **Environment Variables Not Loaded**
```
Error: SECRET_KEY not found
```
**Solution:** Check environment variables in Vercel dashboard

### 4. **Function Timeout**
```
Error: Function execution timed out
```
**Solution:** Optimize your code or upgrade Vercel plan

### 5. **CORS Issues**
```
Error: Access to fetch blocked by CORS policy
```
**Solution:** Update CORS configuration in your Flask app:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-frontend-domain.vercel.app'])
```

## 📝 Deployment Checklist

Before deploying, ensure:

- [ ] `vercel.json` is configured correctly
- [ ] `requirements.txt` is up to date
- [ ] `api/index.py` entry point is created
- [ ] All environment variables are set in Vercel
- [ ] Database is set up and accessible
- [ ] CORS is configured for your frontend domain
- [ ] API endpoints are tested locally

## 🔗 Useful Links

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

## 📞 Support

If you encounter issues:
1. Check Vercel function logs
2. Review this guide
3. Check Flask documentation
4. Contact the development team 