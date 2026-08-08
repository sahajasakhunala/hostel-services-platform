from app.db.connection import get_db_cursor


class AuthRepository:
    """Data Access Object (DAO) for authentication and RBAC identity lookups."""

    @staticmethod
    def get_user_by_username(username):
        """Retrieves user account details by username."""
        query = """
            SELECT 
                u.user_id,
                u.username,
                u.password_hash,
                u.student_id,
                u.staff_id,
                u.is_active,
                u.created_at
            FROM users u
            WHERE u.username = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (username,))
            return cursor.fetchone()

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves user account by primary key ID."""
        query = """
            SELECT 
                u.user_id,
                u.username,
                u.student_id,
                u.staff_id,
                u.is_active,
                u.created_at
            FROM users u
            WHERE u.user_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchone()

    @staticmethod
    def get_user_roles(user_id):
        """Retrieves assigned role names for a user."""
        query = """
            SELECT r.name AS role_name
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [row['role_name'] for row in rows]

    @staticmethod
    def create_user(username, password_hash, student_id=None, staff_id=None, role_ids=None):
        """Creates a new user account and maps role IDs in user_roles table."""
        user_query = """
            INSERT INTO users (username, password_hash, student_id, staff_id, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(user_query, (username, password_hash, student_id, staff_id))
            user_id = cursor.lastrowid

            if role_ids:
                role_query = "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)"
                for r_id in role_ids:
                    cursor.execute(role_query, (user_id, r_id))

            return user_id

    @staticmethod
    def get_all_roles():
        """Retrieves all roles from roles table."""
        query = "SELECT * FROM roles ORDER BY role_id ASC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
