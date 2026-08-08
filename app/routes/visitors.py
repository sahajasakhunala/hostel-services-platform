from flask import Blueprint, request, jsonify
from app.services.visitor_service import VisitorService

visitors_bp = Blueprint('visitors', __name__)


@visitors_bp.route('', methods=['GET'])
def get_visitors():
    """GET /api/visitors - Retrieve visitor logs."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        visitors = VisitorService.get_visitor_report(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@visitors_bp.route('/active', methods=['GET'])
def get_active_visitors():
    """GET /api/visitors/active - Retrieve list of currently checked-in visitors."""
    try:
        visitors = VisitorService.get_active_visitors()
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@visitors_bp.route('/<int:visitor_id>', methods=['GET'])
def get_visitor(visitor_id):
    """GET /api/visitors/<id> - Retrieve single visitor record by ID."""
    try:
        visitor = VisitorService.get_visitor_by_id(visitor_id)
        return jsonify({'status': 'success', 'data': visitor}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@visitors_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_visitors(student_id):
    """GET /api/visitors/student/<student_id> - Retrieve visitor log for a specific student."""
    try:
        visitors = VisitorService.get_student_visitors(student_id)
        return jsonify({'status': 'success', 'count': len(visitors), 'data': visitors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@visitors_bp.route('', methods=['POST'])
def checkin_visitor():
    """POST /api/visitors - Register gate security check-in for a visitor."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        visitor = VisitorService.checkin_visitor(data)
        return jsonify({'status': 'success', 'message': 'Visitor checked in successfully.', 'data': visitor}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@visitors_bp.route('/<int:visitor_id>/checkout', methods=['POST'])
def checkout_visitor(visitor_id):
    """POST /api/visitors/<id>/checkout - Register gate security check-out for a visitor."""
    try:
        data = request.get_json() or {}
        check_out_time = data.get('check_out_time', None)
        visitor = VisitorService.checkout_visitor(visitor_id, check_out_time=check_out_time)
        return jsonify({'status': 'success', 'message': 'Visitor checked out successfully.', 'data': visitor}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
