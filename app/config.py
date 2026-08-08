import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError("CRITICAL SECURITY ERROR: SECRET_KEY must be set in production environment!")
        SECRET_KEY = 'dev-secret-key-hostelflow-local-only'

    # Session & Cookie Security Controls
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = (os.environ.get('FLASK_ENV') == 'production')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Request Body Payload Limits (16 MB maximum)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_NAME = os.environ.get('DB_NAME', 'hostelflow_db')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

    # Connection Pool / Timeouts
    DB_CONNECT_TIMEOUT = 10


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = False
    TESTING = True
    DB_NAME = os.environ.get('TEST_DB_NAME', 'hostelflow_db')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

