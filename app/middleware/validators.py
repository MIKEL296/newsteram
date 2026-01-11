from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def validate_request_json(f):
    """Middleware to validate JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_check(f):
    """Basic rate limiting check (implement with Redis for production)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement rate limiting with Redis
        return f(*args, **kwargs)
    return decorated_function

def log_request(f):
    """Log incoming requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"{request.method} {request.path}")
        return f(*args, **kwargs)
    return decorated_function
