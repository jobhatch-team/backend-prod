from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, EducationExperience
from datetime import datetime

education_routes = Blueprint('education_experiences', __name__)

@education_routes.route('/', methods=['POST'])
@login_required
def create_education_experience():
    data = request.get_json()

    edu = EducationExperience(
        user_id=current_user.id,
        school_name=data.get('school_name'),
        graduation=data.get('graduation'),
        degree=data.get('degree'),
        major=data.get('major'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        gpa=data.get('gpa')
    )

    db.session.add(edu)
    db.session.commit()
    return jsonify(edu.to_dict()), 201


@education_routes.route('/', methods=['GET'])
@login_required
def get_all_my_educations():
    educations = EducationExperience.query.filter_by(user_id=current_user.id).all()
    return jsonify({'education_experiences': [e.to_dict() for e in educations]}), 200


@education_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_education_by_id(id):
    edu = EducationExperience.query.get_or_404(id)
    if edu.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(edu.to_dict()), 200


@education_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_education(id):
    edu = EducationExperience.query.get_or_404(id)
    if edu.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    for field in [
        'school_name', 'graduation', 'degree', 'major', 'gpa'
    ]:
        if field in data:
            setattr(edu, field, data[field])

    if 'start_date' in data:
        edu.start_date = parse_date(data['start_date'])

    if 'end_date' in data:
        edu.end_date = parse_date(data['end_date'])

    db.session.commit()
    return jsonify(edu.to_dict()), 200


@education_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_education(id):
    edu = EducationExperience.query.get_or_404(id)
    if edu.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(edu)
    db.session.commit()
    return jsonify({'message': 'Education deleted successfully'}), 200


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
    except ValueError:
        return None
