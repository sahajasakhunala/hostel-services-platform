from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login - Authenticate user credentials and start session."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        username = data.get('username')
        password = data.get('password')

        user_data = AuthService.login(username, password)
        return jsonify({'status': 'success', 'message': 'Login successful.', 'data': user_data}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """POST /api/auth/logout - Terminate user session."""
    try:
        AuthService.logout()
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
            return jsonify({'status': 'error', 'message': 'User session expired or user account not found.'}), 401
        return jsonify({'status': 'success', 'data': user}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
