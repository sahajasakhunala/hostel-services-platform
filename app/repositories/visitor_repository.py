from app.db.connection import get_db_cursor


class VisitorRepository:
    """Data Access Object (DAO) for gate security visitor management."""

    @staticmethod
    def create(data):
        """Inserts a new visitor check-in record into visitors table."""
        query = """
            INSERT INTO visitors (student_id, visitor_name, phone, id_type, id_number, purpose, check_in_time)
            VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
        """
        params = (
            data['student_id'],
            data['visitor_name'],
            data['phone'],
            data['id_type'],
            data['id_number'],
            data['purpose'],
            data.get('check_in_time', None)
        )
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid

    @staticmethod
    def checkout(visitor_id, check_out_time=None):
        """Updates check_out_time for an active visitor."""
        query = """
            UPDATE visitors 
            SET check_out_time = COALESCE(%s, CURRENT_TIMESTAMP)
            WHERE visitor_id = %s AND check_out_time IS NULL
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (check_out_time, visitor_id))
            return cursor.rowcount > 0

    @staticmethod
    def get_by_id(visitor_id):
        """Retrieves raw visitor record by primary key."""
        query = "SELECT * FROM visitors WHERE visitor_id = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (visitor_id,))
            return cursor.fetchone()

    @staticmethod
    def get_active_visitors():
        """Queries v_visitor_report for currently checked-in visitors."""
        query = "SELECT * FROM v_visitor_report WHERE visitor_status = 'currently_checked_in' ORDER BY check_in_time DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_student_visitors(student_id):
        """Queries v_visitor_report for visitors visiting a specific student."""
        query = "SELECT * FROM v_visitor_report WHERE student_id = %s ORDER BY check_in_time DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchall()

    @staticmethod
    def get_visitor_report(limit=100, offset=0):
        """Queries v_visitor_report for all gate security logs."""
        query = "SELECT * FROM v_visitor_report ORDER BY check_in_time DESC LIMIT %s OFFSET %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
