import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-hostelflow-local-only')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    IS_DEV = False

    # Session & Cookie Security Controls
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
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
    IS_DEV = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = False
    TESTING = True
    IS_DEV = True
    FLASK_ENV = 'testing'
    SESSION_COOKIE_SECURE = False
    DB_NAME = os.environ.get('TEST_DB_NAME', 'hostelflow_db')


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    IS_DEV = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY', '')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
