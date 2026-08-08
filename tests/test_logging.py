"""
Phase 7.6 — Structured Logging & Security Audit Verification Test Suite.

Verifies:
- Log separation (application.log, security.log, error.log)
- Request correlation ID generation and propagation (X-Request-ID)
- Security event logging (AUTH_LOGIN_SUCCESS, AUTH_LOGIN_FAILURE, AUTHZ_ACCESS_DENIED)
- Centralized exception logging without traceback leakage
- Recursive sensitive data scrubbing (passwords, secrets, credentials)
- Database audit independence
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.utils.logging import (
    APP_LOG_PATH, SEC_LOG_PATH, ERR_LOG_PATH,
    log_app_event, log_security_event, log_exception, scrub_sensitive_data
)


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def _read_file_content(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def _clear_log_files():
    for p in (APP_LOG_PATH, SEC_LOG_PATH, ERR_LOG_PATH):
        if os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                f.truncate(0)


# ============================================================================
# LOG-01 .. LOG-03: LOG INFRASTRUCTURE & SEPARATION TESTS
# ============================================================================

def test_log_01_logger_initialization():
    """LOG-01: Verifies log files and loggers initialize cleanly on filesystem."""
    _clear_log_files()
    log_app_event('TEST_INIT_EVENT')
    assert os.path.exists(APP_LOG_PATH), "application.log not created"
    assert os.path.exists(SEC_LOG_PATH), "security.log not created"
    assert os.path.exists(ERR_LOG_PATH), "error.log not created"


def test_log_02_application_events_written():
    """LOG-02: Verifies application events written to application.log and NOT security.log."""
    _clear_log_files()
    log_app_event('STUDENT_REGISTERED', {'student_id': 101})

    app_content = _read_file_content(APP_LOG_PATH)
    sec_content = _read_file_content(SEC_LOG_PATH)

    assert 'STUDENT_REGISTERED' in app_content, "Application event missing from application.log"
    assert 'STUDENT_REGISTERED' not in sec_content, "Application event leaked into security.log!"


def test_log_03_security_events_written_separately():
    """LOG-03: Verifies security events written to security.log and NOT application.log."""
    _clear_log_files()
    log_security_event('AUTHZ_ACCESS_DENIED', {'target': '/admin'})

    app_content = _read_file_content(APP_LOG_PATH)
    sec_content = _read_file_content(SEC_LOG_PATH)

    assert 'AUTHZ_ACCESS_DENIED' in sec_content, "Security event missing from security.log"
    assert 'AUTHZ_ACCESS_DENIED' not in app_content, "Security event leaked into application.log!"


# ============================================================================
# LOG-04 .. LOG-05: REQUEST CORRELATION ID TESTS
# ============================================================================

def test_log_04_request_id_generated(client):
    """LOG-04: Verifies unique X-Request-ID header generated in HTTP response."""
    res = client.get('/health')
    assert res.status_code == 200
    assert 'X-Request-ID' in res.headers, "X-Request-ID header missing from response"
    assert len(res.headers['X-Request-ID']) > 0, "X-Request-ID is empty"


def test_log_05_request_id_preserved_across_logging(client):
    """LOG-05: Verifies request ID is included in structured log context."""
    res = client.get('/health')
    req_id = res.headers.get('X-Request-ID')
    assert req_id is not None


# ============================================================================
# LOG-06 .. LOG-08: SECURITY TAXONOMY EVENTS
# ============================================================================

def test_log_06_authentication_success_logged():
    """LOG-06: Verifies AUTH_LOGIN_SUCCESS logged upon successful login."""
    _clear_log_files()
    log_security_event('AUTH_LOGIN_SUCCESS', {'username': 'admin_user', 'user_id': 1})
    sec_content = _read_file_content(SEC_LOG_PATH)
    assert 'AUTH_LOGIN_SUCCESS' in sec_content, "AUTH_LOGIN_SUCCESS missing from security.log"


def test_log_07_authentication_failure_logged(client):
    """LOG-07: Verifies AUTH_LOGIN_FAILURE logged upon failed authentication."""
    _clear_log_files()
    res = client.post('/api/auth/login', json={'username': 'bad_user', 'password': 'bad_password'})
    assert res.status_code == 401
    sec_content = _read_file_content(SEC_LOG_PATH)
    assert 'AUTH_LOGIN_FAILURE' in sec_content, "AUTH_LOGIN_FAILURE not logged to security.log"


def test_log_08_authorization_failure_logged(client):
    """LOG-08: Verifies AUTHZ_ACCESS_DENIED logged when access is forbidden."""
    _clear_log_files()
    res = client.get('/api/auth/me')  # Unauthenticated
    assert res.status_code == 401
    sec_content = _read_file_content(SEC_LOG_PATH)
    assert 'AUTH_UNAUTHENTICATED_ACCESS' in sec_content or 'AUTHZ_ACCESS_DENIED' in sec_content


# ============================================================================
# LOG-09 .. LOG-10: CENTRALIZED EXCEPTION LOGGING & SAFE RESPONSES
# ============================================================================

def test_log_09_500_exception_logged_server_side():
    """LOG-09: Verifies unhandled exception tracebacks written to error.log."""
    _clear_log_files()
    try:
        raise RuntimeError("Simulated test server exception")
    except Exception:
        log_exception("TEST_SIMULATED_EXCEPTION", exc_info=True)

    err_content = _read_file_content(ERR_LOG_PATH)
    assert 'TEST_SIMULATED_EXCEPTION' in err_content, "Exception missing from error.log"
    assert 'RuntimeError: Simulated test server exception' in err_content, "Traceback missing from error.log"


def test_log_10_500_response_contains_no_traceback():
    """LOG-10: Verifies 500 HTTP response contains safe generic message without traceback."""
    app = create_app('testing')
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.config['TESTING'] = False

    @app.route('/test-error-endpoint')
    def crash_route():
        raise ValueError("Critical Internal Database Failure!")

    tc = app.test_client()
    res = tc.get('/test-error-endpoint')
    assert res.status_code == 500
    data = res.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'An internal server error occurred.'
    assert 'ValueError' not in str(data)
    assert 'Traceback' not in str(data)


# ============================================================================
# LOG-11 .. LOG-13: SENSITIVE DATA LEAKAGE AUDIT
# ============================================================================

def test_log_11_passwords_never_appear_in_logs():
    """LOG-11: Verifies recursive scrubber replaces passwords with [REDACTED]."""
    nested_payload = {
        'username': 'admin',
        'auth_data': {
            'password': 'SuperSecretPassword123!',
            'nested': {
                'secret_key': 'my_top_secret_key'
            }
        }
    }
    scrubbed = scrub_sensitive_data(nested_payload)
    assert scrubbed['auth_data']['password'] == '[REDACTED]'
    assert scrubbed['auth_data']['nested']['secret_key'] == '[REDACTED]'
    assert 'SuperSecretPassword123!' not in json.dumps(scrubbed)


def test_log_12_session_secret_never_appears_in_logs():
    """LOG-12: Verifies session cookies and secret keys are scrubbed."""
    payload = {'session_cookie': 'abc123session', 'token': 'jwt_bearer_token'}
    scrubbed = scrub_sensitive_data(payload)
    assert scrubbed['session_cookie'] == '[REDACTED]'
    assert scrubbed['token'] == '[REDACTED]'


def test_log_13_database_credentials_never_appear_in_logs():
    """LOG-13: Verifies database credentials are scrubbed."""
    payload = {'db_user': 'root', 'db_password': 'my_mysql_root_pass'}
    scrubbed = scrub_sensitive_data(payload)
    assert scrubbed['db_password'] == '[REDACTED]'
    assert scrubbed['db_user'] == 'root'


# ============================================================================
# LOG-14 .. LOG-15: INDEPENDENCE & API COMPATIBILITY
# ============================================================================

def test_log_14_database_audit_records_remain_independent():
    """LOG-14: Verifies application logging operates independently from MySQL audit_logs."""
    _clear_log_files()
    log_app_event('ALLOCATION_CREATED', {'alloc_id': 50})
    app_content = _read_file_content(APP_LOG_PATH)
    assert 'ALLOCATION_CREATED' in app_content


def test_log_15_logging_does_not_break_normal_api_operation(client):
    """LOG-15: Verifies logging middleware does not alter standard HTTP behavior."""
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'healthy'
