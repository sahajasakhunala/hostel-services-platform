from flask import Blueprint, request, jsonify
from app.services.complaint_service import ComplaintService

complaints_bp = Blueprint('complaints', __name__)


@complaints_bp.route('', methods=['GET'])
def get_complaints():
    """GET /api/complaints - Retrieve list of student complaints."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        complaints = ComplaintService.get_all_complaints(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(complaints), 'data': complaints}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@complaints_bp.route('/unresolved', methods=['GET'])
def get_unresolved_complaints():
    """GET /api/complaints/unresolved - Retrieve open and in-progress unresolved complaints."""
    try:
        unresolved = ComplaintService.get_unresolved_complaints()
        return jsonify({'status': 'success', 'count': len(unresolved), 'data': unresolved}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@complaints_bp.route('/categories', methods=['GET'])
def get_complaint_categories():
    """GET /api/complaints/categories - Retrieve list of complaint categories."""
    try:
        categories = ComplaintService.get_categories()
        return jsonify({'status': 'success', 'count': len(categories), 'data': categories}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@complaints_bp.route('/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """GET /api/complaints/<id> - Retrieve single complaint details."""
    try:
        complaint = ComplaintService.get_complaint_by_id(complaint_id)
        return jsonify({'status': 'success', 'data': complaint}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@complaints_bp.route('', methods=['POST'])
def file_complaint():
    """POST /api/complaints - File a new student grievance complaint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        complaint = ComplaintService.file_complaint(data)
        return jsonify({'status': 'success', 'message': 'Complaint filed successfully.', 'data': complaint}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@complaints_bp.route('/<int:complaint_id>/status', methods=['PATCH'])
def update_complaint_status(complaint_id):
    """PATCH /api/complaints/<id>/status - Update complaint resolution status and notes."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        complaint = ComplaintService.update_complaint_status(complaint_id, data)
        return jsonify({'status': 'success', 'message': 'Complaint status updated successfully.', 'data': complaint}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
