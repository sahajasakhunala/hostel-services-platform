from app.db.connection import get_db_cursor


class AllocationRepository:
    """Data Access Object (DAO) delegating transactional allocation workflows to MySQL stored procedures."""

    @staticmethod
    def allocate_bed(student_id, bed_id, start_date):
        """Executes sp_allocate_bed stored procedure."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "CALL sp_allocate_bed(%s, %s, %s, @status_code, @message, @alloc_id);",
                (student_id, bed_id, start_date)
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @alloc_id AS allocation_id;")
            return cursor.fetchone()

    @staticmethod
    def transfer_student(student_id, new_bed_id, transfer_date, reason):
        """Executes sp_transfer_student stored procedure."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "CALL sp_transfer_student(%s, %s, %s, %s, @status_code, @message, @transfer_id);",
                (student_id, new_bed_id, transfer_date, reason)
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @transfer_id AS transfer_id;")
            return cursor.fetchone()

    @staticmethod
    def vacate_student(student_id, vacating_date, reason, clearance_status, refund_amount, remarks):
        """Executes sp_vacate_student stored procedure."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "CALL sp_vacate_student(%s, %s, %s, %s, %s, %s, @status_code, @message, @vacating_id);",
                (student_id, vacating_date, reason, clearance_status, refund_amount, remarks)
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @vacating_id AS vacating_id;")
            return cursor.fetchone()

    @staticmethod
    def get_all_active(limit=100, offset=0):
        """Queries v_current_occupancy view for active resident allocations."""
        query = "SELECT * FROM v_current_occupancy ORDER BY allocation_id DESC LIMIT %s OFFSET %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_active_by_student_id(student_id):
        """Retrieves active allocation record for a specific student."""
        query = "SELECT * FROM v_current_occupancy WHERE student_id = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchone()

    @staticmethod
    def get_history_by_student_id(student_id):
        """Queries v_allocation_history view for complete stay timeline of a student."""
        query = "SELECT * FROM v_allocation_history WHERE student_id = %s ORDER BY start_date DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
