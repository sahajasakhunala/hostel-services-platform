from app.repositories.allocation_repository import AllocationRepository


class AllocationService:
    """Service engine for bed allocations, transfers, and vacating workflows."""

    @staticmethod
    def get_active_allocations(limit=100, offset=0):
        """Retrieves list of current active allocations."""
        return AllocationRepository.get_all_active(limit=limit, offset=offset)

    @staticmethod
    def get_student_active_allocation(student_id):
        """Retrieves current active allocation for a student."""
        return AllocationRepository.get_active_by_student_id(student_id)

    @staticmethod
    def get_student_allocation_history(student_id):
        """Retrieves stay history timeline for a student."""
        return AllocationRepository.get_history_by_student_id(student_id)

    @staticmethod
    def allocate_bed(data):
        """
        Validates input parameters and delegates bed allocation to sp_allocate_bed.
        Raises ValueError if procedure returns ERROR status_code.
        """
        required = ['student_id', 'bed_id', 'start_date']
        for field in required:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: '{field}'")

        result = AllocationRepository.allocate_bed(
            student_id=int(data['student_id']),
            bed_id=int(data['bed_id']),
            start_date=data['start_date']
        )

        if result['status_code'] != 'SUCCESS':
            raise ValueError(result['message'])

        return result

    @staticmethod
    def transfer_student(data):
        """
        Validates input parameters and delegates room transfer to sp_transfer_student.
        Raises ValueError if procedure returns ERROR status_code.
        """
        required = ['student_id', 'new_bed_id', 'transfer_date', 'reason']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        result = AllocationRepository.transfer_student(
            student_id=int(data['student_id']),
            new_bed_id=int(data['new_bed_id']),
            transfer_date=data['transfer_date'],
            reason=data['reason']
        )

        if result['status_code'] != 'SUCCESS':
            raise ValueError(result['message'])

        return result

    @staticmethod
    def vacate_student(data):
        """
        Validates input parameters and delegates vacating to sp_vacate_student.
        Raises ValueError if procedure returns ERROR status_code.
        """
        required = ['student_id', 'vacating_date', 'reason', 'clearance_status']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        refund_amount = float(data.get('deposit_refund_amount', 0.00))
        remarks = data.get('remarks', None)

        result = AllocationRepository.vacate_student(
            student_id=int(data['student_id']),
            vacating_date=data['vacating_date'],
            reason=data['reason'],
            clearance_status=data['clearance_status'],
            refund_amount=refund_amount,
            remarks=remarks
        )

        if result['status_code'] != 'SUCCESS':
            raise ValueError(result['message'])

        return result
