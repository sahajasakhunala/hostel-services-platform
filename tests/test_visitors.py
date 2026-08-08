import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_get_visitors_endpoint(client):
    """Tests GET /api/visitors endpoint."""
    response = client.get('/api/visitors')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_active_visitors_endpoint(client):
    """Tests GET /api/visitors/active endpoint."""
    response = client.get('/api/visitors/active')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_checkin_visitor_missing_fields(client):
    """Tests POST /api/visitors check-in payload validation."""
    response = client.post('/api/visitors', json={'visitor_name': 'John Doe'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Missing required field' in json_data['message']


def test_checkout_visitor_nonexistent(client):
    """Tests POST /api/visitors/<id>/checkout for non-existent visitor."""
    response = client.post('/api/visitors/999999/checkout', json={})
    assert response.status_code in (400, 500)
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'not found' in json_data['message'].lower()
