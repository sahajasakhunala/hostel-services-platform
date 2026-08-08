from app.repositories.report_repository import ReportRepository


class ReportService:
    """Service engine for Business Intelligence reporting datasets."""

    @staticmethod
    def get_hostel_occupancy_report():
        """Retrieves Hostel Occupancy Analysis dataset."""
        return ReportRepository.get_hostel_occupancy()

    @staticmethod
    def get_block_occupancy_ranking():
        """Retrieves Block Occupancy Ranking dataset."""
        return ReportRepository.get_block_occupancy_ranking()

    @staticmethod
    def get_outstanding_dues_ranking():
        """Retrieves Outstanding Fee Ranking dataset."""
        return ReportRepository.get_outstanding_dues_ranking()

    @staticmethod
    def get_allocation_stay_analysis():
        """Retrieves Allocation Stay Analysis dataset."""
        return ReportRepository.get_allocation_stay_analysis()

    @staticmethod
    def get_complaint_resolution_analysis():
        """Retrieves Complaint Resolution Analysis dataset."""
        return ReportRepository.get_complaint_resolution_analysis()

    @staticmethod
    def get_maintenance_analysis():
        """Retrieves Maintenance Cost & Status Analysis dataset."""
        return ReportRepository.get_maintenance_analysis()

    @staticmethod
    def get_visitor_trends():
        """Retrieves Visitor Traffic & Gate Activity Trends dataset."""
        return ReportRepository.get_visitor_trends()

    @staticmethod
    def get_hostel_operational_summary():
        """Retrieves Consolidated Multi-Domain Hostel Dashboard Summary dataset."""
        return ReportRepository.get_hostel_operational_summary()
