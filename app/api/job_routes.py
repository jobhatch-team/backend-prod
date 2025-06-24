from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Job

job_routes = Blueprint('jobs', __name__)

# Create a job 
@job_routes.route('/', methods=['POST'])
@login_required
def create_job():
    data = request.get_json()

    job = Job(
        title=data.get('title'),
        description=data.get('description'),
        work_experience=data.get('work_experience'),
        skills=data.get('skills'),
        location=data.get('location'),
        accept_relocate=data.get('accept_relocate'),
        offer_relocate_assistance=data.get('offer_relocate_assistance'),
        offer_visa_sponsorship=data.get('offer_visa_sponsorship'),
        is_remote=data.get('is_remote'),
        currency=data.get('currency'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        equity_min=data.get('equity_min'),
        equity_max=data.get('equity_max'),
        job_type=data.get('job_type'),
        company_id=data.get('company_id'),
        posted_by=current_user.id
    )

    db.session.add(job)
    db.session.commit()

    return jsonify(job.to_dict()), 201


# Get all jobs
@job_routes.route('/', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return jsonify({'jobs': [job.to_dict() for job in jobs]}), 200


# Get a single job by id
@job_routes.route('/<int:id>', methods=['GET'])
def get_job(id):
    job = Job.query.get_or_404(id)
    return jsonify(job.to_dict()), 200


# Update a job
@job_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_job(id):
    job = Job.query.get_or_404(id)

    if job.posted_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    for field in [
        'title', 'description', 'work_experience', 'skills', 'location',
        'accept_relocate', 'offer_relocate_assistance', 'offer_visa_sponsorship',
        'is_remote', 'currency', 'salary_min', 'salary_max',
        'equity_min', 'equity_max', 'job_type', 'company_id', 'status'
    ]:
        if field in data:
            setattr(job, field, data[field])

    db.session.commit()
    return jsonify(job.to_dict()), 200


# Delete a job
@job_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_job(id):
    job = Job.query.get_or_404(id)

    if job.posted_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(job)
    db.session.commit()

    return jsonify({'message': 'Job deleted successfully'}), 200
