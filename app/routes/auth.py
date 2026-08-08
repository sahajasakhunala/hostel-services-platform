from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.decorators import login_required
from app.utils.logging import log_security_event, log_app_event

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
