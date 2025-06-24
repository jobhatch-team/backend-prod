from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, WorkExperience
from datetime import datetime

work_routes = Blueprint('work_experiences', __name__)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
    except ValueError:
        return None

@work_routes.route('/', methods=['POST'])
@login_required
def create_work_experience():
    data = request.get_json()

    work = WorkExperience(
        user_id=current_user.id,
        company_name=data.get('company_name'),
        title=data.get('title'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        current_work=data.get('current_work'),
        description=data.get('description')
    )

    db.session.add(work)
    db.session.commit()
    return jsonify(work.to_dict()), 201


@work_routes.route('/', methods=['GET'])
@login_required
def get_all_my_work_experiences():
    works = WorkExperience.query.filter_by(user_id=current_user.id).all()
    return jsonify({'work_experiences': [w.to_dict() for w in works]}), 200


@work_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_work_experience_by_id(id):
    work = WorkExperience.query.get_or_404(id)
    if work.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(work.to_dict()), 200


@work_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_work_experience(id):
    work = WorkExperience.query.get_or_404(id)
    if work.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    for field in ['company_name', 'title', 'current_work', 'description']:
        if field in data:
            setattr(work, field, data[field])

    if 'start_date' in data:
        work.start_date = parse_date(data['start_date'])

    if 'end_date' in data:
        work.end_date = parse_date(data['end_date'])

    db.session.commit()
    return jsonify(work.to_dict()), 200


@work_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_work_experience(id):
    work = WorkExperience.query.get_or_404(id)
    if work.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(work)
    db.session.commit()
    return jsonify({'message': 'Work experience deleted successfully'}), 200
