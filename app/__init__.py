import os
from flask import Flask, render_template, request, session, redirect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager
from .models import db, User
from .api.user_routes import user_routes
from .api.auth_routes import auth_routes
from .api.google_auth import google_auth_routes
from .api.education_experience_routes import education_routes
from .api.job_routes import job_routes
from .api.profile_routes import profile_routes
from .api.work_experience_routes import work_routes
from .api.resume_upload_aws_routes import resume_routes
from .api.cover_letter_aws_routes import cover_letter_routes
from .api.ai_resume_routes import ai_resume_routes
from .api.ai_cover_letter_routes import ai_cover_letter_routes
from .api.application_routes import application_routes
from .api.company_routes import company_routes
from .api.conversation_routes import conversation_routes
from .api.message_routes import message_routes
from .api.subscription_plans_routes import subscriptions_plans_routes
# from .api.user_subscriptions_routes import user_subscriptions_routes
from .api.onboarding_routes import onboarding

from .seeds import seed_commands
from .config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,)

# Setup login manager
login = LoginManager(app)
login.login_view = 'auth.unauthorized'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Tell flask about our seed commands
app.cli.add_command(seed_commands)

app.config.from_object(Config)
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(google_auth_routes,url_prefix='/api/auth')
app.register_blueprint(education_routes,url_prefix='/api/educations')
app.register_blueprint(job_routes,url_prefix='/api/jobs')
app.register_blueprint(profile_routes,url_prefix='/api/profile')
app.register_blueprint(work_routes,url_prefix='/api/works')
app.register_blueprint(resume_routes,url_prefix='/api/resumes')
app.register_blueprint(cover_letter_routes,url_prefix='/api/cover_letters')
app.register_blueprint(ai_resume_routes,url_prefix='/api/ai_resume')
app.register_blueprint(ai_cover_letter_routes,url_prefix='/api/ai_cover_letter')
app.register_blueprint(company_routes,url_prefix='/api/companies')
app.register_blueprint(application_routes,url_prefix='/api/applications')
app.register_blueprint(message_routes,url_prefix='/api/messages')
app.register_blueprint(conversation_routes, url_prefix='/api/conversations')
app.register_blueprint(subscriptions_plans_routes,url_prefix='/api/plans')
# app.register_blueprint(user_subscriptions_routes,url_prefix='/api/user-plans')
app.register_blueprint(onboarding,url_prefix='/api/onboarding')


db.init_app(app)
Migrate(app, db)

# Application Security
# CORS(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://myapp.example.com"])



# Since we are deploying with Docker and Flask,
# we won't be using a buildpack when we deploy to Heroku.
# Therefore, we need to make sure that in production any
# request made over http is redirected to https.
# Well.........
@app.before_request
def https_redirect():
    if os.environ.get('FLASK_ENV') == 'production':
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)


@app.after_request
def inject_csrf_token(response):
    response.set_cookie(
        'csrf_token',
        generate_csrf(),
        secure=True if os.environ.get('FLASK_ENV') == 'production' else False,
        samesite='Strict' if os.environ.get(
            'FLASK_ENV') == 'production' else None,
        httponly=True)
    return response


@app.route("/api/docs")
def api_help():
    """
    Returns all API routes and their doc strings
    """
    acceptable_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    route_list = { rule.rule: [[ method for method in rule.methods if method in acceptable_methods ],
                    app.view_functions[rule.endpoint].__doc__ ]
                    for rule in app.url_map.iter_rules() if rule.endpoint != 'static' }
    return route_list




@app.errorhandler(404)
def not_found(e):
    return 'Not Found', 404
