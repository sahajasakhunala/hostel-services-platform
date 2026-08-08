from flask import Blueprint, request, jsonify
from app.services.finance_service import FinanceService

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/dues', methods=['GET'])
def get_fee_dues():
    """GET /api/finance/dues - Retrieve outstanding fee dues report."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        dues = FinanceService.get_fee_dues(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(dues), 'data': dues}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@finance_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """GET /api/finance/invoices/<id> - Retrieve single invoice details."""
    try:
        invoice = FinanceService.get_invoice(invoice_id)
        return jsonify({'status': 'success', 'data': invoice}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@finance_bp.route('/students/<int:student_id>/invoices', methods=['GET'])
def get_student_invoices(student_id):
    """GET /api/finance/students/<student_id>/invoices - Retrieve all invoices for a student."""
    try:
        invoices = FinanceService.get_student_invoices(student_id)
        return jsonify({'status': 'success', 'count': len(invoices), 'data': invoices}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@finance_bp.route('/students/<int:student_id>/payments', methods=['GET'])
def get_student_payment_history(student_id):
    """GET /api/finance/students/<student_id>/payments - Retrieve complete payment transaction history."""
    try:
        payments = FinanceService.get_student_payment_history(student_id)
        return jsonify({'status': 'success', 'count': len(payments), 'data': payments}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@finance_bp.route('/payments', methods=['POST'])
def process_payment():
    """POST /api/finance/payments - Process a fee payment via sp_process_payment."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Request payload must be valid JSON.'}), 400

        result = FinanceService.process_payment(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'payment_id': result['payment_id']}}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
