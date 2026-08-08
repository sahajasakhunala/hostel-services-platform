from flask import Blueprint, request, jsonify
from app.services.maintenance_service import MaintenanceService

maintenance_bp = Blueprint('maintenance', __name__)


@maintenance_bp.route('', methods=['GET'])
def get_maintenance_requests():
    """GET /api/maintenance - Retrieve list of facility maintenance requests."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        requests = MaintenanceService.get_all_requests(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(requests), 'data': requests}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('/pending', methods=['GET'])
def get_pending_maintenance():
    """GET /api/maintenance/pending - Retrieve pending non-completed repair requests from v_maintenance_status."""
    try:
        pending = MaintenanceService.get_pending_requests()
        return jsonify({'status': 'success', 'count': len(pending), 'data': pending}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('/staff', methods=['GET'])
def get_maintenance_staff():
    """GET /api/maintenance/staff - Retrieve list of maintenance staff."""
    try:
        staff = MaintenanceService.get_staff()
        return jsonify({'status': 'success', 'count': len(staff), 'data': staff}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('/<int:request_id>', methods=['GET'])
def get_maintenance_request(request_id):
    """GET /api/maintenance/<id> - Retrieve single maintenance request details."""
    try:
        maint_req = MaintenanceService.get_request_by_id(request_id)
        return jsonify({'status': 'success', 'data': maint_req}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('', methods=['POST'])
def create_maintenance_request():
    """POST /api/maintenance - Create a new facility repair request."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        maint_req = MaintenanceService.create_request(data)
        return jsonify({'status': 'success', 'message': 'Maintenance request created successfully.', 'data': maint_req}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('/<int:request_id>/assign', methods=['PATCH'])
def assign_maintenance_staff(request_id):
    """PATCH /api/maintenance/<id>/assign - Assign repair staff to a maintenance request."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        maint_req = MaintenanceService.assign_staff(request_id, data)
        return jsonify({'status': 'success', 'message': 'Staff assigned to maintenance request successfully.', 'data': maint_req}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@maintenance_bp.route('/<int:request_id>/status', methods=['PATCH'])
def update_maintenance_status(request_id):
    """PATCH /api/maintenance/<id>/status - Update maintenance request status and cost."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        maint_req = MaintenanceService.update_request_status(request_id, data)
        return jsonify({'status': 'success', 'message': 'Maintenance status updated successfully.', 'data': maint_req}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
