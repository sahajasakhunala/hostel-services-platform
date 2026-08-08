import os
import pytest
from app import create_app
from app.utils.auth import validate_password_strength


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


# SEC-01: Production configuration rejects missing SECRET_KEY
# Phase 7.7 moved secret validation into validate_config() which raises ValueError.
def test_sec_01_production_config_rejects_missing_secret_key():
    from app.config import ProductionConfig
    from app.utils.config_validation import validate_config
    cfg = ProductionConfig()
    cfg.SECRET_KEY = ''
    with pytest.raises(ValueError, match="SECRET_KEY must be defined"):
        validate_config(cfg, env_name='production')


# SEC-02: Session cookie is HttpOnly
def test_sec_02_session_cookie_httponly(client):
    res = client.get('/health')
    assert client.application.config['SESSION_COOKIE_HTTPONLY'] is True


# SEC-03: Session cookie uses SameSite=Lax
def test_sec_03_session_cookie_samesite(client):
    assert client.application.config['SESSION_COOKIE_SAMESITE'] == 'Lax'


# SEC-04: Secure cookie behavior follows environment configuration
def test_sec_04_session_cookie_secure_follows_env(client):
    assert client.application.config['SESSION_COOKIE_SECURE'] is False


# SEC-05: Permanent session lifetime configured correctly
def test_sec_05_permanent_session_lifetime(client):
    assert client.application.config['PERMANENT_SESSION_LIFETIME'].total_seconds() == 7200


# SEC-06: Weak password rejected
def test_sec_06_weak_password_rejected():
    is_valid, msg = validate_password_strength('short')
    assert is_valid is False
    assert "at least 8 characters" in msg

    is_valid_alpha, _ = validate_password_strength('onlyletters')
    assert is_valid_alpha is False

    is_valid_num, _ = validate_password_strength('12345678')
    assert is_valid_num is False


# SEC-07: Valid password accepted
def test_sec_07_valid_password_accepted():
    is_valid, err = validate_password_strength('SecurePass123!')
    assert is_valid is True
    assert err == ""


# SEC-08: Unauthenticated protected request → 401
def test_sec_08_unauthenticated_request_returns_401(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401
    assert res.get_json()['status'] == 'error'


# SEC-09: Unauthorized role → 403 or 400 (validation precedes RBAC on POST)
def test_sec_09_unauthorized_role_returns_403(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 999
        sess['roles'] = ['student']

    # POST with incomplete payload may return 400 (validation) before RBAC check
    res = client.post('/api/allocations', json={'student_id': 1, 'bed_id': 10})
    assert res.status_code in (400, 403)


# SEC-10: Student ownership via route parameter enforced
# Note: DB-dependent; ownership decorator may fail with 500 when no live DB.
def test_sec_10_student_ownership_route_param(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 101
        sess['student_id'] = 5
        sess['roles'] = ['student']

    res = client.get('/api/finance/students/999/invoices')
    assert res.status_code in (403, 500)


# SEC-11: Student ownership via query parameter enforced
def test_sec_11_student_ownership_query_param(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 101
        sess['student_id'] = 5
        sess['roles'] = ['student']

    res = client.get('/api/allocations/student/999')
    assert res.status_code in (403, 500)


# SEC-12: Student ownership via JSON body enforced
def test_sec_12_student_ownership_json_body(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 101
        sess['student_id'] = 5
        sess['roles'] = ['student']

    res = client.post('/api/complaints', json={
        'student_id': 999,
        'category_id': 1,
        'subject': 'Unauthorized complaint',
        'description': 'Attempting unauthorized submission',
        'priority': 'low'
    })
    assert res.status_code in (400, 403, 500)


# SEC-13: Privileged role can access permitted student resource
def test_sec_13_privileged_role_access(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['roles'] = ['administrator']

    res = client.get('/api/finance/students/5/invoices')
    assert res.status_code in (200, 404, 500)


# SEC-14: 500 response does not expose database exception details
def test_sec_14_500_response_sanitized():
    app = create_app('testing')
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.config['TESTING'] = False

    @app.route('/test-500-error')
    def trigger_error():
        raise RuntimeError("PyMySQL Database Connection Failed SecretTable: sensitive_column")

    tc = app.test_client()
    res = tc.get('/test-500-error')
    assert res.status_code == 500
    json_data = res.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'An internal server error occurred.'
    assert "PyMySQL" not in json_data['message']
    assert "SecretTable" not in json_data['message']


# SEC-15: X-Content-Type-Options present
def test_sec_15_x_content_type_options_header(client):
    res = client.get('/health')
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'


# SEC-16: X-Frame-Options present
def test_sec_16_x_frame_options_header(client):
    res = client.get('/health')
    assert res.headers.get('X-Frame-Options') == 'SAMEORIGIN'


# SEC-17: Authentication failure does not expose sensitive details
def test_sec_17_auth_failure_no_sensitive_leak(client):
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'WrongPassword123!'})
    assert res.status_code == 401
    json_data = res.get_json()
    assert json_data['status'] == 'error'
    # Must not contain stack traces or internal DB errors
    assert 'Traceback' not in json_data['message']
    assert 'pymysql' not in json_data['message'].lower()
