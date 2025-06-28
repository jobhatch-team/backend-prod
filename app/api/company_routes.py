from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models import db, Company

company_routes = Blueprint('companies', __name__)


# Get all companies (login required)
@company_routes.route('/', methods=['GET'])
@login_required
def get_companies():
    companies = Company.query.all()
    return jsonify({'companies': [company.to_dict() for company in companies]}), 200


# Get a single company by id (login required)
@company_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_company(id):
    company = Company.query.get_or_404(id)
    return jsonify(company.to_dict()), 200


# Create a new company (login required)
@company_routes.route('/', methods=['POST'])
@login_required
def create_company():
    data = request.get_json()

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Company name is required'}), 400

    if Company.query.filter_by(name=name).first():
        return jsonify({'error': 'Company name already exists'}), 400

    company = Company(
        name=name,
        website=data.get('website'),
        logo_url=data.get('logo_url'),
        description=data.get('description'),
        location=data.get('location'),
        funding_stage=data.get('funding_stage')
    )

    db.session.add(company)
    db.session.commit()

    return jsonify(company.to_dict()), 201


# Update a company by id (login required)
@company_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_company(id):
    company = Company.query.get_or_404(id)
    data = request.get_json()

    name = data.get('name')
    if name and name != company.name:
        if Company.query.filter_by(name=name).first():
            return jsonify({'error': 'Company name already exists'}), 400
        company.name = name

    company.website = data.get('website', company.website)
    company.logo_url = data.get('logo_url', company.logo_url)
    company.description = data.get('description', company.description)
    company.location = data.get('location', company.location)
    company.funding_stage = data.get('funding_stage', company.funding_stage)

    db.session.commit()

    return jsonify(company.to_dict()), 200


# Delete a company by id (login required)
@company_routes.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_company(id):
    company = Company.query.get_or_404(id)

    db.session.delete(company)
    db.session.commit()

    return jsonify({'message': 'Company deleted successfully'}), 200
