from app import db
from datetime import datetime

class WatchHistory(db.Model):
    """Watch history model for tracking user viewing activity"""
    __tablename__ = 'watch_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    watch_time = db.Column(db.Integer, default=0)  # Seconds watched
    total_duration = db.Column(db.Integer)  # Total movie duration in seconds
    is_completed = db.Column(db.Boolean, default=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_watched = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),
    )
    
    def to_dict(self):
        """Convert watch history to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'watch_time': self.watch_time,
            'total_duration': self.total_duration,
            'progress_percentage': round((self.watch_time / self.total_duration * 100) if self.total_duration else 0),
            'is_completed': self.is_completed,
            'viewed_at': self.viewed_at.isoformat(),
            'last_watched': self.last_watched.isoformat()
        }
