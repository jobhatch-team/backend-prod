from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, User, Profile, UserPreference

profile_routes = Blueprint('profiles', __name__)

@profile_routes.route('', methods=['POST'])
@login_required
def create_or_update_profile():
    """Create or update user profile"""
    try:
        data = request.get_json()
        
        # Get or create profile
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            profile = Profile(user_id=current_user.id)
            db.session.add(profile)
        
        # Update profile fields
        if data.get('location'):
            profile.location = data.get('location')
        if data.get('current_role'):
            # Map current_role to preferred_roles in Profile
            profile.preferred_roles = [data.get('current_role')] if data.get('current_role') else None
        if data.get('years_experience'):
            profile.experience_years = int(data.get('years_experience').split('-')[0]) if '-' in data.get('years_experience') else None
        if data.get('linkedin_url'):
            profile.linkedin_url = data.get('linkedin_url')
        if data.get('website_url'):
            profile.portfolio_url = data.get('website_url')
        if data.get('github_url'):
            profile.github_url = data.get('github_url')
        
        # Handle is_student in UserPreference
        if data.get('is_student') is not None:
            user_preference = UserPreference.query.filter_by(user_id=current_user.id).first()
            if not user_preference:
                user_preference = UserPreference(user_id=current_user.id)
                db.session.add(user_preference)
            # Store student status in job_search_status for now
            user_preference.job_search_status = 'student' if data.get('is_student') else 'professional'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_routes.route('', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    try:
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        user_preference = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        profile_data = {
            'user_id': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
        }
        
        if profile:
            profile_data.update({
                'location': profile.location,
                'current_role': profile.preferred_roles[0] if profile.preferred_roles else None,
                'years_experience': profile.experience_years,
                'linkedin_url': profile.linkedin_url,
                'website_url': profile.portfolio_url,
                'github_url': profile.github_url,
                'bio': profile.bio,
            })
        
        if user_preference:
            profile_data.update({
                'is_student': user_preference.job_search_status == 'student',
                'job_search_status': user_preference.job_search_status,
                'willing_to_mentor': user_preference.willing_to_mentor,
            })
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_routes.route('/', methods=['DELETE'])
@login_required
def delete_my_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({'message': 'Profile deleted successfully'}), 200

