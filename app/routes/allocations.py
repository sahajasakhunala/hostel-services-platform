from flask import Blueprint, request, jsonify
from app.services.allocation_service import AllocationService

allocations_bp = Blueprint('allocations', __name__)


@allocations_bp.route('', methods=['GET'])
def get_allocations():
    """GET /api/allocations - Retrieve list of active resident bed allocations."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        allocations = AllocationService.get_active_allocations(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(allocations), 'data': allocations}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@allocations_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_active_allocation(student_id):
    """GET /api/allocations/student/<student_id> - Retrieve current active allocation for a student."""
    try:
        allocation = AllocationService.get_student_active_allocation(student_id)
        if not allocation:
            return jsonify({'status': 'error', 'message': f'No active allocation found for student ID {student_id}.'}), 404
        return jsonify({'status': 'success', 'data': allocation}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@allocations_bp.route('/history/<int:student_id>', methods=['GET'])
def get_student_allocation_history(student_id):
    """GET /api/allocations/history/<student_id> - Retrieve complete stay history for a student."""
    try:
        history = AllocationService.get_student_allocation_history(student_id)
        return jsonify({'status': 'success', 'count': len(history), 'data': history}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@allocations_bp.route('', methods=['POST'])
def allocate_bed():
    """POST /api/allocations - Allocate a bed to a student via sp_allocate_bed."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        result = AllocationService.allocate_bed(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'allocation_id': result['allocation_id']}}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@allocations_bp.route('/transfer', methods=['POST'])
def transfer_student():
    """POST /api/allocations/transfer - Transfer a resident student via sp_transfer_student."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        result = AllocationService.transfer_student(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'transfer_id': result['transfer_id']}}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@allocations_bp.route('/vacate', methods=['POST'])
def vacate_student():
    """POST /api/allocations/vacate - Vacate a resident student via sp_vacate_student."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        result = AllocationService.vacate_student(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'vacating_id': result['vacating_id']}}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
