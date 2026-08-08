from flask import Blueprint, request, jsonify
from app.services.complaint_service import ComplaintService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_enum,
    validate_string_length, parse_pagination_params
)

complaints_bp = Blueprint('complaints', __name__)


@complaints_bp.route('', methods=['GET'])
def get_complaints():
    """GET /api/complaints - Retrieve list of student complaints."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        complaints = ComplaintService.get_all_complaints(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(complaints), 'data': complaints}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@complaints_bp.route('/unresolved', methods=['GET'])
def get_unresolved_complaints():
    """GET /api/complaints/unresolved - Retrieve open and in-progress unresolved complaints."""
    try:
        unresolved = ComplaintService.get_unresolved_complaints()
        return jsonify({'status': 'success', 'count': len(unresolved), 'data': unresolved}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@complaints_bp.route('/categories', methods=['GET'])
def get_complaint_categories():
    """GET /api/complaints/categories - Retrieve list of complaint categories."""
    try:
        categories = ComplaintService.get_categories()
        return jsonify({'status': 'success', 'count': len(categories), 'data': categories}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@complaints_bp.route('/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """GET /api/complaints/<id> - Retrieve single complaint details."""
    try:
        val_id, err = validate_integer_id(complaint_id, 'complaint_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'complaint_id': err}}), 400
        complaint = ComplaintService.get_complaint_by_id(val_id)
        return jsonify({'status': 'success', 'data': complaint}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@complaints_bp.route('', methods=['POST'])
def file_complaint():
    """POST /api/complaints - File a new student grievance complaint."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['student_id', 'category_id', 'subject', 'description', 'priority'])

        if 'student_id' in data and data['student_id'] is not None:
            _, err = validate_integer_id(data['student_id'], 'student_id')
            if err: errors['student_id'] = err

        if 'category_id' in data and data['category_id'] is not None:
            _, err = validate_integer_id(data['category_id'], 'category_id')
            if err: errors['category_id'] = err

        if 'priority' in data and data['priority']:
            allowed_priorities = ['low', 'medium', 'high', 'urgent']
            _, err = validate_enum(data['priority'], allowed_priorities, 'priority')
            if err: errors['priority'] = err

        if 'subject' in data and data['subject']:
            _, err = validate_string_length(data['subject'], 'subject', max_length=255)
            if err: errors['subject'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        complaint = ComplaintService.file_complaint(data)
        return jsonify({'status': 'success', 'message': 'Complaint filed successfully.', 'data': complaint}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@complaints_bp.route('/<int:complaint_id>/status', methods=['PATCH'])
def update_complaint_status(complaint_id):
    """PATCH /api/complaints/<id>/status - Update complaint resolution status and notes."""
    try:
        val_id, err = validate_integer_id(complaint_id, 'complaint_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'complaint_id': err}}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['status'])

        if 'status' in data and data['status']:
            allowed_statuses = ['open', 'in_progress', 'resolved', 'cancelled']
            _, err = validate_enum(data['status'], allowed_statuses, 'status')
            if err: errors['status'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        complaint = ComplaintService.update_complaint_status(val_id, data)
        return jsonify({'status': 'success', 'message': 'Complaint status updated successfully.', 'data': complaint}), 200
    except ValueError as ve:
        msg = str(ve)
        status_code = 404 if 'not found' in msg.lower() else (409 if 'already resolved' in msg.lower() else 400)
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
