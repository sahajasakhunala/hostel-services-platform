from app.repositories.visitor_repository import VisitorRepository


class VisitorService:
    """Service engine for visitor check-in, check-out, and gate security reporting."""

    @staticmethod
    def checkin_visitor(data):
        """
        Validates check-in parameters and inserts visitor record.
        Raises ValueError if required fields are missing or invalid.
        """
        required = ['student_id', 'visitor_name', 'phone', 'id_type', 'id_number', 'purpose']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        visitor_id = VisitorRepository.create(data)
        return VisitorRepository.get_by_id(visitor_id)

    @staticmethod
    def checkout_visitor(visitor_id, check_out_time=None):
        """
        Validates active visit state and updates check_out_time.
        Raises ValueError if visitor ID not found or already checked out.
        """
        visitor = VisitorRepository.get_by_id(visitor_id)
        if not visitor:
            raise ValueError(f"Visitor ID {visitor_id} not found.")

        if visitor['check_out_time'] is not None:
            raise ValueError(f"Visitor ID {visitor_id} has already checked out.")

        success = VisitorRepository.checkout(visitor_id, check_out_time=check_out_time)
        if not success:
            raise ValueError(f"Failed to check out visitor ID {visitor_id}.")

        return VisitorRepository.get_by_id(visitor_id)

    @staticmethod
    def get_visitor_by_id(visitor_id):
        """Retrieves single visitor record by ID."""
        visitor = VisitorRepository.get_by_id(visitor_id)
        if not visitor:
            raise ValueError(f"Visitor ID {visitor_id} not found.")
        return visitor

    @staticmethod
    def get_active_visitors():
        """Retrieves list of currently checked-in visitors."""
        return VisitorRepository.get_active_visitors()

    @staticmethod
    def get_student_visitors(student_id):
        """Retrieves visitor logs for a specific student."""
        return VisitorRepository.get_student_visitors(student_id)

    @staticmethod
    def get_visitor_report(limit=100, offset=0):
        """Retrieves full gate security visitor report."""
        return VisitorRepository.get_visitor_report(limit=limit, offset=offset)
