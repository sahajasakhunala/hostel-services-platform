from flask import Blueprint, request, jsonify
from app.services.student_service import StudentService

students_bp = Blueprint('students', __name__)


@students_bp.route('', methods=['GET'])
def get_students():
    """GET /api/students - Retrieve list of registered students."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        students = StudentService.get_students(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(students), 'data': students}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """GET /api/students/<id> - Retrieve student details by ID."""
    try:
        student = StudentService.get_student_by_id(student_id)
        return jsonify({'status': 'success', 'data': student}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@students_bp.route('', methods=['POST'])
def register_student():
    """POST /api/students - Register a new resident student."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400
        
        new_student = StudentService.register_student(data)
        return jsonify({'status': 'success', 'message': 'Student registered successfully.', 'data': new_student}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
