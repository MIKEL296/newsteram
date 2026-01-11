from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.movie_service import MovieService
from app.services.s3_service import S3Service
from app.services.tmdb_service import TMDBService
from app.models.movie import Movie
from app import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os

movies_bp = Blueprint('movies', __name__)
s3_service = S3Service()
tmdb_service = TMDBService()

ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv'}
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5368709120))  # 5GB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@movies_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_movie():
    """Upload a new movie"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'File size exceeds maximum allowed'}), 413
    
    try:
        # Get metadata from request
        metadata = {
            'title': request.form.get('title', 'Untitled'),
            'description': request.form.get('description', ''),
            'genre': request.form.get('genre', ''),
            'tmdb_id': request.form.get('tmdb_id')
        }
        
        # Generate S3 key
        filename = secure_filename(file.filename)
        s3_key = f"movies/{user_id}/{datetime.utcnow().timestamp()}_{filename}"
        
        # Upload to S3
        file_ext = filename.rsplit('.', 1)[1].lower()
        s3_service.upload_movie(
            file,
            s3_key,
            content_type=f'video/{file_ext}',
            metadata=metadata
        )
        
        # Create movie record
        movie_data = {
            'title': metadata['title'],
            'description': metadata['description'],
            'genre': metadata['genre'],
            'tmdb_id': metadata['tmdb_id'],
            's3_key': s3_key,
            'file_size': file_size,
            'video_format': file_ext,
            'uploader_id': user_id,
            'is_public': request.form.get('is_public', 'false').lower() == 'true'
        }
        
        movie, status_code = MovieService.create_movie(movie_data)
        
        return jsonify({
            'message': 'Movie uploaded successfully',
            'movie': movie.to_dict()
        }), status_code
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get movie details"""
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    if not movie.is_public:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(movie.to_dict(include_uploader=True)), 200

@movies_bp.route('', methods=['GET'])
def list_movies():
    """List all public movies with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = MovieService.get_public_movies(page, per_page)
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'movies': [movie.to_dict() for movie in paginated.items]
    }), 200

@movies_bp.route('/featured', methods=['GET'])
def get_featured():
    """Get featured movies"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = MovieService.get_featured_movies(page, per_page)
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'movies': [movie.to_dict() for movie in paginated.items]
    }), 200

@movies_bp.route('/search', methods=['GET'])
def search_movies():
    """Search movies"""
    query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    paginated = MovieService.search_movies(query, page, per_page)
    
    return jsonify({
        'query': query,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'movies': [movie.to_dict() for movie in paginated.items]
    }), 200

@movies_bp.route('/tmdb/search', methods=['GET'])
def tmdb_search():
    """Search movies from TMDB API"""
    query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        results = tmdb_service.search_movies(query, page)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': f'TMDB search failed: {str(e)}'}), 500

@movies_bp.route('/tmdb/trending', methods=['GET'])
def tmdb_trending():
    """Get trending movies from TMDB"""
    time_window = request.args.get('time_window', 'week', type=str)
    page = request.args.get('page', 1, type=int)
    
    if time_window not in ['day', 'week']:
        time_window = 'week'
    
    try:
        results = tmdb_service.get_trending_movies(time_window, page)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch trending movies: {str(e)}'}), 500

@movies_bp.route('/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id):
    """Update movie details"""
    user_id = get_jwt_identity()
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    if movie.uploader_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    allowed_fields = ['title', 'description', 'genre', 'is_public', 'is_featured']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    try:
        movie, status_code = MovieService.update_movie(movie_id, update_data)
        return jsonify(movie.to_dict()), status_code
    except Exception as e:
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

@movies_bp.route('/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    """Delete a movie"""
    user_id = get_jwt_identity()
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    if movie.uploader_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        s3_service.delete_movie(movie.s3_key)
        MovieService.delete_movie(movie_id)
        return jsonify({'message': 'Movie deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500
