from flask import Blueprint, jsonify
from app.services.report_service import ReportService

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/occupancy', methods=['GET'])
def get_hostel_occupancy_report():
    """GET /api/reports/occupancy - Retrieve hostel occupancy analysis report."""
    try:
        data = ReportService.get_hostel_occupancy_report()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/occupancy/blocks', methods=['GET'])
def get_block_occupancy_ranking():
    """GET /api/reports/occupancy/blocks - Retrieve block-level occupancy ranking dataset."""
    try:
        data = ReportService.get_block_occupancy_ranking()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/fees/ranking', methods=['GET'])
def get_outstanding_dues_ranking():
    """GET /api/reports/fees/ranking - Retrieve fee debtor DENSE_RANK dataset."""
    try:
        data = ReportService.get_outstanding_dues_ranking()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/allocations/stays', methods=['GET'])
def get_allocation_stay_analysis():
    """GET /api/reports/allocations/stays - Retrieve allocation stay duration analysis."""
    try:
        data = ReportService.get_allocation_stay_analysis()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/complaints', methods=['GET'])
def get_complaint_resolution_analysis():
    """GET /api/reports/complaints - Retrieve complaint resolution rate and time dataset."""
    try:
        data = ReportService.get_complaint_resolution_analysis()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/maintenance', methods=['GET'])
def get_maintenance_analysis():
    """GET /api/reports/maintenance - Retrieve maintenance cost and status analysis."""
    try:
        data = ReportService.get_maintenance_analysis()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/visitors', methods=['GET'])
def get_visitor_trends():
    """GET /api/reports/visitors - Retrieve visitor traffic and gate activity trends."""
    try:
        data = ReportService.get_visitor_trends()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@reports_bp.route('/hostel-summary', methods=['GET'])
def get_hostel_operational_summary():
    """GET /api/reports/hostel-summary - Retrieve multi-domain cross-domain dashboard summary."""
    try:
        data = ReportService.get_hostel_operational_summary()
        return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
