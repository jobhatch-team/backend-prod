from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Message, Conversation
from sqlalchemy.sql import func

message_routes = Blueprint('messages', __name__)

@message_routes.route('/', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    message_body = data.get('message_body')

    if not conversation_id or not message_body:
        return {'error': 'Missing fields'}, 400

    # Check permission
    conversation = Conversation.query.get_or_404(conversation_id)
    if current_user.id not in [conversation.user_1_id, conversation.user_2_id]:
        return {'error': 'Unauthorized'}, 403

    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        message_body=message_body
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict())

@message_routes.route('/<int:message_id>/read', methods=['PATCH'])
@login_required
def mark_message_read(message_id):
    message = Message.query.get_or_404(message_id)
    conversation = message.conversation
    if current_user.id not in [conversation.user_1_id, conversation.user_2_id]:
        return {'error': 'Unauthorized'}, 403

    message.read_at = func.now()
    db.session.commit()
    return jsonify(message.to_dict())

@message_routes.route('/<int:message_id>/recall', methods=['PATCH'])
@login_required
def recall_message(message_id):
    message = Message.query.get_or_404(message_id)
    conversation = message.conversation

    if current_user.id != message.sender_id:
        return {'error': 'Unauthorized'}, 403

    if message.is_recalled:
        return {'error': 'Message already recalled'}, 400

    message.is_recalled = True
    db.session.commit()
    return jsonify(message.to_dict())

@message_routes.route('/<int:message_id>/edit', methods=['PATCH'])
@login_required
def edit_message(message_id):
    data = request.get_json()
    new_body = data.get('message_body')
    if not new_body:
        return {'error': 'Missing message_body'}, 400

    message = Message.query.get_or_404(message_id)
    if current_user.id != message.sender_id:
        return {'error': 'Unauthorized'}, 403

    if message.is_recalled:
        return {'error': 'Cannot edit a recalled message'}, 400

    message.message_body = new_body
    message.edited_at = func.now()
    db.session.commit()
    return jsonify(message.to_dict())
