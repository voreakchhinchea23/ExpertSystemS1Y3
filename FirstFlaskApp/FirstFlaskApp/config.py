import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-me"
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL not set in environment variables or .env file")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MySQL connection pool settings (recommended)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {'charset': 'utf8mb4'}
    }

    # Upload settings
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'dishes')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB