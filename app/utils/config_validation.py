"""
Phase 7.7 — HostelFlow Fail-Fast Configuration Validation Utility.

Validates environment parameters, database configuration, port boundaries,
and production security controls upon application startup.
Provides non-sensitive configuration fingerprinting.
"""

import os

VALID_ENVIRONMENTS = {'development', 'testing', 'production'}

DEV_PLACEHOLDER_SECRETS = {
    'dev-secret-key-hostelflow-local-only',
    'hostelflow-dev-secret-key-2026',
    'dev-secret-key-change-in-production',
    'dev-secret-key',
    'secret_key',
    'change-me',
    'your_secret_key_here'
}


def _get_config_value(config_source, key, default=None):
    """Utility extracting configuration value from object, dict, or environment."""
    if isinstance(config_source, dict):
        return config_source.get(key, default)
    if hasattr(config_source, key):
        return getattr(config_source, key)
    return os.environ.get(key, default)


def validate_config(config_source, env_name=None):
    """
    Validates application configuration object or dictionary.
    Raises ValueError on missing, invalid, or unsafe configuration.
    """
    if env_name is None:
        env_name = _get_config_value(config_source, 'FLASK_ENV', os.environ.get('FLASK_ENV', 'development'))
    
    env_name = str(env_name).lower()
    if env_name not in VALID_ENVIRONMENTS:
        raise ValueError(f"Invalid environment '{env_name}'. Permitted environments: {sorted(list(VALID_ENVIRONMENTS))}")

    # 1. Database Port Range Validation (1 .. 65535)
    db_port = _get_config_value(config_source, 'DB_PORT', 3306)
    try:
        db_port_int = int(db_port)
        if not (1 <= db_port_int <= 65535):
            raise ValueError(f"Database port {db_port} out of valid range (1-65535).")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid database port value: {db_port}")

    # 2. Database Parameter Validation
    db_host = _get_config_value(config_source, 'DB_HOST', 'localhost')
    db_name = _get_config_value(config_source, 'DB_NAME', 'hostelflow_db')
    db_user = _get_config_value(config_source, 'DB_USER', 'root')

    if not db_host or not str(db_host).strip():
        raise ValueError("DB_HOST configuration parameter cannot be empty.")
    if not db_name or not str(db_name).strip():
        raise ValueError("DB_NAME configuration parameter cannot be empty.")
    if not db_user or not str(db_user).strip():
        raise ValueError("DB_USER configuration parameter cannot be empty.")

    secret_key = _get_config_value(config_source, 'SECRET_KEY', '')
    debug = _get_config_value(config_source, 'DEBUG', False)
    testing = _get_config_value(config_source, 'TESTING', False)
    secure_cookie = _get_config_value(config_source, 'SESSION_COOKIE_SECURE', False)

    # 3. Production Hardening Validation
    is_production = (env_name == 'production') or (debug is False and testing is False and not _get_config_value(config_source, 'IS_DEV', False))

    if is_production or env_name == 'production':
        if not secret_key or not str(secret_key).strip():
            raise ValueError("CRITICAL CONFIGURATION ERROR: SECRET_KEY must be defined in Production environment!")
        
        if str(secret_key).lower() in DEV_PLACEHOLDER_SECRETS or 'dev-secret' in str(secret_key).lower():
            raise ValueError(f"SECURITY VIOLATION: Production cannot use development placeholder SECRET_KEY '{secret_key}'.")

        if debug is True:
            raise ValueError("SECURITY VIOLATION: DEBUG mode must be False in Production environment!")

        if secure_cookie is False and os.environ.get('ALLOW_INSECURE_PROD_COOKIE') != '1':
            raise ValueError("SECURITY VIOLATION: SESSION_COOKIE_SECURE must be True in Production environment!")

    return True


def get_config_fingerprint(config_source):
    """
    Returns non-sensitive configuration metadata fingerprint for debugging and diagnostics.
    Excludes all passwords, secret keys, and session secrets.
    """
    env_name = _get_config_value(config_source, 'FLASK_ENV', os.environ.get('FLASK_ENV', 'development'))
    return {
        'environment': env_name,
        'debug_mode': bool(_get_config_value(config_source, 'DEBUG', False)),
        'testing_mode': bool(_get_config_value(config_source, 'TESTING', False)),
        'database_host': str(_get_config_value(config_source, 'DB_HOST', 'localhost')),
        'database_port': int(_get_config_value(config_source, 'DB_PORT', 3306)),
        'database_name': str(_get_config_value(config_source, 'DB_NAME', 'hostelflow_db')),
        'database_user': str(_get_config_value(config_source, 'DB_USER', 'root')),
        'session_cookie_httponly': bool(_get_config_value(config_source, 'SESSION_COOKIE_HTTPONLY', True)),
        'session_cookie_samesite': str(_get_config_value(config_source, 'SESSION_COOKIE_SAMESITE', 'Lax')),
        'session_cookie_secure': bool(_get_config_value(config_source, 'SESSION_COOKIE_SECURE', False))
    }
