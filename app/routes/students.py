from flask import Blueprint, request, jsonify
from app.services.student_service import StudentService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_enum,
    validate_date_string, validate_string_length, parse_pagination_params
)

students_bp = Blueprint('students', __name__)


@students_bp.route('', methods=['GET'])
def get_students():
    """GET /api/students - Retrieve list of registered students."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        students = StudentService.get_students(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(students), 'data': students}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """GET /api/students/<id> - Retrieve student details by ID."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        student = StudentService.get_student_by_id(val_id)
        return jsonify({'status': 'success', 'data': student}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@students_bp.route('', methods=['POST'])
def register_student():
    """POST /api/students - Register a new resident student."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        required = [
            'registration_number', 'first_name', 'last_name', 'email',
            'phone', 'dob', 'gender', 'department_id', 'course_id', 'academic_year_id'
        ]
        errors = require_fields(data, required)

        if 'gender' in data and data['gender']:
            _, err = validate_enum(data['gender'], ['male', 'female', 'other'], 'gender')
            if err: errors['gender'] = err

        if 'dob' in data and data['dob']:
            _, err = validate_date_string(data['dob'], 'dob')
            if err: errors['dob'] = err

        for id_field in ['department_id', 'course_id', 'academic_year_id']:
            if id_field in data and data[id_field] is not None:
                _, err = validate_integer_id(data[id_field], id_field)
                if err: errors[id_field] = err

        for str_field, max_len in [('registration_number', 50), ('first_name', 50), ('last_name', 50), ('email', 100), ('phone', 20)]:
            if str_field in data and data[str_field]:
                _, err = validate_string_length(data[str_field], str_field, max_length=max_len)
                if err: errors[str_field] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        new_student = StudentService.register_student(data)
        return jsonify({'status': 'success', 'message': 'Student registered successfully.', 'data': new_student}), 201
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if "already registered" in msg.lower() or "already exists" in msg.lower() else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
