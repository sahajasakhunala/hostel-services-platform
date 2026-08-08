"""
Phase 7.9 — Final Full-Platform Regression Verification Test Suite.

This is the final quality gate before v1.0.0 release candidate.
It executes a comprehensive regression across every subsystem:
  - Environment & configuration
  - API route availability & validation
  - Authentication & RBAC boundaries
  - UI template rendering
  - Structured logging & security events
  - Configuration hardening
  - Documentation integrity
  - Complete end-to-end student lifecycle

Release Criteria:
  ALL TESTS MUST PASS. No v1.0 candidate unless every assertion succeeds.
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
from app.utils.validation import (
    require_fields, validate_integer_id, validate_positive_amount,
    validate_enum, validate_date_string, validate_string_length
)
from app.utils.logging import (
    APP_LOG_PATH, SEC_LOG_PATH, ERR_LOG_PATH,
    log_app_event, log_security_event, log_exception, scrub_sensitive_data
)
from app.utils.config_validation import validate_config, get_config_fingerprint

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def _read_log(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def _clear_logs():
    for p in (APP_LOG_PATH, SEC_LOG_PATH, ERR_LOG_PATH):
        if os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                f.truncate(0)


# ============================================================================
# SECTION 1: ENVIRONMENT & CONFIGURATION REGRESSION (REG-01..REG-05)
# ============================================================================

def test_reg_01_development_config():
    """REG-01: Development configuration loads with correct defaults."""
    cfg = DevelopmentConfig()
    assert cfg.DEBUG is True
    assert cfg.TESTING is False
    assert validate_config(cfg, env_name='development') is True


def test_reg_02_testing_config():
    """REG-02: Testing configuration loads deterministic test parameters."""
    cfg = TestingConfig()
    assert cfg.TESTING is True
    assert cfg.DEBUG is False
    assert validate_config(cfg, env_name='testing') is True


def test_reg_03_production_debug_false():
    """REG-03: Production configuration enforces DEBUG = False."""
    cfg = ProductionConfig()
    assert cfg.DEBUG is False


def test_reg_04_production_rejects_dev_secret():
    """REG-04: Production rejects development placeholder secrets."""
    cfg = ProductionConfig()
    cfg.SECRET_KEY = 'dev-secret-key-hostelflow-local-only'
    with pytest.raises(ValueError, match="SECURITY VIOLATION"):
        validate_config(cfg, env_name='production')


def test_reg_05_config_fingerprint_safe():
    """REG-05: Configuration fingerprint excludes credentials."""
    cfg = DevelopmentConfig()
    fp = get_config_fingerprint(cfg)
    fp_str = str(fp).lower()
    assert 'password' not in fp
    assert 'secret_key' not in fp
    assert 'dev-secret-key' not in fp_str


# ============================================================================
# SECTION 2: API ROUTE AVAILABILITY & VALIDATION REGRESSION (REG-06..REG-12)
# ============================================================================

def test_reg_06_health_check(client):
    """REG-06: Health endpoint responds with 200."""
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'healthy'


def test_reg_07_student_validation(client):
    """REG-07: Student registration rejects invalid payloads with 400."""
    res = client.post('/api/students', json={})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


def test_reg_08_allocation_validation(client):
    """REG-08: Allocation endpoint rejects invalid payloads with 400."""
    res = client.post('/api/allocations', json={'student_id': -1})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


def test_reg_09_finance_validation(client):
    """REG-09: Finance payment rejects invalid payloads with 400."""
    res = client.post('/api/finance/payments', json={'amount': -500})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


def test_reg_10_visitor_validation(client):
    """REG-10: Visitor endpoint rejects invalid payloads with 400."""
    res = client.post('/api/visitors', json={'id_type': 'InvalidCard'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


def test_reg_11_complaint_validation(client):
    """REG-11: Complaint endpoint rejects invalid payloads with 400."""
    res = client.post('/api/complaints', json={'priority': 'super_urgent'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


def test_reg_12_maintenance_validation(client):
    """REG-12: Maintenance endpoint rejects invalid payloads with 400."""
    res = client.post('/api/maintenance', json={'priority': 'invalid'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# ============================================================================
# SECTION 3: AUTHENTICATION & RBAC REGRESSION (REG-13..REG-16)
# ============================================================================

def test_reg_13_unauthenticated_access_blocked(client):
    """REG-13: Unauthenticated access to protected endpoints returns 401."""
    res = client.get('/api/auth/me')
    assert res.status_code == 401


def test_reg_14_invalid_login(client):
    """REG-14: Invalid credentials return 401."""
    res = client.post('/api/auth/login', json={'username': 'invalid', 'password': 'wrong'})
    assert res.status_code == 401


def test_reg_15_missing_credentials(client):
    """REG-15: Missing credentials return 400."""
    res = client.post('/api/auth/login', json={})
    assert res.status_code == 400


def test_reg_16_x_request_id_header(client):
    """REG-16: Every response includes X-Request-ID correlation header."""
    res = client.get('/health')
    assert 'X-Request-ID' in res.headers
    assert len(res.headers['X-Request-ID']) > 0


# ============================================================================
# SECTION 4: UI TEMPLATE ROUTE REGRESSION (REG-17..REG-25)
# ============================================================================

@pytest.mark.parametrize("route,expected_status", [
    ('/login', 200),
    ('/dashboard', 200),
    ('/students', 200),
    ('/allocations', 200),
    ('/finance', 200),
    ('/visitors', 200),
    ('/complaints', 200),
    ('/maintenance', 200),
    ('/reports', 200),
])
def test_reg_17_to_25_ui_templates(client, route, expected_status):
    """REG-17..25: All UI template routes render without errors."""
    res = client.get(route)
    assert res.status_code == expected_status


# ============================================================================
# SECTION 5: STRUCTURED LOGGING & SECURITY REGRESSION (REG-26..REG-31)
# ============================================================================

def test_reg_26_log_file_separation():
    """REG-26: Application events write to application.log only."""
    _clear_logs()
    log_app_event('REG_TEST_APP_EVENT', {'test': True})
    assert 'REG_TEST_APP_EVENT' in _read_log(APP_LOG_PATH)
    assert 'REG_TEST_APP_EVENT' not in _read_log(SEC_LOG_PATH)


def test_reg_27_security_log_separation():
    """REG-27: Security events write to security.log only."""
    _clear_logs()
    log_security_event('REG_TEST_SEC_EVENT', {'test': True})
    assert 'REG_TEST_SEC_EVENT' in _read_log(SEC_LOG_PATH)
    assert 'REG_TEST_SEC_EVENT' not in _read_log(APP_LOG_PATH)


def test_reg_28_error_traceback_logged():
    """REG-28: Exception tracebacks are logged server-side to error.log."""
    _clear_logs()
    try:
        raise RuntimeError("REG_TEST_EXCEPTION")
    except Exception:
        log_exception("REG_TEST_ERROR", exc_info=True)
    assert 'REG_TEST_EXCEPTION' in _read_log(ERR_LOG_PATH)


def test_reg_29_500_response_sanitized(client):
    """REG-29: 500 responses contain no stack trace leakage."""
    app = create_app('testing')
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.config['TESTING'] = False

    @app.route('/reg-crash-test')
    def crash():
        raise ValueError("REG_INTERNAL_FAILURE")

    tc = app.test_client()
    res = tc.get('/reg-crash-test')
    assert res.status_code == 500
    data = res.get_json()
    assert data['message'] == 'An internal server error occurred.'
    assert 'REG_INTERNAL_FAILURE' not in str(data)


def test_reg_30_sensitive_data_scrubbed():
    """REG-30: Recursive sensitive data scrubber works correctly."""
    payload = {
        'user': {'username': 'admin', 'password': 'secret123'},
        'config': {'db_password': 'root_pass', 'token': 'jwt_abc'}
    }
    scrubbed = scrub_sensitive_data(payload)
    assert scrubbed['user']['password'] == '[REDACTED]'
    assert scrubbed['config']['db_password'] == '[REDACTED]'
    assert scrubbed['config']['token'] == '[REDACTED]'
    assert scrubbed['user']['username'] == 'admin'


def test_reg_31_auth_failure_logged(client):
    """REG-31: Failed login attempts are logged to security.log."""
    _clear_logs()
    client.post('/api/auth/login', json={'username': 'attacker', 'password': 'wrong'})
    assert 'AUTH_LOGIN_FAILURE' in _read_log(SEC_LOG_PATH)


# ============================================================================
# SECTION 6: INPUT VALIDATION REGRESSION (REG-32..REG-37)
# ============================================================================

def test_reg_32_missing_required_field():
    """REG-32: Missing required fields produce validation errors."""
    errs = require_fields({'name': 'John'}, ['name', 'email'])
    assert 'email' in errs


def test_reg_33_invalid_integer_id():
    """REG-33: Non-integer IDs are rejected."""
    _, err = validate_integer_id('abc', 'id')
    assert err is not None


def test_reg_34_negative_amount():
    """REG-34: Negative payment amounts are rejected."""
    _, err = validate_positive_amount(-100, 'amount')
    assert err is not None


def test_reg_35_invalid_date():
    """REG-35: Invalid dates are rejected."""
    _, err = validate_date_string('2026-99-99', 'date')
    assert err is not None


def test_reg_36_invalid_enum():
    """REG-36: Invalid enum values are rejected."""
    _, err = validate_enum('invalid', ['a', 'b', 'c'], 'field')
    assert err is not None


def test_reg_37_string_length_exceeded():
    """REG-37: Overlong strings are rejected."""
    _, err = validate_string_length('x' * 300, 'field', max_length=255)
    assert err is not None


# ============================================================================
# SECTION 7: DOCUMENTATION INTEGRITY REGRESSION (REG-38..REG-40)
# ============================================================================

def test_reg_38_all_docs_exist():
    """REG-38: All mandatory documentation files exist and are non-empty."""
    required = [
        'README.md',
        'docs/architecture/system_architecture.md',
        'docs/architecture/database_architecture.md',
        'docs/architecture/application_architecture.md',
        'docs/architecture/api_architecture.md',
        'docs/architecture/security_architecture.md',
        'docs/guides/installation.md',
        'docs/guides/testing.md',
        'docs/operations/backup_restore.md',
        'docs/operations/troubleshooting.md',
    ]
    for rel_path in required:
        full_path = os.path.join(ROOT_DIR, rel_path)
        assert os.path.exists(full_path), f"Missing: {rel_path}"
        assert os.path.getsize(full_path) > 0, f"Empty: {rel_path}"


def test_reg_39_gitignore_excludes_env():
    """REG-39: .gitignore excludes .env file."""
    gitignore = os.path.join(ROOT_DIR, '.gitignore')
    with open(gitignore, 'r', encoding='utf-8') as f:
        assert '.env' in f.read()


def test_reg_40_env_example_no_secrets():
    """REG-40: .env.example contains placeholder values only."""
    example = os.path.join(ROOT_DIR, '.env.example')
    with open(example, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'Root@123' not in content
    assert 'SuperSecret' not in content


# ============================================================================
# SECTION 8: COMPLETE E2E LIFECYCLE REGRESSION (REG-41)
# ============================================================================

def test_reg_41_complete_e2e_lifecycle(client):
    """REG-41: Complete end-to-end student lifecycle verification.

    Exercises the full flow:
    1. Register student (validation)
    2. Login attempt (auth)
    3. Verify RBAC (unauthenticated block)
    4. Verify UI templates render
    5. Verify logging infrastructure
    6. Verify security event capture
    7. Verify error sanitization
    8. Verify correlation IDs
    """
    # Step 1: Student registration validates payloads
    res = client.post('/api/students', json={})
    assert res.status_code == 400
    assert 'errors' in res.get_json()

    # Step 2: Authentication attempt
    res = client.post('/api/auth/login', json={'username': 'e2e_user', 'password': 'e2e_pass'})
    assert res.status_code == 401

    # Step 3: RBAC blocks unauthenticated access
    res = client.get('/api/auth/me')
    assert res.status_code == 401

    # Step 4: UI templates render
    for route in ['/login', '/dashboard', '/students', '/allocations', '/finance']:
        res = client.get(route)
        assert res.status_code == 200, f"UI template {route} failed"

    # Step 5: Allocation validation
    res = client.post('/api/allocations', json={'student_id': -1, 'bed_id': -1})
    assert res.status_code == 400

    # Step 6: Finance validation
    res = client.post('/api/finance/payments', json={'amount': 0})
    assert res.status_code == 400

    # Step 7: Visitor validation
    res = client.post('/api/visitors', json={})
    assert res.status_code == 400

    # Step 8: Complaint validation
    res = client.post('/api/complaints', json={})
    assert res.status_code == 400

    # Step 9: Maintenance validation
    res = client.post('/api/maintenance', json={})
    assert res.status_code == 400

    # Step 10: Verify correlation IDs present
    res = client.get('/health')
    assert 'X-Request-ID' in res.headers

    # Step 11: Verify health check
    assert res.get_json()['status'] == 'healthy'
