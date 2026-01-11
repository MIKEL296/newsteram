from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app import db
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication and JWT token management"""
    
    @staticmethod
    def register_user(username, email, password):
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return {'error': 'Username already exists'}, 400
            
            if User.query.filter_by(email=email).first():
                return {'error': 'Email already registered'}, 400
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            return {'message': 'User registered successfully', 'user': user.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            return {'error': 'Registration failed'}, 500
    
    @staticmethod
    def login_user(username, password):
        """Authenticate user and generate tokens"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                return {'error': 'Invalid username or password'}, 401
            
            if not user.is_active:
                return {'error': 'User account is disabled'}, 403
            
            # Generate tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            logger.info(f"User logged in: {username}")
            return {
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }, 200
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return {'error': 'Login failed'}, 500
    
    @staticmethod
    def refresh_access_token(user_id):
        """Generate new access token from refresh token"""
        try:
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return {'error': 'User not found or inactive'}, 401
            
            access_token = create_access_token(identity=user_id)
            return {'access_token': access_token}, 200
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return {'error': 'Token refresh failed'}, 500
