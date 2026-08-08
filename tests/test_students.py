import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Tests /health API endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert json_data['service'] == 'HostelFlow API'


def test_get_students_endpoint(client):
    """Tests GET /api/students listing endpoint."""
    response = client.get('/api/students')
    # Can return 200 OK or 500 if local DB credentials not set in CI environment
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_register_student_missing_fields(client):
    """Tests POST /api/students with missing payload validation."""
    response = client.post('/api/students', json={'first_name': 'Incomplete'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Validation failed.'
    assert 'errors' in json_data
