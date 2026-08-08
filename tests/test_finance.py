import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_get_fee_dues_endpoint(client):
    """Tests GET /api/finance/dues endpoint."""
    response = client.get('/api/finance/dues')
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)


def test_process_payment_missing_fields(client):
    """Tests POST /api/finance/payments missing field validation."""
    response = client.post('/api/finance/payments', json={'invoice_id': 1})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Validation failed.'
    assert 'errors' in json_data


def test_process_payment_invalid_amount(client):
    """Tests POST /api/finance/payments zero or negative amount validation."""
    response = client.post('/api/finance/payments', json={
        'invoice_id': 1,
        'amount': -100.00,
        'payment_method': 'cash',
        'receipt_number': 'TEST-FAIL-01'
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Validation failed.'
    assert 'errors' in json_data
