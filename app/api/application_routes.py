from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, Application, Job

application_routes = Blueprint('applications', __name__)


# Get all applications of the current user
@application_routes.route('/', methods=['GET'])
@login_required
def get_applications():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    return jsonify({'applications': [app.to_dict() for app in applications]}), 200


# Get a specific application by ID (must belong to current user)
@application_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_application(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(application.to_dict()), 200


# Create a new application (login required)
@application_routes.route('/', methods=['POST'])
@login_required
def create_application():
    data = request.get_json()

    job_id = data.get('job_id')
    cover_letter = data.get('cover_letter', '')

    if not job_id:
        return jsonify({'error': 'Job ID is required'}), 400

    # Optional: check if job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Optional: prevent duplicate application
    existing = Application.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing:
        return jsonify({'error': 'You have already applied for this job'}), 400

    new_app = Application(
        user_id=current_user.id,
        job_id=job_id,
        cover_letter=cover_letter,
    )

    db.session.add(new_app)
    db.session.commit()

    return jsonify(new_app.to_dict()), 201


# Update an application (only if owned by current user)
@application_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_application(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'cover_letter' in data:
        application.cover_letter = data['cover_letter']

    if 'status' in data:
        application.status = data['status']  # Could add validation (e.g., only admin can change)

    db.session.commit()

    return jsonify(application.to_dict()), 200


# Delete an application (only if owned by current user)
@application_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_application(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(application)
    db.session.commit()

    return jsonify({'message': 'Application deleted successfully'}), 200
