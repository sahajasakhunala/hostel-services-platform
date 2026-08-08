-- HostelFlow Audit Trail Triggers
-- Document ID: HOSTEL-TRG-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP TRIGGER IF EXISTS trg_allocations_after_insert_audit;
DROP TRIGGER IF EXISTS trg_allocations_after_update_audit;
DROP TRIGGER IF EXISTS trg_payments_after_insert_audit;
DROP TRIGGER IF EXISTS trg_transfers_after_insert_audit;

DELIMITER //

-- Trigger: trg_allocations_after_insert_audit
-- Purpose: Log creation of new student bed allocations to audit_logs.
CREATE TRIGGER trg_allocations_after_insert_audit
AFTER INSERT ON allocations
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        NULL,
        'INSERT',
        'allocations',
        NEW.allocation_id,
        NULL,
        JSON_OBJECT(
            'allocation_id', NEW.allocation_id,
            'student_id', NEW.student_id,
            'bed_id', NEW.bed_id,
            'status', NEW.status,
            'start_date', NEW.start_date
        )
    );
END //

-- Trigger: trg_allocations_after_update_audit
-- Purpose: Log status/date state transitions of bed allocations (vacating, transfers) to audit_logs.
CREATE TRIGGER trg_allocations_after_update_audit
AFTER UPDATE ON allocations
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        NULL,
        'UPDATE',
        'allocations',
        NEW.allocation_id,
        JSON_OBJECT(
            'status', OLD.status,
            'end_date', OLD.end_date
        ),
        JSON_OBJECT(
            'status', NEW.status,
            'end_date', NEW.end_date
        )
    );
END //

-- Trigger: trg_payments_after_insert_audit
-- Purpose: Log financial payments to audit_logs.
CREATE TRIGGER trg_payments_after_insert_audit
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        NULL,
        'INSERT',
        'payments',
        NEW.payment_id,
        NULL,
        JSON_OBJECT(
            'payment_id', NEW.payment_id,
            'invoice_id', NEW.invoice_id,
            'amount', NEW.amount,
            'receipt_number', NEW.receipt_number,
            'payment_method', NEW.payment_method
        )
    );
END //

-- Trigger: trg_transfers_after_insert_audit
-- Purpose: Log student transfer transactions to audit_logs.
CREATE TRIGGER trg_transfers_after_insert_audit
AFTER INSERT ON transfers
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        NULL,
        'INSERT',
        'transfers',
        NEW.transfer_id,
        NULL,
        JSON_OBJECT(
            'transfer_id', NEW.transfer_id,
            'old_allocation_id', NEW.old_allocation_id,
            'new_allocation_id', NEW.new_allocation_id,
            'reason', NEW.reason
        )
    );
END //

DELIMITER ;
