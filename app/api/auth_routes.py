from flask import Blueprint, request,jsonify
from app.models import User, db
from app.forms import LoginForm
from app.forms import SignUpForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf.csrf import generate_csrf

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/csrf/restore', methods=["GET"])
def restore_csrf():
    csrf_token = generate_csrf()
    response = jsonify({
        'message': 'CSRF token generated',
        'csrf_token': csrf_token  
    })
    return response

@auth_routes.route('/')
def authenticate():
    """
    Authenticates a user.
    """
    if current_user.is_authenticated:
        return current_user.to_dict()
    return {'errors': {'message': 'Unauthorized'}}, 401


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Logs a user in
    """
    try:
        form = LoginForm()
        # Get the csrf_token from the request cookie and put it into the
        # form manually to validate_on_submit can be used
        form['csrf_token'].data = request.cookies.get('csrf_token')
        if form.validate_on_submit():
            # Add the user to the session, we are logged in!
            user = User.query.filter(User.email == form.data['email']).first()
            login_user(user)
            return user.to_dict()
        return form.errors, 401
    except Exception as e:
        print(f"Login error: {str(e)}")  # For debugging
        return {'error': 'Internal server error', 'details': str(e)}, 500


@auth_routes.route('/logout')
def logout():
    """
    Logs a user out
    """
    logout_user()
    return {'message': 'User logged out'}


@auth_routes.route('/signup', methods=['POST'])
def sign_up():
    """
    Creates a new user and logs them in
    """
    try:
        form = SignUpForm()
        form['csrf_token'].data = request.cookies.get('csrf_token')
        if form.validate_on_submit():
            user = User(
                username=form.data['username'],
                email=form.data['email'],
                password=form.data['password']
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return user.to_dict()
        return form.errors, 401
    except Exception as e:
        print(f"Signup error: {str(e)}")  # For debugging
        return {'error': 'Internal server error', 'details': str(e)}, 500


@auth_routes.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """
    Test endpoint to verify API is working
    """
    return {'message': 'API is working', 'method': request.method}, 200


@auth_routes.route('/signup-no-csrf', methods=['POST'])
def sign_up_no_csrf():
    """
    Creates a new user without CSRF validation (for testing)
    """
    try:
        data = request.get_json()
        if not data:
            return {'error': 'No JSON data provided'}, 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {'error': 'Email and password are required'}, 400
            
        # Check if user already exists
        existing_user = User.query.filter(User.email == email).first()
        if existing_user:
            return {'error': 'User with this email already exists'}, 400
            
        user = User(
            username=username,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return user.to_dict()
    except Exception as e:
        print(f"Signup no-csrf error: {str(e)}")
        return {'error': 'Internal server error', 'details': str(e)}, 500


@auth_routes.route('/unauthorized')
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {'errors': {'message': 'Unauthorized'}}, 401