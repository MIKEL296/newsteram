from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.movie_service import MovieService
from app import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    allowed_fields = ['first_name', 'last_name', 'profile_picture_url']
    
    try:
        for key, value in data.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

@users_bp.route('/me/movies', methods=['GET'])
@jwt_required()
def get_user_movies():
    """Get current user's uploaded movies"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = MovieService.get_user_movies(user_id, page, per_page)
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'movies': [movie.to_dict() for movie in paginated.items]
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get public user profile"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = user.to_dict()
    # Add public statistics
    profile['total_uploads'] = len(user.uploaded_movies)
    
    return jsonify(profile), 200

@users_bp.route('/<int:user_id>/movies', methods=['GET'])
def get_user_public_movies(user_id):
    """Get user's public movies"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = MovieService.get_user_movies(user_id, page, per_page)
    
    return jsonify({
        'user': user.to_dict(),
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'movies': [movie.to_dict() for movie in paginated.items if movie.is_public]
    }), 200
