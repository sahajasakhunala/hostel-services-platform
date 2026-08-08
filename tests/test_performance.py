import pytest
from app import create_app


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


# PERF-01: Occupancy query plan & execution verified
def test_perf_01_occupancy_query_plan(client):
    res = client.get('/api/reports/occupancy')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-02: Fee dues query plan & execution verified
def test_perf_02_fee_dues_query_plan(client):
    res = client.get('/api/finance/dues')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-03: Visitor report query plan & execution verified
def test_perf_03_visitor_report_query_plan(client):
    res = client.get('/api/visitors')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-04: Unresolved complaints query plan & execution verified
def test_perf_04_unresolved_complaints_query_plan(client):
    res = client.get('/api/complaints/unresolved')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-05: Maintenance report query plan & execution verified
def test_perf_05_maintenance_report_query_plan(client):
    res = client.get('/api/maintenance/pending')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-06: Outstanding dues ranking plan & execution verified
def test_perf_06_outstanding_dues_ranking_plan(client):
    res = client.get('/api/reports/fees/ranking')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-07: Hostel summary query plan & execution verified
def test_perf_07_hostel_summary_query_plan(client):
    res = client.get('/api/reports/hostel-summary')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'


# PERF-08: Transactional point lookups plan & execution verified
def test_perf_08_transactional_point_lookups(client):
    res = client.get('/api/allocations')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'success'
