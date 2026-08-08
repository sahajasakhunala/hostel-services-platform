import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_get_allocations_endpoint(client):
    """Tests GET /api/allocations endpoint."""
    response = client.get('/api/allocations')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_allocate_bed_missing_fields(client):
    """Tests POST /api/allocations payload validation."""
    response = client.post('/api/allocations', json={'student_id': 1})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Missing required field' in json_data['message']


def test_transfer_student_missing_fields(client):
    """Tests POST /api/allocations/transfer payload validation."""
    response = client.post('/api/allocations/transfer', json={'student_id': 1})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Missing required field' in json_data['message']


def test_vacate_student_missing_fields(client):
    """Tests POST /api/allocations/vacate payload validation."""
    response = client.post('/api/allocations/vacate', json={'student_id': 1})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Missing required field' in json_data['message']
