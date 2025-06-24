from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Profile

profile_routes = Blueprint('profiles', __name__)

@profile_routes.route('/', methods=['POST'])
@login_required
def create_profile():
    existing = Profile.query.filter_by(user_id=current_user.id).first()
    if existing:
        return jsonify({'error': 'Profile already exists'}), 400

    data = request.get_json()
    profile = Profile(user_id=current_user.id)

    for field in [
        'location', 'experience_years', 'preferred_roles', 'open_to_roles', 'bio',
        'github_url', 'portfolio_url', 'linkedin_url', 'twitter_url', 'resume_url',
        'achievements', 'pronouns', 'gender', 'ethnicity'
    ]:
        if field in data:
            setattr(profile, field, data[field])

    db.session.add(profile)
    db.session.commit()
    return jsonify(profile.to_dict()), 201

@profile_routes.route('/', methods=['PUT'])
@login_required
def update_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    data = request.get_json()

    for field in [
        'location', 'experience_years', 'preferred_roles', 'open_to_roles', 'bio',
        'github_url', 'portfolio_url', 'linkedin_url', 'twitter_url', 'resume_url',
        'achievements', 'pronouns', 'gender', 'ethnicity'
    ]:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()
    return jsonify(profile.to_dict()), 200

@profile_routes.route('/me', methods=['GET'])
@login_required
def get_my_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify(profile.to_dict()), 200

@profile_routes.route('/<int:user_id>', methods=['GET'])
def get_profile_by_user_id(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify(profile.to_dict()), 200

@profile_routes.route('/', methods=['DELETE'])
@login_required
def delete_my_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({'message': 'Profile deleted successfully'}), 200

