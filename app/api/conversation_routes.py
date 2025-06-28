from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Conversation

conversation_routes = Blueprint('conversations', __name__)

@conversation_routes.route('/')
@login_required
def get_conversations():
    conversations = Conversation.query.filter(
        (Conversation.user_1_id == current_user.id) | 
        (Conversation.user_2_id == current_user.id)
    ).all()
    return jsonify([c.to_dict() for c in conversations])

@conversation_routes.route('/', methods=['POST'])
@login_required
def create_or_get_conversation():
    data = request.get_json()
    user_b_id = data.get('user_id')
    if not user_b_id:
        return {'error': 'Missing user_id'}, 400

    conversation = Conversation.get_or_create(current_user.id, user_b_id)
    return jsonify(conversation.to_dict())

@conversation_routes.route('/<int:conversation_id>')
@login_required
def get_conversation_detail(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if current_user.id not in [conversation.user_1_id, conversation.user_2_id]:
        return {'error': 'Unauthorized'}, 403
    return jsonify({
        **conversation.to_dict(),
        'messages': [m.to_dict() for m in conversation.messages]
    })


@conversation_routes.route('/<int:conversation_id>/delete', methods=['PATCH'])
@login_required
def delete_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    if current_user.id == conversation.user_1_id:
        conversation.deleted_by_user_1 = True
    elif current_user.id == conversation.user_2_id:
        conversation.deleted_by_user_2 = True
    else:
        return {'error': 'Unauthorized'}, 403

    db.session.commit()
    return {'message': 'Conversation marked as deleted'}, 200
