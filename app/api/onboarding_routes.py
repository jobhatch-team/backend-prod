# need double check this
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, User, UserPreference

onboarding = Blueprint('onboarding', __name__)

@onboarding.route('/user-type', methods=['POST'])
@login_required
def update_user_type():
    """Update user type/role during onboarding"""
    try:
        data = request.get_json()
        user_type = data.get('user_type')
        
        if not user_type or user_type not in ['job_seeker', 'founder', 'investor']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Update user role
        current_user.role = user_type
        db.session.commit()
        
        return jsonify({
            'message': 'User type updated successfully',
            'user_type': user_type
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@onboarding.route('/preferences', methods=['POST'])
@login_required
def update_onboarding_preferences():
    """Update user preferences during onboarding"""
    try:
        data = request.get_json()
        interests = data.get('interests', [])
        user_type = data.get('user_type')
        
        # Get or create user preferences
        user_preference = UserPreference.query.filter_by(user_id=current_user.id).first()
        if not user_preference:
            user_preference = UserPreference(user_id=current_user.id)
            db.session.add(user_preference)
        
        # Store interests based on user type
        if user_type == 'job_seeker':
            # For job seekers: "seeking_job", "mentor_others"
            if 'seeking_job' in interests:
                user_preference.job_search_status = 'active'
            if 'mentor_others' in interests:
                user_preference.willing_to_mentor = True
                
        elif user_type == 'founder':
            # For founders: "recruiting", "fundraising"
            user_preference.founder_interests = ','.join(interests)
            
        elif user_type == 'investor':
            # For investors: "find_startups", "join_program"
            user_preference.investor_interests = ','.join(interests)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'interests': interests
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@onboarding.route('/status', methods=['GET'])
@login_required
def get_onboarding_status():
    """Get current user's onboarding status"""
    try:
        user_preference = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        return jsonify({
            'user_type': current_user.role,
            'has_preferences': user_preference is not None,
            'onboarding_completed': current_user.role is not None and user_preference is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onboarding.route('/complete', methods=['POST'])
@login_required
def complete_onboarding():
    """Mark onboarding as completed"""
    try:
        # You can add a field to track onboarding completion if needed
        # For now, we'll just return success if user has role and preferences
        user_preference = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        if not current_user.role or not user_preference:
            return jsonify({'error': 'Onboarding not complete'}), 400
        
        return jsonify({
            'message': 'Onboarding completed successfully',
            'redirect_url': '/webapp'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 