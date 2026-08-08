from app.repositories.maintenance_repository import MaintenanceRepository


class MaintenanceService:
    """Service engine for facility repair requests, staff assignment, and status updates."""

    VALID_PRIORITIES = {'low', 'medium', 'high', 'urgent'}
    VALID_STATUSES = {'pending', 'assigned', 'in_progress', 'completed'}

    @staticmethod
    def create_request(data):
        """
        Validates repair request parameters and persists record.
        Raises ValueError if required fields or priority values are invalid.
        """
        required = ['room_id', 'category', 'description']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        priority = data.get('priority', 'medium')
        if priority not in MaintenanceService.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {', '.join(MaintenanceService.VALID_PRIORITIES)}")

        request_id = MaintenanceRepository.create(data)
        return MaintenanceRepository.get_by_id(request_id)

    @staticmethod
    def get_request_by_id(request_id):
        """Retrieves single maintenance request record or raises ValueError if not found."""
        maint_req = MaintenanceRepository.get_by_id(request_id)
        if not maint_req:
            raise ValueError(f"Maintenance request ID {request_id} not found.")
        return maint_req

    @staticmethod
    def get_all_requests(limit=100, offset=0):
        """Retrieves all maintenance requests."""
        return MaintenanceRepository.get_all(limit=limit, offset=offset)

    @staticmethod
    def get_pending_requests():
        """Retrieves non-completed repair requests from v_maintenance_status."""
        return MaintenanceRepository.get_pending()

    @staticmethod
    def assign_staff(request_id, data):
        """
        Assigns repair staff to maintenance request.
        Raises ValueError if request ID or staff_id missing.
        """
        if 'staff_id' not in data or not data['staff_id']:
            raise ValueError("Missing required field: 'staff_id'")

        maint_req = MaintenanceRepository.get_by_id(request_id)
        if not maint_req:
            raise ValueError(f"Maintenance request ID {request_id} not found.")

        success = MaintenanceRepository.assign_staff(request_id, int(data['staff_id']))
        if not success:
            raise ValueError(f"Failed to assign staff to maintenance request ID {request_id}.")

        return MaintenanceRepository.get_by_id(request_id)

    @staticmethod
    def update_request_status(request_id, data):
        """
        Updates maintenance request status and optional repair cost.
        Raises ValueError if status invalid.
        """
        if 'status' not in data or not data['status']:
            raise ValueError("Missing required field: 'status'")

        status = data['status']
        if status not in MaintenanceService.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(MaintenanceService.VALID_STATUSES)}")

        maint_req = MaintenanceRepository.get_by_id(request_id)
        if not maint_req:
            raise ValueError(f"Maintenance request ID {request_id} not found.")

        cost = float(data.get('cost', 0.00))

        success = MaintenanceRepository.update_status(request_id, status=status, cost=cost)
        if not success:
            raise ValueError(f"Failed to update status for maintenance request ID {request_id}.")

        return MaintenanceRepository.get_by_id(request_id)

    @staticmethod
    def get_staff():
        """Retrieves list of maintenance staff."""
        return MaintenanceRepository.get_staff()
