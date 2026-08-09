from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.decorators import login_required
from app.utils.logging import log_security_event, log_app_event
from app.utils.auth import validate_password_strength

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login - Authenticate user credentials and start session."""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_security_event('AUTH_LOGIN_FAILURE', {'username': username, 'reason': 'Missing credentials'})
        return jsonify({'status': 'error', 'message': 'Username and password are required.'}), 400

    try:
        user_data = AuthService.login(username, password)
        log_security_event('AUTH_LOGIN_SUCCESS', {'username': username, 'user_id': user_data.get('user_id')})
        return jsonify({'status': 'success', 'message': 'Login successful.', 'data': user_data}), 200
    except ValueError as ve:
        log_security_event('AUTH_LOGIN_FAILURE', {'username': username, 'reason': str(ve)})
        return jsonify({'status': 'error', 'message': str(ve)}), 401
    except Exception as e:
        log_security_event('AUTH_LOGIN_FAILURE', {'username': username, 'reason': str(e)})
        return jsonify({'status': 'error', 'message': 'Authentication failed due to server error.'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register - Register a new user account with secure password hashing."""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required.'}), 400

    username = username.strip()
    if len(username) < 3:
        return jsonify({'status': 'error', 'message': 'Username must be at least 3 characters long.'}), 400

    # Validate password complexity
    is_valid, err_msg = validate_password_strength(password)
    if not is_valid:
        return jsonify({'status': 'error', 'message': err_msg}), 400

    try:
        new_user = AuthService.register_user(
            username=username,
            password=password,
            student_id=data.get('student_id'),
            staff_id=data.get('staff_id'),
            role_ids=data.get('role_ids', [1])  # Default to Administrator/User role
        )
        log_security_event('AUTH_ACCOUNT_REGISTERED', {'username': username, 'user_id': new_user.get('user_id')})
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully with encrypted password protection. You can now log in.',
            'data': {'username': new_user['username'], 'user_id': new_user['user_id']}
        }), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 409
    except Exception as e:
        log_security_event('AUTH_REGISTER_ERROR', {'username': username, 'reason': str(e)})
        return jsonify({'status': 'error', 'message': 'Account creation failed due to database server error.'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """POST /api/auth/logout - Terminate user session."""
    try:
        AuthService.logout()
        log_security_event('AUTH_LOGOUT', {'status': 'success'})
        return jsonify({'status': 'success', 'message': 'Logged out successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    """GET /api/auth/me - Retrieve current authenticated user session details."""
    try:
        user = AuthService.get_current_user()
        if not user:
            log_security_event('AUTH_SESSION_EXPIRED', {'reason': 'Session user not found'})
            return jsonify({'status': 'error', 'message': 'User session expired or user account not found.'}), 401
        return jsonify({'status': 'success', 'data': user}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
