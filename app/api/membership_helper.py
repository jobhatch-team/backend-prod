from functools import wraps
from flask import jsonify
from flask_login import current_user
from app.models import UserSubscription
from sqlalchemy.sql import func

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401

        subscription = UserSubscription.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()

        if not subscription:
            return jsonify({"error": "Membership required"}), 403

        if subscription.end_date and subscription.end_date < func.now():
            return jsonify({"error": "Membership expired"}), 403

        return f(*args, **kwargs)
    return decorated_function
