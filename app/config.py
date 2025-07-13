import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-vercel')
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Handle database URL for both development and production
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # SQLAlchemy 1.4 no longer supports url strings that start with 'postgres'
        # (only 'postgresql') but heroku's postgres add-on automatically sets the
        # url in the hidden config vars to start with postgres.
        # so the connection uri must be updated here (for production)
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
    else:
        # Use SQLite for local development and Vercel deployments without DATABASE_URL
        SQLALCHEMY_DATABASE_URI = 'sqlite:///jobhatch.db'
    
    SQLALCHEMY_ECHO = True
