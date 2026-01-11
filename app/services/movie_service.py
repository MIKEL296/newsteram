from app.models.movie import Movie
from app.models.watch_history import WatchHistory
from app import db
import logging

logger = logging.getLogger(__name__)

class MovieService:
    """Service for movie management operations"""
    
    @staticmethod
    def create_movie(movie_data):
        """Create a new movie record"""
        try:
            movie = Movie(**movie_data)
            db.session.add(movie)
            db.session.commit()
            
            logger.info(f"Movie created: {movie.title}")
            return movie, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating movie: {str(e)}")
            raise
    
    @staticmethod
    def update_movie(movie_id, update_data):
        """Update movie details"""
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return None, 404
            
            for key, value in update_data.items():
                if hasattr(movie, key):
                    setattr(movie, key, value)
            
            db.session.commit()
            logger.info(f"Movie updated: {movie.title}")
            return movie, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating movie: {str(e)}")
            raise
    
    @staticmethod
    def delete_movie(movie_id):
        """Delete a movie"""
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return False
            
            db.session.delete(movie)
            db.session.commit()
            logger.info(f"Movie deleted: {movie.title}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting movie: {str(e)}")
            raise
    
    @staticmethod
    def get_movie_by_id(movie_id):
        """Get movie by ID"""
        return Movie.query.get(movie_id)
    
    @staticmethod
    def get_public_movies(page=1, per_page=20):
        """Get all public movies with pagination"""
        return Movie.query.filter_by(is_public=True).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_featured_movies(page=1, per_page=20):
        """Get featured movies"""
        return Movie.query.filter_by(is_public=True, is_featured=True).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def search_movies(query, page=1, per_page=20):
        """Search movies by title or description"""
        return Movie.query.filter(
            (Movie.is_public == True) &
            ((Movie.title.ilike(f'%{query}%')) | (Movie.description.ilike(f'%{query}%')))
        ).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_user_movies(user_id, page=1, per_page=20):
        """Get all movies uploaded by a user"""
        return Movie.query.filter_by(uploader_id=user_id).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def record_watch(user_id, movie_id, watch_time, total_duration):
        """Record or update watch history"""
        try:
            watch_entry = WatchHistory.query.filter_by(user_id=user_id, movie_id=movie_id).first()
            
            if watch_entry:
                watch_entry.watch_time = watch_time
                watch_entry.is_completed = watch_time >= total_duration * 0.9  # 90% watched
            else:
                watch_entry = WatchHistory(
                    user_id=user_id,
                    movie_id=movie_id,
                    watch_time=watch_time,
                    total_duration=total_duration,
                    is_completed=watch_time >= total_duration * 0.9
                )
                db.session.add(watch_entry)
            
            db.session.commit()
            return watch_entry, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording watch history: {str(e)}")
            raise
    
    @staticmethod
    def get_user_watch_history(user_id, page=1, per_page=20):
        """Get user's watch history"""
        return WatchHistory.query.filter_by(user_id=user_id).order_by(
            WatchHistory.last_watched.desc()
        ).paginate(page=page, per_page=per_page)
