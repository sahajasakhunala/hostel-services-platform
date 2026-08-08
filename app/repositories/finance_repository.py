from app.db.connection import get_db_cursor


class FinanceRepository:
    """Data Access Object (DAO) for financial transactions, billing, and fee dues reporting."""

    @staticmethod
    def process_payment(invoice_id, amount, payment_method, receipt_number, remarks=None):
        """Executes sp_process_payment stored procedure."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "CALL sp_process_payment(%s, %s, %s, %s, %s, @status_code, @message, @payment_id);",
                (invoice_id, amount, payment_method, receipt_number, remarks)
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @payment_id AS payment_id;")
            return cursor.fetchone()

    @staticmethod
    def get_fee_dues(limit=100, offset=0):
        """Queries v_fee_dues view for outstanding resident balances."""
        query = "SELECT * FROM v_fee_dues ORDER BY outstanding_balance DESC LIMIT %s OFFSET %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_invoice_by_id(invoice_id):
        """Retrieves invoice details by ID."""
        query = """
            SELECT 
                i.invoice_id,
                i.student_id,
                CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                s.registration_number,
                rt.name AS room_type,
                ay.year_label AS academic_year,
                i.total_amount,
                i.outstanding_balance,
                (i.total_amount - i.outstanding_balance) AS paid_amount,
                i.due_date,
                i.status
            FROM invoices i
            JOIN students s ON i.student_id = s.student_id
            JOIN fee_structures fs ON i.fee_structure_id = fs.fee_structure_id
            JOIN room_types rt ON fs.room_type_id = rt.room_type_id
            JOIN academic_years ay ON fs.academic_year_id = ay.academic_year_id
            WHERE i.invoice_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (invoice_id,))
            return cursor.fetchone()

    @staticmethod
    def get_student_invoices(student_id):
        """Retrieves all invoices for a given student."""
        query = """
            SELECT 
                i.invoice_id,
                rt.name AS room_type,
                ay.year_label AS academic_year,
                i.total_amount,
                i.outstanding_balance,
                (i.total_amount - i.outstanding_balance) AS paid_amount,
                i.due_date,
                i.status
            FROM invoices i
            JOIN fee_structures fs ON i.fee_structure_id = fs.fee_structure_id
            JOIN room_types rt ON fs.room_type_id = rt.room_type_id
            JOIN academic_years ay ON fs.academic_year_id = ay.academic_year_id
            WHERE i.student_id = %s
            ORDER BY i.due_date DESC
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchall()

    @staticmethod
    def get_student_payment_history(student_id):
        """Retrieves complete payment transaction ledger for a student."""
        query = """
            SELECT 
                p.payment_id,
                p.invoice_id,
                p.amount,
                p.payment_date,
                p.payment_method,
                p.receipt_number,
                p.remarks,
                rt.name AS room_type
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN fee_structures fs ON i.fee_structure_id = fs.fee_structure_id
            JOIN room_types rt ON fs.room_type_id = rt.room_type_id
            WHERE i.student_id = %s
            ORDER BY p.payment_date DESC
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
