from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config.config import config
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Serve frontend from 'frontend' directory
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    app = Flask(__name__, static_folder=frontend_path, static_url_path='/')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    migrate.init_app(app, db)
    
    # Serve frontend files
    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if path != '' and os.path.exists(os.path.join(frontend_path, path)):
            return app.send_static_file(path)
        return app.send_static_file('index.html')
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.streaming import streaming_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(streaming_bp, url_prefix='/api/stream')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    with app.app_context():
        db.create_all()
    
    return app
