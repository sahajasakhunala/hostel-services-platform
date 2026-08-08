from app.repositories.complaint_repository import ComplaintRepository


class ComplaintService:
    """Service engine for student grievance filing and status workflow resolution."""

    VALID_PRIORITIES = {'low', 'medium', 'high', 'urgent'}
    VALID_STATUSES = {'open', 'in_progress', 'resolved', 'closed'}

    @staticmethod
    def file_complaint(data):
        """
        Validates complaint fields and persists record.
        Raises ValueError if required fields or priority values are invalid.
        """
        required = ['student_id', 'category_id', 'subject', 'description']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        priority = data.get('priority', 'medium')
        if priority not in ComplaintService.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {', '.join(ComplaintService.VALID_PRIORITIES)}")

        complaint_id = ComplaintRepository.create(data)
        return ComplaintRepository.get_by_id(complaint_id)

    @staticmethod
    def get_complaint_by_id(complaint_id):
        """Retrieves single complaint record or raises ValueError if not found."""
        complaint = ComplaintRepository.get_by_id(complaint_id)
        if not complaint:
            raise ValueError(f"Complaint ID {complaint_id} not found.")
        return complaint

    @staticmethod
    def get_all_complaints(limit=100, offset=0):
        """Retrieves all complaints."""
        return ComplaintRepository.get_all(limit=limit, offset=offset)

    @staticmethod
    def get_unresolved_complaints():
        """Retrieves open and in-progress unresolved complaints from v_unresolved_complaints."""
        return ComplaintRepository.get_unresolved()

    @staticmethod
    def update_complaint_status(complaint_id, data):
        """
        Updates complaint status, optional notes, and staff assignment.
        Raises ValueError if complaint ID not found or status invalid.
        """
        if 'status' not in data or not data['status']:
            raise ValueError("Missing required field: 'status'")

        status = data['status']
        if status not in ComplaintService.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(ComplaintService.VALID_STATUSES)}")

        complaint = ComplaintRepository.get_by_id(complaint_id)
        if not complaint:
            raise ValueError(f"Complaint ID {complaint_id} not found.")

        resolution_notes = data.get('resolution_notes', None)
        assigned_staff_id = data.get('assigned_staff_id', None)

        success = ComplaintRepository.update_status(
            complaint_id=complaint_id,
            status=status,
            resolution_notes=resolution_notes,
            assigned_staff_id=assigned_staff_id
        )

        if not success:
            raise ValueError(f"Failed to update complaint ID {complaint_id}.")

        return ComplaintRepository.get_by_id(complaint_id)

    @staticmethod
    def get_categories():
        """Retrieves list of complaint categories."""
        return ComplaintRepository.get_categories()
