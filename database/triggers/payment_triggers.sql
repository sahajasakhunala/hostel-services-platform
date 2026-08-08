-- HostelFlow Financial & Payment Balance Triggers
-- Document ID: HOSTEL-TRG-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP TRIGGER IF EXISTS trg_payments_before_insert_validate_balance;
DROP TRIGGER IF EXISTS trg_payments_after_insert_update_balance;

DELIMITER //

-- Trigger: trg_payments_before_insert_validate_balance
-- Purpose: Validate that a payment amount does not exceed the current outstanding balance on the invoice.
-- Concurrency Strategy: Performs a FOR UPDATE lock on the target invoice row to prevent concurrent over-payment race conditions.
CREATE TRIGGER trg_payments_before_insert_validate_balance
BEFORE INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE v_outstanding DECIMAL(10,2);

    -- Lock target invoice row for update
    SELECT outstanding_balance INTO v_outstanding
    FROM invoices
    WHERE invoice_id = NEW.invoice_id
    FOR UPDATE;

    -- Validate payment amount against locked outstanding balance
    IF NEW.amount > v_outstanding THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERR_PAYMENT_EXCEEDS_BALANCE: Payment amount exceeds outstanding invoice balance.';
    END IF;
END //

-- Trigger: trg_payments_after_insert_update_balance
-- Purpose: Deduct payment amount from invoice outstanding_balance and adjust status to partially_paid or paid.
CREATE TRIGGER trg_payments_after_insert_update_balance
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    UPDATE invoices
    SET outstanding_balance = outstanding_balance - NEW.amount,
        status = CASE 
            WHEN (outstanding_balance - NEW.amount) = 0.00 THEN 'paid'
            ELSE 'partially_paid'
        END
    WHERE invoice_id = NEW.invoice_id;
END //

DELIMITER ;
