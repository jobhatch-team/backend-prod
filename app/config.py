import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkasjdf09ajsdkfljalsiorj12n3490re9485309irefvn,u90818734902139489230'
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLAlchemy 1.4 no longer supports url strings that start with 'postgres'
    # (only 'postgresql') but heroku's postgres add-on automatically sets the
    # url in the hidden config vars to start with postgres.
    # so the connection uri must be updated here (for production)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
    elif database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'  # Default to SQLite for development
    SQLALCHEMY_ECHO = True
