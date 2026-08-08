from app.db.connection import get_db_cursor


class MaintenanceRepository:
    """Data Access Object (DAO) for facility repair and maintenance request tracking."""

    @staticmethod
    def create(data):
        """Inserts a new maintenance request into maintenance_requests table."""
        query = """
            INSERT INTO maintenance_requests (room_id, category, description, priority, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data['room_id'],
            data['category'],
            data['description'],
            data.get('priority', 'medium'),
            data.get('status', 'pending')
        )
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid

    @staticmethod
    def get_by_id(request_id):
        """Retrieves single maintenance request by ID."""
        query = """
            SELECT 
                mr.request_id,
                mr.room_id,
                r.room_number,
                fl.floor_number,
                b.name AS block_name,
                h.name AS hostel_name,
                mr.category,
                mr.description,
                mr.priority,
                mr.status,
                mr.cost,
                mr.assigned_staff_id,
                ms.name AS assigned_staff_name,
                mr.reported_at,
                mr.completed_at
            FROM maintenance_requests mr
            JOIN rooms r ON mr.room_id = r.room_id
            JOIN floors fl ON r.floor_id = fl.floor_id
            JOIN blocks b ON fl.block_id = b.block_id
            JOIN hostels h ON b.hostel_id = h.hostel_id
            LEFT JOIN maintenance_staff ms ON mr.assigned_staff_id = ms.staff_id
            WHERE mr.request_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (request_id,))
            return cursor.fetchone()

    @staticmethod
    def get_all(limit=100, offset=0):
        """Retrieves all maintenance requests."""
        query = """
            SELECT 
                mr.request_id,
                r.room_number,
                h.name AS hostel_name,
                mr.category,
                mr.priority,
                mr.status,
                mr.cost,
                mr.reported_at
            FROM maintenance_requests mr
            JOIN rooms r ON mr.room_id = r.room_id
            JOIN floors fl ON r.floor_id = fl.floor_id
            JOIN blocks b ON fl.block_id = b.block_id
            JOIN hostels h ON b.hostel_id = h.hostel_id
            ORDER BY mr.request_id DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_pending():
        """Queries v_maintenance_status for incomplete repair requests."""
        query = "SELECT * FROM v_maintenance_status WHERE maintenance_status != 'completed' ORDER BY reported_at DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def assign_staff(request_id, staff_id):
        """Assigns maintenance staff to repair request and updates status to assigned."""
        query = """
            UPDATE maintenance_requests 
            SET assigned_staff_id = %s,
                status = 'assigned'
            WHERE request_id = %s
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (staff_id, request_id))
            return cursor.rowcount > 0

    @staticmethod
    def update_status(request_id, status, cost=0.00):
        """Updates repair request status and cost, setting completed_at timestamp on completion."""
        query = """
            UPDATE maintenance_requests 
            SET status = %s,
                cost = %s,
                completed_at = IF(%s = 'completed', CURRENT_TIMESTAMP, completed_at)
            WHERE request_id = %s
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (status, cost, status, request_id))
            return cursor.rowcount > 0

    @staticmethod
    def get_staff():
        """Retrieves list of maintenance staff."""
        query = "SELECT * FROM maintenance_staff ORDER BY staff_id ASC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
