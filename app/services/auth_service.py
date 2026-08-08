from flask import session
from app.repositories.auth_repository import AuthRepository
from app.utils.auth import verify_password, hash_password


class AuthService:
    """Service engine for authentication, session management, and RBAC security."""

    @staticmethod
    def login(username, password):
        """
        Verifies credentials, loads user roles, and establishes Flask session.
        Raises ValueError if authentication fails.
        """
        if not username or not password:
            raise ValueError("Username and password are required.")

        user = AuthRepository.get_user_by_username(username)
        if not user:
            raise ValueError("Invalid username or password.")

        if not user['is_active']:
            raise ValueError("User account is disabled.")

        if not verify_password(password, user['password_hash']):
            raise ValueError("Invalid username or password.")

        roles = AuthRepository.get_user_roles(user['user_id'])

        # Populate Flask server-side session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['student_id'] = user['student_id']
        session['staff_id'] = user['staff_id']
        session['roles'] = roles

        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'student_id': user['student_id'],
            'staff_id': user['staff_id'],
            'roles': roles
        }

    @staticmethod
    def get_current_user():
        """Retrieves currently authenticated session user or None."""
        user_id = session.get('user_id')
        if not user_id:
            return None

        user = AuthRepository.get_user_by_id(user_id)
        if not user or not user['is_active']:
            return None

        roles = AuthRepository.get_user_roles(user_id)
        user['roles'] = roles
        return user

    @staticmethod
    def logout():
        """Clears Flask user session."""
        session.clear()
        return True

    @staticmethod
    def register_user(username, password, student_id=None, staff_id=None, role_ids=None):
        """Helper to create a new hashed user account."""
        existing = AuthRepository.get_user_by_username(username)
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")

        pwd_hash = hash_password(password)
        user_id = AuthRepository.create_user(
            username=username,
            password_hash=pwd_hash,
            student_id=student_id,
            staff_id=staff_id,
            role_ids=role_ids
        )
        return AuthRepository.get_user_by_id(user_id)
