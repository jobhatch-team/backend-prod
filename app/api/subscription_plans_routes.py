from flask import Blueprint, request, jsonify
from app.models import SubscriptionPlan, db

subscriptions_plans_routes = Blueprint('subscriptions', __name__)

# Get all subscription plans
@subscriptions_plans_routes.route('/', methods=['GET'])
def get_plans():
    plans = SubscriptionPlan.query.all()
    return jsonify([plan.to_dict() for plan in plans]), 200

# Get a single subscription plan by id
@subscriptions_plans_routes.route('/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan.to_dict()), 200

# Create a new subscription plan
@subscriptions_plans_routes.route('/', methods=['POST'])
def create_plan():
    data = request.get_json()
    try:
        plan = SubscriptionPlan(
            name=data['name'],
            tagline=data.get('tagline'),
            description=data.get('description'),
            price=data['price'],
            billing_cycle=data['billing_cycle'],
            for_role=data.get('for_role'),
            feature_flags=data.get('feature_flags')
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify(plan.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Update an existing subscription plan by id
@subscriptions_plans_routes.route('/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404

    data = request.get_json()
    try:
        plan.name = data.get('name', plan.name)
        plan.tagline = data.get('tagline', plan.tagline)
        plan.description = data.get('description', plan.description)
        plan.price = data.get('price', plan.price)
        plan.billing_cycle = data.get('billing_cycle', plan.billing_cycle)
        plan.for_role = data.get('for_role', plan.for_role)
        plan.feature_flags = data.get('feature_flags', plan.feature_flags)

        db.session.commit()
        return jsonify(plan.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete a subscription plan by id
@subscriptions_plans_routes.route('/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    try:
        db.session.delete(plan)
        db.session.commit()
        return jsonify({"message": "Plan deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
