from flask import Blueprint, request, jsonify
from app.services.allocation_service import AllocationService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_enum,
    validate_date_string, validate_string_length, parse_pagination_params
)

allocations_bp = Blueprint('allocations', __name__)


@allocations_bp.route('', methods=['GET'])
def get_allocations():
    """GET /api/allocations - Retrieve list of active resident bed allocations."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        allocations = AllocationService.get_active_allocations(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(allocations), 'data': allocations}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@allocations_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_active_allocation(student_id):
    """GET /api/allocations/student/<student_id> - Retrieve current active allocation for a student."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        allocation = AllocationService.get_student_active_allocation(val_id)
        if not allocation:
            return jsonify({'status': 'error', 'message': f'No active allocation found for student ID {student_id}.'}), 404
        return jsonify({'status': 'success', 'data': allocation}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@allocations_bp.route('/history/<int:student_id>', methods=['GET'])
def get_student_allocation_history(student_id):
    """GET /api/allocations/history/<student_id> - Retrieve complete stay history for a student."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        history = AllocationService.get_student_allocation_history(val_id)
        return jsonify({'status': 'success', 'count': len(history), 'data': history}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@allocations_bp.route('', methods=['POST'])
def allocate_bed():
    """POST /api/allocations - Allocate a bed to a student via sp_allocate_bed."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['student_id', 'bed_id', 'start_date'])

        if 'student_id' in data and data['student_id'] is not None:
            _, err = validate_integer_id(data['student_id'], 'student_id')
            if err: errors['student_id'] = err

        if 'bed_id' in data and data['bed_id'] is not None:
            _, err = validate_integer_id(data['bed_id'], 'bed_id')
            if err: errors['bed_id'] = err

        if 'start_date' in data and data['start_date']:
            _, err = validate_date_string(data['start_date'], 'start_date')
            if err: errors['start_date'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        result = AllocationService.allocate_bed(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'allocation_id': result['allocation_id']}}), 201
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if any(k in msg.lower() for k in ['already', 'occupied', 'active', 'conflict', 'capacity']) else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@allocations_bp.route('/transfer', methods=['POST'])
def transfer_student():
    """POST /api/allocations/transfer - Transfer a resident student via sp_transfer_student."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['student_id', 'new_bed_id', 'transfer_date', 'reason'])

        if 'student_id' in data and data['student_id'] is not None:
            _, err = validate_integer_id(data['student_id'], 'student_id')
            if err: errors['student_id'] = err

        if 'new_bed_id' in data and data['new_bed_id'] is not None:
            _, err = validate_integer_id(data['new_bed_id'], 'new_bed_id')
            if err: errors['new_bed_id'] = err

        if 'transfer_date' in data and data['transfer_date']:
            _, err = validate_date_string(data['transfer_date'], 'transfer_date')
            if err: errors['transfer_date'] = err

        if 'reason' in data and data['reason']:
            _, err = validate_string_length(data['reason'], 'reason', max_length=255)
            if err: errors['reason'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        result = AllocationService.transfer_student(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'transfer_id': result['transfer_id']}}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if any(k in msg.lower() for k in ['already', 'occupied', 'no active', 'conflict']) else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@allocations_bp.route('/vacate', methods=['POST'])
def vacate_student():
    """POST /api/allocations/vacate - Vacate a resident student via sp_vacate_student."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['student_id', 'vacating_date', 'clearance_status', 'reason'])

        if 'student_id' in data and data['student_id'] is not None:
            _, err = validate_integer_id(data['student_id'], 'student_id')
            if err: errors['student_id'] = err

        if 'vacating_date' in data and data['vacating_date']:
            _, err = validate_date_string(data['vacating_date'], 'vacating_date')
            if err: errors['vacating_date'] = err

        if 'clearance_status' in data and data['clearance_status']:
            _, err = validate_enum(data['clearance_status'], ['cleared', 'pending_dues'], 'clearance_status')
            if err: errors['clearance_status'] = err

        if 'reason' in data and data['reason']:
            _, err = validate_string_length(data['reason'], 'reason', max_length=255)
            if err: errors['reason'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        result = AllocationService.vacate_student(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'vacating_id': result['vacating_id']}}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if any(k in msg.lower() for k in ['no active', 'already vacated', 'pending dues', 'conflict']) else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
