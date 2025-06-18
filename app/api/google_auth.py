from flask import Blueprint, request, jsonify
from app.models import db, User
from flask_login import login_user
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt
import os
import uuid

google_auth_routes = Blueprint('google_auth', __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")


@google_auth_routes.route('/google', methods=['POST'])
def login_with_google():
    data = request.get_json()
    id_token_str = data.get('idToken')

    if not id_token_str:
        return jsonify({'error': 'Missing id_token'}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get('email')
        username = idinfo.get('name') or email.split('@')[0]
        picture = idinfo.get('picture')

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                username=username,
                email=email,
                avatar_url=picture,
                role='job_seeker', 
                password=str(uuid.uuid4())  
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)

        payload = {
            'user_id': user.id,
            'email': user.email,
        }

        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

        return jsonify({
            'token': jwt_token,
            'user': user.to_dict()
        })

    except ValueError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

