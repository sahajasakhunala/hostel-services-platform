from app.db.connection import get_db_cursor


class ComplaintRepository:
    """Data Access Object (DAO) for student complaint grievance handling."""

    @staticmethod
    def create(data):
        """Inserts a new student complaint into complaints table."""
        query = """
            INSERT INTO complaints (student_id, category_id, subject, description, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['student_id'],
            data['category_id'],
            data['subject'],
            data['description'],
            data.get('priority', 'medium'),
            data.get('status', 'open')
        )
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid

    @staticmethod
    def get_by_id(complaint_id):
        """Retrieves complaint by ID with category and student details."""
        query = """
            SELECT 
                c.complaint_id,
                c.student_id,
                CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                s.registration_number,
                c.category_id,
                cc.name AS category_name,
                c.subject,
                c.description,
                c.priority,
                c.status,
                c.resolution_notes,
                c.assigned_staff_id,
                c.filed_at,
                c.resolved_at
            FROM complaints c
            JOIN students s ON c.student_id = s.student_id
            JOIN complaint_categories cc ON c.category_id = cc.category_id
            WHERE c.complaint_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (complaint_id,))
            return cursor.fetchone()

    @staticmethod
    def get_all(limit=100, offset=0):
        """Retrieves all complaints."""
        query = """
            SELECT 
                c.complaint_id,
                c.student_id,
                CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                cc.name AS category_name,
                c.subject,
                c.priority,
                c.status,
                c.filed_at
            FROM complaints c
            JOIN students s ON c.student_id = s.student_id
            JOIN complaint_categories cc ON c.category_id = cc.category_id
            ORDER BY c.complaint_id DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_unresolved():
        """Queries v_unresolved_complaints for open and in-progress complaints."""
        query = "SELECT * FROM v_unresolved_complaints ORDER BY filed_at DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def update_status(complaint_id, status, resolution_notes=None, assigned_staff_id=None):
        """Updates complaint status, resolution notes, and optional assigned staff."""
        query = """
            UPDATE complaints 
            SET status = %s,
                resolution_notes = COALESCE(%s, resolution_notes),
                assigned_staff_id = COALESCE(%s, assigned_staff_id),
                resolved_at = IF(%s = 'resolved', CURRENT_TIMESTAMP, resolved_at)
            WHERE complaint_id = %s
        """
        params = (status, resolution_notes, assigned_staff_id, status, complaint_id)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.rowcount > 0

    @staticmethod
    def get_categories():
        """Retrieves list of controlled complaint categories."""
        query = "SELECT * FROM complaint_categories ORDER BY category_id ASC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
