from flask import Blueprint, request, jsonify
from app.services.maintenance_service import MaintenanceService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_positive_amount,
    validate_enum, validate_string_length, parse_pagination_params
)

maintenance_bp = Blueprint('maintenance', __name__)


@maintenance_bp.route('', methods=['GET'])
def get_maintenance_requests():
    """GET /api/maintenance - Retrieve list of facility maintenance requests."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        requests = MaintenanceService.get_all_requests(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(requests), 'data': requests}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('/pending', methods=['GET'])
def get_pending_maintenance():
    """GET /api/maintenance/pending - Retrieve pending non-completed repair requests from v_maintenance_status."""
    try:
        pending = MaintenanceService.get_pending_requests()
        return jsonify({'status': 'success', 'count': len(pending), 'data': pending}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('/staff', methods=['GET'])
def get_maintenance_staff():
    """GET /api/maintenance/staff - Retrieve list of maintenance staff."""
    try:
        staff = MaintenanceService.get_staff()
        return jsonify({'status': 'success', 'count': len(staff), 'data': staff}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('/<int:request_id>', methods=['GET'])
def get_maintenance_request(request_id):
    """GET /api/maintenance/<id> - Retrieve single maintenance request details."""
    try:
        val_id, err = validate_integer_id(request_id, 'request_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'request_id': err}}), 400
        maint_req = MaintenanceService.get_request_by_id(val_id)
        return jsonify({'status': 'success', 'data': maint_req}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('', methods=['POST'])
def create_maintenance_request():
    """POST /api/maintenance - Create a new facility repair request."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['room_id', 'category', 'description', 'priority'])

        if 'room_id' in data and data['room_id'] is not None:
            _, err = validate_integer_id(data['room_id'], 'room_id')
            if err: errors['room_id'] = err

        if 'priority' in data and data['priority']:
            allowed_priorities = ['low', 'medium', 'high', 'urgent']
            _, err = validate_enum(data['priority'], allowed_priorities, 'priority')
            if err: errors['priority'] = err

        for str_field, max_len in [('category', 50), ('description', 255)]:
            if str_field in data and data[str_field]:
                _, err = validate_string_length(data[str_field], str_field, max_length=max_len)
                if err: errors[str_field] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        maint_req = MaintenanceService.create_request(data)
        return jsonify({'status': 'success', 'message': 'Maintenance request created successfully.', 'data': maint_req}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('/<int:request_id>/assign', methods=['PATCH'])
def assign_maintenance_staff(request_id):
    """PATCH /api/maintenance/<id>/assign - Assign repair staff to a maintenance request."""
    try:
        val_id, err = validate_integer_id(request_id, 'request_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'request_id': err}}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['assigned_staff_id'])

        if 'assigned_staff_id' in data and data['assigned_staff_id'] is not None:
            _, err = validate_integer_id(data['assigned_staff_id'], 'assigned_staff_id')
            if err: errors['assigned_staff_id'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        maint_req = MaintenanceService.assign_staff(val_id, data)
        return jsonify({'status': 'success', 'message': 'Staff assigned to maintenance request successfully.', 'data': maint_req}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 404 if 'not found' in msg.lower() else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@maintenance_bp.route('/<int:request_id>/status', methods=['PATCH'])
def update_maintenance_status(request_id):
    """PATCH /api/maintenance/<id>/status - Update maintenance request status and cost."""
    try:
        val_id, err = validate_integer_id(request_id, 'request_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'request_id': err}}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['status'])

        if 'status' in data and data['status']:
            allowed_statuses = ['assigned', 'in_progress', 'completed', 'cancelled']
            _, err = validate_enum(data['status'], allowed_statuses, 'status')
            if err: errors['status'] = err

        if 'cost' in data and data['cost'] is not None:
            _, err = validate_positive_amount(data['cost'], 'cost')
            if err: errors['cost'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        maint_req = MaintenanceService.update_request_status(val_id, data)
        return jsonify({'status': 'success', 'message': 'Maintenance status updated successfully.', 'data': maint_req}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 404 if 'not found' in msg.lower() else (409 if 'already completed' in msg.lower() else 400)
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
