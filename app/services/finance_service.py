from app.repositories.finance_repository import FinanceRepository


class FinanceService:
    """Service engine for billing, payment processing, and fee dues reporting."""

    @staticmethod
    def get_fee_dues(limit=100, offset=0):
        """Retrieves outstanding fee dues report."""
        return FinanceRepository.get_fee_dues(limit=limit, offset=offset)

    @staticmethod
    def get_invoice(invoice_id):
        """Retrieves single invoice record or raises ValueError if not found."""
        invoice = FinanceRepository.get_invoice_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice ID {invoice_id} not found.")
        return invoice

    @staticmethod
    def get_student_invoices(student_id):
        """Retrieves list of invoices for a student."""
        return FinanceRepository.get_student_invoices(student_id)

    @staticmethod
    def get_student_payment_history(student_id):
        """Retrieves complete payment transaction history for a student."""
        return FinanceRepository.get_student_payment_history(student_id)

    @staticmethod
    def process_payment(data):
        """
        Validates input parameters and delegates payment execution to sp_process_payment.
        Raises ValueError on validation failure or procedure error.
        """
        required = ['invoice_id', 'amount', 'payment_method', 'receipt_number']
        for field in required:
            if field not in data or data[field] is None or data[field] == '':
                raise ValueError(f"Missing required field: '{field}'")

        try:
            amount = float(data['amount'])
        except (ValueError, TypeError):
            raise ValueError("Payment amount must be a valid numeric value.")

        if amount <= 0.00:
            raise ValueError("Payment amount must be greater than zero.")

        result = FinanceRepository.process_payment(
            invoice_id=int(data['invoice_id']),
            amount=amount,
            payment_method=data['payment_method'],
            receipt_number=data['receipt_number'],
            remarks=data.get('remarks', None)
        )

        if result['status_code'] != 'SUCCESS':
            raise ValueError(result['message'])

        return result
