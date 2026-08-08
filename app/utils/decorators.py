from functools import wraps
from flask import session, jsonify, request


def login_required(f):
    """
    Decorator requiring active Flask user session authentication.
    Returns HTTP 401 Unauthorized if user is unauthenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] is None:
            return jsonify({'status': 'error', 'message': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator enforcing Role-Based Access Control (RBAC).
    Checks user roles loaded from MySQL user_roles table.
    Returns HTTP 403 Forbidden if user lacks permitted role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session['user_id'] is None:
                return jsonify({'status': 'error', 'message': 'Authentication required. Please log in.'}), 401

            user_roles = [r.lower() for r in session.get('roles', [])]
            permitted = [r.lower() for r in allowed_roles]

            # Standardized role alias mappings for flexibility
            role_aliases = {
                'admin': 'administrator',
                'administrator': 'admin',
                'warden': 'warden',
                'manager': 'warden',
                'security': 'security staff',
                'security staff': 'security',
                'maintenance': 'maintenance staff',
                'maintenance staff': 'maintenance',
                'student': 'student'
            }

            expanded_permitted = set()
            for r in permitted:
                expanded_permitted.add(r)
                if r in role_aliases:
                    expanded_permitted.add(role_aliases[r])

            has_access = any(r in expanded_permitted for r in user_roles)

            if not has_access:
                return jsonify({'status': 'error', 'message': 'Access forbidden: Insufficient role permissions.'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def student_ownership_required(f):
    """
    Decorator enforcing resource ownership authorization for student endpoints.
    Allows access if user is Admin/Warden OR if student_id matches session['student_id'].
    Returns HTTP 403 Forbidden if attempting unauthorized access to another student's data.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] is None:
            return jsonify({'status': 'error', 'message': 'Authentication required. Please log in.'}), 401

        user_roles = [r.lower() for r in session.get('roles', [])]
        is_admin_or_warden = any(r in ('administrator', 'admin', 'warden') for r in user_roles)

        if is_admin_or_warden:
            return f(*args, **kwargs)

        target_student_id = kwargs.get('student_id')
        session_student_id = session.get('student_id')

        if target_student_id is not None and session_student_id is not None:
            if int(target_student_id) == int(session_student_id):
                return f(*args, **kwargs)

        return jsonify({'status': 'error', 'message': 'Access forbidden: You cannot view or modify data belonging to another student.'}), 403
    return decorated_function
