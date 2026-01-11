from app import db
from datetime import datetime

class Movie(db.Model):
    """Movie model for storing movie metadata and streaming info"""
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    genre = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    duration = db.Column(db.Integer)  # Duration in minutes
    rating = db.Column(db.Float)  # IMDb or TMDB rating
    poster_url = db.Column(db.String(500))
    backdrop_url = db.Column(db.String(500))
    tmdb_id = db.Column(db.Integer, unique=True, index=True)
    
    # Storage information
    s3_key = db.Column(db.String(500), unique=True, nullable=False, index=True)
    file_size = db.Column(db.BigInteger)  # File size in bytes
    video_format = db.Column(db.String(20))  # mp4, mkv, etc.
    resolution = db.Column(db.String(20))  # 480p, 720p, 1080p, 4K
    
    # Metadata
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    view_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', backref=db.backref('uploaded_movies', lazy=True))
    watch_history = db.relationship('WatchHistory', backref='movie', lazy=True, cascade='all, delete-orphan')
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def to_dict(self, include_uploader=False):
        """Convert movie to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'duration': self.duration,
            'rating': self.rating,
            'poster_url': self.poster_url,
            'backdrop_url': self.backdrop_url,
            'tmdb_id': self.tmdb_id,
            'resolution': self.resolution,
            'view_count': self.view_count,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_uploader:
            data['uploader'] = self.uploader.to_dict()
        else:
            data['uploader_id'] = self.uploader_id
        
        return data
