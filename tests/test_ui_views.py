import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_login_view(client):
    """Tests GET /login page."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'HostelFlow' in response.data


def test_dashboard_view(client):
    """Tests GET /dashboard page."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Operational Dashboard' in response.data


def test_students_view(client):
    """Tests GET /students page."""
    response = client.get('/students')
    assert response.status_code == 200
    assert b'Resident Student Directory' in response.data


def test_allocations_view(client):
    """Tests GET /allocations page."""
    response = client.get('/allocations')
    assert response.status_code == 200
    assert b'Bed Allocations' in response.data


def test_finance_view(client):
    """Tests GET /finance page."""
    response = client.get('/finance')
    assert response.status_code == 200
    assert b'Finance' in response.data


def test_visitors_view(client):
    """Tests GET /visitors page."""
    response = client.get('/visitors')
    assert response.status_code == 200
    assert b'Gate Security' in response.data


def test_complaints_view(client):
    """Tests GET /complaints page."""
    response = client.get('/complaints')
    assert response.status_code == 200
    assert b'Student Grievance' in response.data


def test_maintenance_view(client):
    """Tests GET /maintenance page."""
    response = client.get('/maintenance')
    assert response.status_code == 200
    assert b'Facility Repair' in response.data


def test_reports_view(client):
    """Tests GET /reports page."""
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Business Intelligence' in response.data
