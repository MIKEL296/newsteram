from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    response, status_code = AuthService.register_user(
        data['username'],
        data['email'],
        data['password']
    )
    
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and get tokens"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    response, status_code = AuthService.login_user(data['username'], data['password'])
    
    return jsonify(response), status_code

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    response, status_code = AuthService.refresh_access_token(user_id)
    
    return jsonify(response), status_code

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token is valid"""
    user_id = get_jwt_identity()
    return jsonify({'user_id': user_id, 'valid': True}), 200
