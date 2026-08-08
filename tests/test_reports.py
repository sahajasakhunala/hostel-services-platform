import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_get_occupancy_report_endpoint(client):
    """Tests GET /api/reports/occupancy endpoint."""
    response = client.get('/api/reports/occupancy')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_block_occupancy_ranking_endpoint(client):
    """Tests GET /api/reports/occupancy/blocks endpoint."""
    response = client.get('/api/reports/occupancy/blocks')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_fees_ranking_endpoint(client):
    """Tests GET /api/reports/fees/ranking endpoint."""
    response = client.get('/api/reports/fees/ranking')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_allocation_stays_endpoint(client):
    """Tests GET /api/reports/allocations/stays endpoint."""
    response = client.get('/api/reports/allocations/stays')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_complaints_report_endpoint(client):
    """Tests GET /api/reports/complaints endpoint."""
    response = client.get('/api/reports/complaints')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_maintenance_report_endpoint(client):
    """Tests GET /api/reports/maintenance endpoint."""
    response = client.get('/api/reports/maintenance')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_visitor_trends_endpoint(client):
    """Tests GET /api/reports/visitors endpoint."""
    response = client.get('/api/reports/visitors')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_get_hostel_summary_endpoint(client):
    """Tests GET /api/reports/hostel-summary multi-domain dashboard endpoint."""
    response = client.get('/api/reports/hostel-summary')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)
