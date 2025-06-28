from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from openai import OpenAI
import os

ai_routes = Blueprint('ai', __name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Chat with AI (login required)
@ai_routes.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    data = request.get_json()
    messages = data.get('messages')

    if not messages or not isinstance(messages, list):
        return jsonify({'error': 'Invalid or missing messages'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

