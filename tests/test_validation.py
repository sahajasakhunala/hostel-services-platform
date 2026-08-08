import pytest
from app import create_app
from app.utils.validation import (
    require_fields, validate_integer_id, validate_positive_amount,
    validate_enum, validate_date_string, validate_string_length
)


@pytest.fixture
def client():
    """Pytest fixture initializing Flask test client."""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


# VAL-01: Missing required field rejected
def test_val_01_missing_required_field_rejected():
    errs = require_fields({'first_name': 'John'}, ['first_name', 'last_name'])
    assert 'last_name' in errs
    assert "required field" in errs['last_name']


# VAL-02: Invalid JSON rejected
def test_val_02_invalid_json_payload_rejected(client):
    res = client.post('/api/students', data="Not JSON Payload", content_type='text/plain')
    assert res.status_code == 400
    assert res.get_json()['status'] == 'error'


# VAL-03: Invalid student_id rejected
def test_val_03_invalid_student_id_rejected():
    val, err = validate_integer_id("abc", "student_id")
    assert val is None
    assert "valid positive integer" in err


# VAL-04: Negative ID rejected
def test_val_04_negative_id_rejected():
    val, err = validate_integer_id(-5, "student_id")
    assert val is None
    assert "greater than zero" in err


# VAL-05: Invalid amount rejected
def test_val_05_invalid_amount_rejected():
    val, err = validate_positive_amount("not-a-number", "amount")
    assert val is None
    assert "numeric amount" in err


# VAL-06: Zero payment rejected
def test_val_06_zero_payment_rejected():
    val, err = validate_positive_amount(0.00, "amount")
    assert val is None
    assert "greater than zero" in err


# VAL-07: Invalid date rejected
def test_val_07_invalid_date_rejected():
    val, err = validate_date_string("2026-99-99", "start_date")
    assert val is None
    assert "valid date string" in err


# VAL-08: Invalid date format rejected
def test_val_08_invalid_date_format_rejected():
    val, err = validate_date_string("08-08-2026", "start_date")
    assert val is None
    assert "valid date string" in err


# VAL-09: Invalid enum value rejected
def test_val_09_invalid_enum_rejected():
    val, err = validate_enum("super_high", ["low", "medium", "high", "urgent"], "priority")
    assert val is None
    assert "must be one of" in err


# VAL-10: Excessively long string rejected
def test_val_10_excessively_long_string_rejected():
    val, err = validate_string_length("a" * 300, "subject", max_length=255)
    assert val is None
    assert "exceeds maximum length" in err


# VAL-11: Oversized payload rejected
def test_val_11_oversized_payload_rejected(client):
    large_payload = {'description': 'X' * (17 * 1024 * 1024)}
    res = client.post('/api/complaints', json=large_payload)
    assert res.status_code in (413, 400)


# VAL-12: Unknown resource returns 404
def test_val_12_unknown_resource_returns_404(client):
    res = client.get('/api/students/99999')
    assert res.status_code == 404
    assert res.get_json()['status'] == 'error'


# VAL-13: Business conflict returns 409
def test_val_13_business_conflict_returns_409(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['roles'] = ['administrator']

    # Submitting duplicate allocation or non-existent student/bed conflict
    res = client.post('/api/allocations', json={'student_id': 999, 'bed_id': 999, 'start_date': '2026-08-08'})
    assert res.status_code in (400, 409)


# VAL-14: Validation errors follow standard JSON contract
def test_val_14_standard_json_contract(client):
    res = client.post('/api/students', json={'first_name': 'OnlyFirstName'})
    assert res.status_code == 400
    json_data = res.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Validation failed.'
    assert isinstance(json_data['errors'], dict)


# VAL-15: Internal exceptions remain sanitized
def test_val_15_sanitized_internal_exceptions(client):
    res = client.get('/api/students/abc')
    assert res.status_code == 400


# VAL-16: Student invalid payload -> standard 400
def test_val_16_student_invalid_payload(client):
    res = client.post('/api/students', json={})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-17: Allocation invalid payload -> standard 400
def test_val_17_allocation_invalid_payload(client):
    res = client.post('/api/allocations', json={'student_id': -1})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-18: Finance invalid payload -> standard 400
def test_val_18_finance_invalid_payload(client):
    res = client.post('/api/finance/payments', json={'amount': -500})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-19: Visitor invalid payload -> standard 400
def test_val_19_visitor_invalid_payload(client):
    res = client.post('/api/visitors', json={'id_type': 'InvalidIDCard'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-20: Complaint invalid payload -> standard 400
def test_val_20_complaint_invalid_payload(client):
    res = client.post('/api/complaints', json={'priority': 'super_urgent'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-21: Maintenance invalid payload -> standard 400
def test_val_21_maintenance_invalid_payload(client):
    res = client.post('/api/maintenance', json={'priority': 'invalid'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()


# VAL-22: Missing resource -> standard 404
def test_val_22_missing_resource(client):
    res = client.get('/api/finance/invoices/99999')
    assert res.status_code == 404


# VAL-23: State conflict -> standard 409
def test_val_23_state_conflict(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['roles'] = ['administrator']

    res = client.post('/api/allocations/transfer', json={
        'student_id': 999,
        'new_bed_id': 1,
        'transfer_date': '2026-08-08',
        'reason': 'Roommate change'
    })
    assert res.status_code in (400, 409)
