-- HostelFlow Stored Procedure: sp_process_payment
-- Document ID: HOSTEL-PRC-004
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS sp_process_payment;

DELIMITER //

CREATE PROCEDURE sp_process_payment(
    IN p_invoice_id BIGINT,
    IN p_amount DECIMAL(10,2),
    IN p_payment_method VARCHAR(50),
    IN p_receipt_number VARCHAR(50),
    IN p_remarks VARCHAR(255),
    OUT p_status_code VARCHAR(20),
    OUT p_message VARCHAR(255),
    OUT p_payment_id BIGINT
)
proc_label: BEGIN
    DECLARE v_outstanding DECIMAL(10,2);
    DECLARE v_receipt_exists INT DEFAULT 0;

    -- Error handler for unexpected transaction failures
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Payment transaction aborted due to database exception or constraint violation.';
        SET p_payment_id = NULL;
    END;

    SET p_payment_id = NULL;
    START TRANSACTION;

    -- 1. Validate payment amount positive
    IF p_amount <= 0.00 THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Payment amount must be greater than zero.';
        LEAVE proc_label;
    END IF;

    -- 2. Lock target invoice row for update
    SELECT outstanding_balance INTO v_outstanding
    FROM invoices
    WHERE invoice_id = p_invoice_id
    FOR UPDATE;

    IF v_outstanding IS NULL THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Invoice ID does not exist.';
        LEAVE proc_label;
    END IF;

    -- 3. Check for receipt number uniqueness
    SELECT COUNT(*) INTO v_receipt_exists
    FROM payments
    WHERE receipt_number = p_receipt_number;

    IF v_receipt_exists > 0 THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Receipt number already exists.';
        LEAVE proc_label;
    END IF;

    -- 4. Validate payment against locked outstanding balance
    IF p_amount > v_outstanding THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Payment amount exceeds outstanding invoice balance.';
        LEAVE proc_label;
    END IF;

    -- 5. Insert payment record (triggers automatically update balance & audit log)
    INSERT INTO payments (invoice_id, amount, payment_method, receipt_number, remarks)
    VALUES (p_invoice_id, p_amount, p_payment_method, p_receipt_number, p_remarks);
    SET p_payment_id = LAST_INSERT_ID();

    COMMIT;
    SET p_status_code = 'SUCCESS';
    SET p_message = 'Payment processed successfully.';
END //

DELIMITER ;
