from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.s3_service import S3Service
from app.services.movie_service import MovieService

streaming_bp = Blueprint('streaming', __name__)
s3_service = S3Service()

@streaming_bp.route('/<int:movie_id>/url', methods=['GET'])
@jwt_required()
def get_stream_url(movie_id):
    """Get presigned URL for streaming"""
    user_id = get_jwt_identity()
    
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    if not movie.is_public:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Generate presigned URL (valid for 1 hour)
        stream_url = s3_service.generate_presigned_url(movie.s3_key, expiration=3600)
        
        # Increment view count
        movie.increment_view_count()
        
        return jsonify({
            'movie_id': movie_id,
            'stream_url': stream_url,
            'title': movie.title,
            'duration': movie.duration,
            'resolution': movie.resolution,
            'expires_in': 3600
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate stream URL: {str(e)}'}), 500

@streaming_bp.route('/<int:movie_id>/watch', methods=['POST'])
@jwt_required()
def record_watch(movie_id):
    """Record watch progress"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'watch_time' not in data or 'total_duration' not in data:
        return jsonify({'error': 'Missing watch_time or total_duration'}), 400
    
    try:
        watch_entry, status_code = MovieService.record_watch(
            user_id,
            movie_id,
            data['watch_time'],
            data['total_duration']
        )
        
        return jsonify({
            'message': 'Watch progress recorded',
            'watch_entry': watch_entry.to_dict()
        }), status_code
    except Exception as e:
        return jsonify({'error': f'Failed to record watch progress: {str(e)}'}), 500

@streaming_bp.route('/history', methods=['GET'])
@jwt_required()
def get_watch_history():
    """Get user's watch history"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = MovieService.get_user_watch_history(user_id, page, per_page)
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'watch_history': [entry.to_dict() for entry in paginated.items]
    }), 200
