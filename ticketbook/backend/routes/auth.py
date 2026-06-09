from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from database import db
from models import User

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = 'ticketbook-secret-key-for-testing'


def make_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id'], None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'


def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, 'Missing or malformed Authorization header'
    token = auth_header.split(' ', 1)[1]
    user_id, err = decode_token(token)
    if err:
        return None, err
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'
    return user, None


# POST /api/auth/register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    if not email or not password or not name:
        return jsonify({'error': 'email, password and name are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
        role='user'
    )
    db.session.add(user)
    db.session.commit()

    token = make_token(user.id)
    return jsonify({'message': 'Registered successfully', 'session_token': token, 'user': user.to_dict()}), 201


# POST /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = make_token(user.id)
    return jsonify({'message': 'Login successful', 'session_token': token, 'user': user.to_dict()}), 200


# POST /api/auth/logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Stateless JWT — just acknowledge
    return jsonify({'message': 'Logged out successfully'}), 200


# GET /api/auth/me
@auth_bp.route('/me', methods=['GET'])
def me():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    return jsonify({'user': user.to_dict()}), 200
