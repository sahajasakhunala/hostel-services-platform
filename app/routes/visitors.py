from flask import Blueprint, request, jsonify
from app.services.visitor_service import VisitorService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_enum,
    validate_string_length, parse_pagination_params
)

visitors_bp = Blueprint('visitors', __name__)


@visitors_bp.route('', methods=['GET'])
def get_visitors():
    """GET /api/visitors - Retrieve visitor logs."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        visitors = VisitorService.get_visitor_report(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@visitors_bp.route('/active', methods=['GET'])
def get_active_visitors():
    """GET /api/visitors/active - Retrieve list of currently checked-in visitors."""
    try:
        visitors = VisitorService.get_active_visitors()
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@visitors_bp.route('/<int:visitor_id>', methods=['GET'])
def get_visitor(visitor_id):
    """GET /api/visitors/<id> - Retrieve single visitor record by ID."""
    try:
        val_id, err = validate_integer_id(visitor_id, 'visitor_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'visitor_id': err}}), 400
        visitor = VisitorService.get_visitor_by_id(val_id)
        return jsonify({'status': 'success', 'data': visitor}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@visitors_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_visitors(student_id):
    """GET /api/visitors/student/<student_id> - Retrieve visitor log for a specific student."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        visitors = VisitorService.get_student_visitors(val_id)
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@visitors_bp.route('', methods=['POST'])
def checkin_visitor():
    """POST /api/visitors - Register gate security check-in for a visitor."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['student_id', 'visitor_name', 'phone', 'id_type', 'id_number', 'purpose'])

        if 'student_id' in data and data['student_id'] is not None:
            _, err = validate_integer_id(data['student_id'], 'student_id')
            if err: errors['student_id'] = err

        if 'id_type' in data and data['id_type']:
            allowed_types = ['Aadhaar', 'PAN', 'DrivingLicense', 'Passport']
            _, err = validate_enum(data['id_type'], allowed_types, 'id_type')
            if err: errors['id_type'] = err

        for str_field, max_len in [('visitor_name', 100), ('phone', 20), ('id_number', 50), ('purpose', 255)]:
            if str_field in data and data[str_field]:
                _, err = validate_string_length(data[str_field], str_field, max_length=max_len)
                if err: errors[str_field] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        visitor = VisitorService.checkin_visitor(data)
        return jsonify({'status': 'success', 'message': 'Visitor checked in successfully.', 'data': visitor}), 201
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if 'already checked in' in msg.lower() else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@visitors_bp.route('/<int:visitor_id>/checkout', methods=['POST'])
def checkout_visitor(visitor_id):
    """POST /api/visitors/<id>/checkout - Register gate security check-out for a visitor."""
    try:
        val_id, err = validate_integer_id(visitor_id, 'visitor_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'visitor_id': err}}), 400

        data = request.get_json(silent=True) or {}
        check_out_time = data.get('check_out_time', None)

        visitor = VisitorService.checkout_visitor(val_id, check_out_time=check_out_time)
        return jsonify({'status': 'success', 'message': 'Visitor checked out successfully.', 'data': visitor}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if 'already checked out' in msg.lower() else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
