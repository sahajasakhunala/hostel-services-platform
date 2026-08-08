import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_login_invalid_credentials(client):
    """Tests POST /api/auth/login with wrong credentials returning 401 Unauthorized."""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent_user',
        'password': 'WrongPassword123'
    })
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Invalid username or password' in json_data['message']


def test_login_missing_payload(client):
    """Tests POST /api/auth/login with missing username/password."""
    response = client.post('/api/auth/login', json={'username': 'admin'})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['status'] == 'error'


def test_unauthenticated_protected_endpoint(client):
    """Tests accessing /api/auth/me without active session returning 401 Unauthorized."""
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Authentication required' in json_data['message']


def test_logout_endpoint(client):
    """Tests POST /api/auth/logout clearing session."""
    response = client.post('/api/auth/logout')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'Logged out' in json_data['message']
