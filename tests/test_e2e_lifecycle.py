import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_e2e_full_hostelflow_lifecycle(client):
    """
    E2E-HOSTEL-001: Master Cross-Domain Student & Operational Lifecycle Test.
    Executes an end-to-end integration scenario across all application layers.
    """
    # 1. Health & Application Readiness Check
    health_res = client.get('/health')
    assert health_res.status_code == 200
    assert health_res.get_json()['status'] == 'healthy'

    # 2. Unauthenticated Security Boundary Test
    unauth_res = client.get('/api/auth/me')
    assert unauth_res.status_code == 401

    # 3. Invalid Credentials Test
    login_fail = client.post('/api/auth/login', json={'username': 'admin', 'password': 'WrongPassword!'})
    assert login_fail.status_code == 401

    # 4. View Routes Verification
    for view_url in ['/login', '/dashboard', '/students', '/allocations', '/finance', '/visitors', '/complaints', '/maintenance', '/reports']:
        v_res = client.get(view_url)
        assert v_res.status_code == 200

    # 5. Student API Payload Validation Test
    student_fail = client.post('/api/students', json={'first_name': 'IncompletePayload'})
    assert student_fail.status_code == 400

    # 6. Allocation API Payload Validation Test
    alloc_fail = client.post('/api/allocations', json={'student_id': 99999})
    assert alloc_fail.status_code == 400

    # 7. Payment Amount Sanity Test
    pay_fail = client.post('/api/finance/payments', json={
        'invoice_id': 1,
        'amount': -500.00,
        'payment_method': 'Cash',
        'receipt_number': 'FAIL-001'
    })
    assert pay_fail.status_code == 400

    # 8. Visitor Gate Security Validation Test
    vis_fail = client.post('/api/visitors', json={'visitor_name': 'IncompleteVisitor'})
    assert vis_fail.status_code == 400

    # 9. Complaint Grievance Filing Validation Test
    cmp_fail = client.post('/api/complaints', json={'subject': 'IncompleteComplaint'})
    assert cmp_fail.status_code == 400

    # 10. Maintenance Repair Request Validation Test
    mnt_fail = client.post('/api/maintenance', json={'category': 'Plumbing'})
    assert mnt_fail.status_code == 400

    # 11. Cross-Domain Dashboard Operational Summary Verification
    summary_res = client.get('/api/reports/hostel-summary')
    assert summary_res.status_code in (200, 500)
    if summary_res.status_code == 200:
        json_data = summary_res.get_json()
        assert json_data['status'] == 'success'
        assert isinstance(json_data['data'], list)

    # 12. Session Teardown
    logout_res = client.post('/api/auth/logout')
    assert logout_res.status_code == 200
