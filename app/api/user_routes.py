from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, User

user_routes = Blueprint('users', __name__)


# Get all users (login required)
@user_routes.route('/', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200


# Get a single user by id (login required)
@user_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200


# Update a user (login required, only self)
@user_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get_or_404(id)

    # Only allow user to update their own info
    if current_user.id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    avatar_url = data.get('avatar_url')

    # If username provided and different, check for duplicates
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already in use'}), 400
        user.username = username

    # If email provided and different, check for duplicates
    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = email

    if password:
        user.password = password  # Setter hashes password

    if role is not None:
        user.role = role

    if avatar_url is not None:
        user.avatar_url = avatar_url

    db.session.commit()

    return jsonify(user.to_dict()), 200

# Delete a user (login required, only self)
@user_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)

    if current_user.id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200
