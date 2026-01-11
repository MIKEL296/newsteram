from werkzeug.utils import secure_filename
import os

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(file_obj):
    """Get file size without reading entire file"""
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    return size

def format_file_size(size_bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def generate_s3_key(user_id, filename):
    """Generate S3 key for file storage"""
    from datetime import datetime
    secure_name = secure_filename(filename)
    timestamp = datetime.utcnow().timestamp()
    return f"movies/{user_id}/{timestamp}_{secure_name}"
