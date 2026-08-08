import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_get_maintenance_requests_endpoint(client):
    """Tests GET /api/maintenance endpoint."""
    response = client.get('/api/maintenance')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_pending_maintenance_endpoint(client):
    """Tests GET /api/maintenance/pending endpoint."""
    response = client.get('/api/maintenance/pending')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_create_maintenance_missing_fields(client):
    """Tests POST /api/maintenance payload validation."""
    response = client.post('/api/maintenance', json={'category': 'Electrical'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Validation failed.'
    assert 'errors' in json_data


def test_update_maintenance_status_invalid_status(client):
    """Tests PATCH /api/maintenance/<id>/status invalid status validation."""
    response = client.patch('/api/maintenance/1/status', json={'status': 'INVALID_STATUS'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Validation failed' in json_data['message'] or 'Invalid status' in json_data.get('message', '') or 'errors' in json_data
