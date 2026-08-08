"""
Phase 7.7 — Configuration & Environment Hardening Test Suite.

Verifies:
- Environment separation (development, testing, production)
- Production safety rules (DEBUG=False, SESSION_COOKIE_SECURE=True, secret key enforcement)
- Development placeholder secret rejection in production
- Fail-fast configuration validation during startup (create_app)
- Database port and parameter range checks
- Non-sensitive configuration fingerprinting
- Repository secret exclusion (.env, .gitignore, tracked secret scan)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
from app.utils.config_validation import validate_config, get_config_fingerprint


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# CFG-01 .. CFG-04: ENVIRONMENT SEPARATION & PRODUCTION CONTROLS
# ============================================================================

def test_cfg_01_development_config_loads():
    """CFG-01: Verifies DevelopmentConfig loads cleanly with local defaults."""
    cfg = DevelopmentConfig()
    assert cfg.DEBUG is True
    assert cfg.TESTING is False
    assert cfg.SESSION_COOKIE_SECURE is False
    assert validate_config(cfg, env_name='development') is True


def test_cfg_02_testing_config_loads():
    """CFG-02: Verifies TestingConfig loads deterministic testing defaults."""
    cfg = TestingConfig()
    assert cfg.TESTING is True
    assert cfg.DEBUG is False
    assert validate_config(cfg, env_name='testing') is True


def test_cfg_03_production_config_loads():
    """CFG-03: Verifies ProductionConfig loads with production security flags."""
    cfg = ProductionConfig()
    cfg.SECRET_KEY = 'prod-super-secure-random-key-2026-xyz!'
    assert cfg.DEBUG is False
    assert cfg.TESTING is False
    assert cfg.SESSION_COOKIE_SECURE is True
    assert validate_config(cfg, env_name='production') is True


def test_cfg_04_production_debug_is_false():
    """CFG-04: Verifies ProductionConfig enforces DEBUG = False."""
    cfg = ProductionConfig()
    assert cfg.DEBUG is False


# ============================================================================
# CFG-05 .. CFG-07: SECRET KEY & PLACEHOLDER REJECTION
# ============================================================================

def test_cfg_05_production_requires_secret_key():
    """CFG-05: Verifies production configuration rejects empty SECRET_KEY."""
    cfg = ProductionConfig()
    cfg.SECRET_KEY = ''
    with pytest.raises(ValueError, match="SECRET_KEY must be defined"):
        validate_config(cfg, env_name='production')


def test_cfg_06_development_allows_local_defaults():
    """CFG-06: Verifies development configuration permits local dev secrets."""
    cfg = DevelopmentConfig()
    assert validate_config(cfg, env_name='development') is True


def test_cfg_07_production_rejects_dev_secret_placeholder():
    """CFG-07: Verifies production configuration rejects dev secret placeholders."""
    cfg = ProductionConfig()
    dev_secrets = ['dev-secret-key-hostelflow-local-only', 'hostelflow-dev-secret-key-2026', 'dev-secret-key-change-in-production']
    for secret in dev_secrets:
        cfg.SECRET_KEY = secret
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            validate_config(cfg, env_name='production')


# ============================================================================
# CFG-08 .. CFG-10: DATABASE & ENVIRONMENT VALIDATION
# ============================================================================

def test_cfg_08_required_db_config_validated():
    """CFG-08: Verifies required DB parameters (DB_HOST, DB_NAME, DB_USER) are validated."""
    cfg = DevelopmentConfig()
    cfg.DB_HOST = ''
    with pytest.raises(ValueError, match="DB_HOST.*cannot be empty"):
        validate_config(cfg, env_name='development')


def test_cfg_09_invalid_db_port_rejected():
    """CFG-09: Verifies invalid DB port numbers (<1 or >65535) are rejected."""
    cfg = DevelopmentConfig()
    
    cfg.DB_PORT = 0
    with pytest.raises(ValueError, match="out of valid range|Invalid database port"):
        validate_config(cfg, env_name='development')

    cfg.DB_PORT = 70000
    with pytest.raises(ValueError, match="out of valid range|Invalid database port"):
        validate_config(cfg, env_name='development')

    cfg.DB_PORT = "invalid_port"
    with pytest.raises(ValueError, match="Invalid database port"):
        validate_config(cfg, env_name='development')


def test_cfg_10_invalid_environment_rejected():
    """CFG-10: Verifies non-standard environment names are rejected."""
    cfg = DevelopmentConfig()
    with pytest.raises(ValueError, match="Invalid environment 'staging'"):
        validate_config(cfg, env_name='staging')


# ============================================================================
# CFG-11 .. CFG-13: REPOSITORY SECRET SCAN & GITIGNORE AUDIT
# ============================================================================

def test_cfg_11_env_file_excluded_from_gitignore():
    """CFG-11: Verifies .gitignore explicitly excludes .env file."""
    gitignore_path = os.path.join(ROOT_DIR, '.gitignore')
    assert os.path.exists(gitignore_path), ".gitignore missing from repository root"
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '.env' in content, ".gitignore does not exclude .env"


def test_cfg_12_env_example_contains_placeholders_only():
    """CFG-12: Verifies .env.example contains placeholders and zero actual secrets."""
    example_path = os.path.join(ROOT_DIR, '.env.example')
    assert os.path.exists(example_path), ".env.example missing from repository root"
    with open(example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'your_database_password_here' in content or 'your_database_user_here' in content
    assert 'Root@123' not in content
    assert 'SuperSecret' not in content


def test_cfg_13_no_tracked_secret_files():
    """CFG-13: Verifies no sensitive .pem, .key, or secrets files exist in repository root."""
    forbidden_extensions = ['.pem', '.key', '.pfx']
    for root, _, files in os.walk(ROOT_DIR):
        if 'venv' in root or '.git' in root:
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            assert ext not in forbidden_extensions, f"Found tracked secret file: {os.path.join(root, file)}"


# ============================================================================
# CFG-14 .. CFG-15: FINGERPRINT & STARTUP FAIL-FAST VERIFICATION
# ============================================================================

def test_cfg_14_configuration_fingerprint_safe():
    """CFG-14: Verifies configuration fingerprint returns non-sensitive metadata only."""
    cfg = DevelopmentConfig()
    fingerprint = get_config_fingerprint(cfg)
    
    assert 'environment' in fingerprint
    assert 'database_host' in fingerprint
    assert 'database_port' in fingerprint
    assert 'database_name' in fingerprint

    # Secret credentials MUST NOT appear in fingerprint keys or values
    fp_str = str(fingerprint).lower()
    assert 'password' not in fingerprint
    assert 'secret_key' not in fingerprint
    assert 'dev-secret-key' not in fp_str


def test_cfg_15_create_app_fails_fast_on_invalid_production_config(monkeypatch):
    """CFG-15: Verifies create_app('production') fails fast when production config is invalid."""
    monkeypatch.delenv('SECRET_KEY', raising=False)
    ProductionConfig.SECRET_KEY = ''
    
    with pytest.raises(ValueError, match="SECRET_KEY must be defined|SECURITY VIOLATION"):
        create_app('production')
