from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.decorators import login_required
from app.utils.logging import log_security_event, log_app_event

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login - Authenticate user credentials and start session."""
    try:
        data = request.get_json()
        if not data:
            log_security_event('AUTH_LOGIN_FAILURE', {'reason': 'Empty or invalid JSON payload'})
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        username = data.get('username')
        password = data.get('password')

        user_data = AuthService.login(username, password)
        log_security_event('AUTH_LOGIN_SUCCESS', {'username': username, 'user_id': user_data.get('user_id')})
        return jsonify({'status': 'success', 'message': 'Login successful.', 'data': user_data}), 200
    except ValueError as ve:
        log_security_event('AUTH_LOGIN_FAILURE', {'username': data.get('username') if data else None, 'reason': str(ve)})
        return jsonify({'status': 'error', 'message': str(ve)}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


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
