from flask import Blueprint, request, jsonify
from app.services.finance_service import FinanceService
from app.utils.validation import (
    require_fields, validate_integer_id, validate_positive_amount,
    validate_enum, validate_string_length, parse_pagination_params
)

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/dues', methods=['GET'])
def get_fee_dues():
    """GET /api/finance/dues - Retrieve outstanding fee dues report."""
    try:
        limit, offset, err = parse_pagination_params(request.args)
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'pagination': err}}), 400
        dues = FinanceService.get_fee_dues(limit=limit, offset=offset)
        return jsonify({'status': 'success', 'count': len(dues), 'data': dues}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@finance_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """GET /api/finance/invoices/<id> - Retrieve single invoice details."""
    try:
        val_id, err = validate_integer_id(invoice_id, 'invoice_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'invoice_id': err}}), 400
        invoice = FinanceService.get_invoice(val_id)
        return jsonify({'status': 'success', 'data': invoice}), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@finance_bp.route('/students/<int:student_id>/invoices', methods=['GET'])
def get_student_invoices(student_id):
    """GET /api/finance/students/<student_id>/invoices - Retrieve all invoices for a student."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        invoices = FinanceService.get_student_invoices(val_id)
        return jsonify({'status': 'success', 'count': len(invoices), 'data': invoices}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@finance_bp.route('/students/<int:student_id>/payments', methods=['GET'])
def get_student_payment_history(student_id):
    """GET /api/finance/students/<student_id>/payments - Retrieve complete payment transaction history."""
    try:
        val_id, err = validate_integer_id(student_id, 'student_id')
        if err:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': {'student_id': err}}), 400
        payments = FinanceService.get_student_payment_history(val_id)
        return jsonify({'status': 'success', 'count': len(payments), 'data': payments}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500


@finance_bp.route('/payments', methods=['POST'])
def process_payment():
    """POST /api/finance/payments - Process a fee payment via sp_process_payment."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Request payload must be a valid JSON object.'}), 400

        errors = require_fields(data, ['invoice_id', 'amount', 'payment_method', 'receipt_number'])

        if 'invoice_id' in data and data['invoice_id'] is not None:
            _, err = validate_integer_id(data['invoice_id'], 'invoice_id')
            if err: errors['invoice_id'] = err

        if 'amount' in data and data['amount'] is not None:
            _, err = validate_positive_amount(data['amount'], 'amount')
            if err: errors['amount'] = err

        if 'payment_method' in data and data['payment_method']:
            allowed_methods = ['UPI', 'NetBanking', 'CreditCard', 'Cash', 'BankDraft']
            _, err = validate_enum(data['payment_method'], allowed_methods, 'payment_method')
            if err: errors['payment_method'] = err

        if 'receipt_number' in data and data['receipt_number']:
            _, err = validate_string_length(data['receipt_number'], 'receipt_number', max_length=50)
            if err: errors['receipt_number'] = err

        if errors:
            return jsonify({'status': 'error', 'message': 'Validation failed.', 'errors': errors}), 400

        result = FinanceService.process_payment(data)
        return jsonify({'status': 'success', 'message': result['message'], 'data': {'payment_id': result['payment_id']}}), 201
    except ValueError as ve:
        msg = str(ve)
        status_code = 409 if any(k in msg.lower() for k in ['exceeds', 'already paid', 'overpaid', 'balance']) else 400
        return jsonify({'status': 'error', 'message': msg}), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500
