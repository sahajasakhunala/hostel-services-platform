-- HostelFlow Trigger Verification Suite
-- Document ID: HOSTEL-TST-002
-- Target Triggers: Allocation Capacity, Payment Balance, Audit Trail
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS run_trigger_tests;

DELIMITER //

CREATE PROCEDURE run_trigger_tests()
BEGIN
    -- Fixture variables
    DECLARE v_dept_id BIGINT;
    DECLARE v_room_type_id BIGINT;
    DECLARE v_year_id BIGINT;
    DECLARE v_course_id BIGINT;
    DECLARE v_student1_id BIGINT;
    DECLARE v_student2_id BIGINT;
    DECLARE v_hostel_id BIGINT;
    DECLARE v_block_id BIGINT;
    DECLARE v_floor_id BIGINT;
    DECLARE v_room_id BIGINT;
    DECLARE v_bed1_id BIGINT;
    DECLARE v_bed2_id BIGINT;
    DECLARE v_bed3_id BIGINT;
    DECLARE v_fee_id BIGINT;
    DECLARE v_invoice_id BIGINT;
    DECLARE v_alloc1_id BIGINT;
    DECLARE v_alloc2_id BIGINT;
    DECLARE v_transfer_id BIGINT;

    -- Results tracking
    DECLARE v_caught_error INT DEFAULT 0;
    DECLARE v_audit_count INT DEFAULT 0;
    DECLARE v_balance DECIMAL(10,2);
    DECLARE v_status VARCHAR(20);

    -- Exception Handler
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
    BEGIN
        SET v_caught_error = 1;
    END;

    -- Temporary table for test results
    DROP TEMPORARY TABLE IF EXISTS temp_trigger_test_results;
    CREATE TEMPORARY TABLE temp_trigger_test_results (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        test_code VARCHAR(20) NOT NULL,
        test_description VARCHAR(150) NOT NULL,
        result VARCHAR(10) NOT NULL,
        detail TEXT NULL
    );

    -- =========================================================================
    -- FIXTURE SETUP
    -- =========================================================================
    DELETE FROM audit_logs WHERE table_name IN ('allocations', 'payments', 'transfers');
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-REC-%';
    DELETE FROM invoices WHERE total_amount = 10000.00 AND due_date = '2026-12-31';
    DELETE FROM fee_structures WHERE amount = 10000.00;
    DELETE FROM transfers WHERE reason = 'TEST-TRANSFER-REASON';
    DELETE FROM allocations WHERE student_id IN (SELECT student_id FROM students WHERE registration_number LIKE 'TEST-TRG-REG-%');
    DELETE FROM students WHERE registration_number LIKE 'TEST-TRG-REG-%';
    DELETE FROM beds WHERE bed_code LIKE 'TEST-TRG-BED-%';
    DELETE FROM rooms WHERE room_number = 'TEST-TRG-ROOM-200';
    DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'TEST-TRG-BLOCK-B');
    DELETE FROM blocks WHERE name = 'TEST-TRG-BLOCK-B';
    DELETE FROM hostels WHERE name = 'TEST-TRG-HOSTEL-BETA';
    DELETE FROM courses WHERE name = 'TEST-TRG-COURSE';
    DELETE FROM departments WHERE code = 'TEST-TRG-DEPT';
    DELETE FROM academic_years WHERE year_label = 'TEST-TRG-YEAR-2026';
    DELETE FROM room_types WHERE name = 'TEST-TRG-DOUBLE-TYPE';

    -- Insert Reference & Infrastructure
    INSERT INTO departments (name, code) VALUES ('Test Trigger Dept', 'TEST-TRG-DEPT');
    SET v_dept_id = LAST_INSERT_ID();

    INSERT INTO room_types (name, base_capacity) VALUES ('TEST-TRG-DOUBLE-TYPE', 2);
    SET v_room_type_id = LAST_INSERT_ID();

    INSERT INTO academic_years (year_label, start_date, end_date) VALUES ('TEST-TRG-YEAR-2026', '2026-01-01', '2026-12-31');
    SET v_year_id = LAST_INSERT_ID();

    INSERT INTO courses (department_id, name, degree_level) VALUES (v_dept_id, 'TEST-TRG-COURSE', 'UG');
    SET v_course_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-TRG-REG-001', 'TrgStudent', 'One', '2003-01-01', 'M', 'trg1@hostelflow.local', '9997770001', v_dept_id, v_course_id, v_year_id);
    SET v_student1_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-TRG-REG-002', 'TrgStudent', 'Two', '2003-02-02', 'F', 'trg2@hostelflow.local', '9997770002', v_dept_id, v_course_id, v_year_id);
    SET v_student2_id = LAST_INSERT_ID();

    INSERT INTO hostels (name, gender_type, address) VALUES ('TEST-TRG-HOSTEL-BETA', 'Co-ed', 'Campus Trigger Test');
    SET v_hostel_id = LAST_INSERT_ID();

    INSERT INTO blocks (hostel_id, name) VALUES (v_hostel_id, 'TEST-TRG-BLOCK-B');
    SET v_block_id = LAST_INSERT_ID();

    INSERT INTO floors (block_id, floor_number) VALUES (v_block_id, 2);
    SET v_floor_id = LAST_INSERT_ID();

    -- Create room with capacity = 2
    INSERT INTO rooms (floor_id, room_type_id, room_number, capacity) VALUES (v_floor_id, v_room_type_id, 'TEST-TRG-ROOM-200', 2);
    SET v_room_id = LAST_INSERT_ID();

    INSERT INTO fee_structures (room_type_id, academic_year_id, amount) VALUES (v_room_type_id, v_year_id, 10000.00);
    SET v_fee_id = LAST_INSERT_ID();

    INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status)
    VALUES (v_student1_id, v_fee_id, 10000.00, 10000.00, '2026-12-31', 'unpaid');
    SET v_invoice_id = LAST_INSERT_ID();


    -- =========================================================================
    -- TEST CATEGORY 1: CAPACITY ENFORCEMENT TRIGGER (trg_beds_before_insert_check_capacity)
    -- =========================================================================

    -- TRG-CAP-01 (Positive): Add 2 beds to room with capacity = 2
    SET v_caught_error = 0;
    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-TRG-BED-01');
    SET v_bed1_id = LAST_INSERT_ID();
    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-TRG-BED-02');
    SET v_bed2_id = LAST_INSERT_ID();

    IF v_caught_error = 0 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-CAP-01', 'Add bed within room capacity', 'PASS', '2 beds inserted successfully into room with capacity 2.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-CAP-01', 'Add bed within room capacity', 'FAIL', 'Valid bed insertion failed unexpectedly.');
    END IF;

    -- TRG-CAP-02 (Negative): Attempt adding 3rd bed to room with capacity = 2
    SET v_caught_error = 0;
    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-TRG-BED-03');

    IF v_caught_error = 1 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-CAP-02', 'Add bed beyond room capacity', 'PASS', 'Trigger trg_beds_before_insert_check_capacity rejected 3rd bed insertion.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-CAP-02', 'Add bed beyond room capacity', 'FAIL', 'Room capacity overflow was allowed without error.');
    END IF;


    -- =========================================================================
    -- TEST CATEGORY 2: PAYMENT & BALANCE TRIGGERS
    -- =========================================================================

    -- TRG-PAY-01 (Positive): Payment within balance (4000.00 against 10000.00 outstanding)
    SET v_caught_error = 0;
    INSERT INTO payments (invoice_id, amount, payment_method, receipt_number, remarks)
    VALUES (v_invoice_id, 4000.00, 'online', 'TEST-REC-001', 'Partial payment test');

    SELECT outstanding_balance, status INTO v_balance, v_status FROM invoices WHERE invoice_id = v_invoice_id;

    IF v_caught_error = 0 AND v_balance = 6000.00 AND v_status = 'partially_paid' THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-01', 'Payment within balance updates outstanding balance', 'PASS', 'Payment of 4000 deducted outstanding balance to 6000 and status set to partially_paid.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-01', 'Payment within balance updates outstanding balance', 'FAIL', CONCAT('Balance or status mismatch. Balance: ', v_balance, ', Status: ', v_status));
    END IF;

    -- TRG-PAY-02 (Negative): Payment exceeding outstanding balance (7000.00 against 6000.00 outstanding)
    SET v_caught_error = 0;
    INSERT INTO payments (invoice_id, amount, payment_method, receipt_number, remarks)
    VALUES (v_invoice_id, 7000.00, 'cash', 'TEST-REC-002', 'Overpayment test');

    IF v_caught_error = 1 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-02', 'Payment exceeding balance rejected', 'PASS', 'Trigger trg_payments_before_insert_validate_balance correctly rejected overpayment.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-02', 'Payment exceeding balance rejected', 'FAIL', 'Overpayment was allowed without error.');
    END IF;

    -- TRG-PAY-03 (Positive): Final payment settling outstanding balance (6000.00 against 6000.00 outstanding)
    SET v_caught_error = 0;
    INSERT INTO payments (invoice_id, amount, payment_method, receipt_number, remarks)
    VALUES (v_invoice_id, 6000.00, 'bank_transfer', 'TEST-REC-003', 'Settlement payment test');

    SELECT outstanding_balance, status INTO v_balance, v_status FROM invoices WHERE invoice_id = v_invoice_id;

    IF v_caught_error = 0 AND v_balance = 0.00 AND v_status = 'paid' THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-03', 'Final payment settles balance to paid status', 'PASS', 'Payment of 6000 settled balance to 0.00 and status set to paid.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-PAY-03', 'Final payment settles balance to paid status', 'FAIL', CONCAT('Settlement failed. Balance: ', v_balance, ', Status: ', v_status));
    END IF;


    -- =========================================================================
    -- TEST CATEGORY 3: AUDIT TRAIL TRIGGERS
    -- =========================================================================

    -- TRG-AUD-01: Allocation insert generates audit log
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student1_id, v_bed1_id, '2026-08-01', 'active');
    SET v_alloc1_id = LAST_INSERT_ID();

    SELECT COUNT(*) INTO v_audit_count FROM audit_logs WHERE table_name = 'allocations' AND action = 'INSERT' AND record_id = v_alloc1_id;

    IF v_audit_count = 1 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-01', 'Allocation generates audit record', 'PASS', 'Audit log entry created for allocation insertion with JSON payload.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-01', 'Allocation generates audit record', 'FAIL', 'Audit log entry missing for allocation insertion.');
    END IF;

    -- TRG-AUD-02: Payment insert generates audit log
    SELECT COUNT(*) INTO v_audit_count FROM audit_logs WHERE table_name = 'payments' AND action = 'INSERT';

    IF v_audit_count = 2 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-02', 'Payment generates audit record', 'PASS', 'Audit log entries created for successful payment transactions.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-02', 'Payment generates audit record', 'FAIL', CONCAT('Audit log entry count mismatch. Found: ', v_audit_count, ', Expected: 2'));
    END IF;

    -- TRG-AUD-03: Transfer insert generates audit log
    -- Setup transfer
    UPDATE allocations SET status = 'transferred', end_date = '2026-08-05' WHERE allocation_id = v_alloc1_id;
    INSERT INTO allocations (student_id, bed_id, start_date, status) VALUES (v_student1_id, v_bed2_id, '2026-08-06', 'active');
    SET v_alloc2_id = LAST_INSERT_ID();

    INSERT INTO transfers (old_allocation_id, new_allocation_id, transfer_date, reason)
    VALUES (v_alloc1_id, v_alloc2_id, '2026-08-06', 'TEST-TRANSFER-REASON');
    SET v_transfer_id = LAST_INSERT_ID();

    SELECT COUNT(*) INTO v_audit_count FROM audit_logs WHERE table_name = 'transfers' AND action = 'INSERT' AND record_id = v_transfer_id;

    IF v_audit_count = 1 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-03', 'Transfer generates audit record', 'PASS', 'Audit log entry created for student transfer transaction.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-03', 'Transfer generates audit record', 'FAIL', 'Audit log entry missing for transfer transaction.');
    END IF;

    -- TRG-AUD-04: Invalid operation generates no misleading audit log
    -- Attempting an invalid payment (already tested above) should not produce an audit log entry for payments
    SELECT COUNT(*) INTO v_audit_count FROM audit_logs WHERE table_name = 'payments' AND action = 'INSERT';

    IF v_audit_count = 2 THEN
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-04', 'Invalid operation generates no misleading audit record', 'PASS', 'Rejected overpayment produced no phantom audit record.');
    ELSE
        INSERT INTO temp_trigger_test_results (test_code, test_description, result, detail)
        VALUES ('TRG-AUD-04', 'Invalid operation generates no misleading audit record', 'FAIL', 'Phantom audit record generated on rejected payment.');
    END IF;


    -- =========================================================================
    -- OUTPUT RESULTS & CLEANUP
    -- =========================================================================

    SELECT 
        CONCAT('[', result, '] ', test_code, ' — ', test_description) AS test_summary,
        detail
    FROM temp_trigger_test_results
    ORDER BY test_id ASC;

    -- Cleanup test data
    DELETE FROM audit_logs WHERE table_name IN ('allocations', 'payments', 'transfers');
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-REC-%';
    DELETE FROM invoices WHERE invoice_id = v_invoice_id;
    DELETE FROM fee_structures WHERE fee_structure_id = v_fee_id;
    DELETE FROM transfers WHERE transfer_id = v_transfer_id;
    DELETE FROM allocations WHERE student_id IN (v_student1_id, v_student2_id);
    DELETE FROM students WHERE student_id IN (v_student1_id, v_student2_id);
    DELETE FROM beds WHERE room_id = v_room_id;
    DELETE FROM rooms WHERE room_id = v_room_id;
    DELETE FROM floors WHERE floor_id = v_floor_id;
    DELETE FROM blocks WHERE block_id = v_block_id;
    DELETE FROM hostels WHERE hostel_id = v_hostel_id;
    DELETE FROM courses WHERE course_id = v_course_id;
    DELETE FROM academic_years WHERE academic_year_id = v_year_id;
    DELETE FROM room_types WHERE room_type_id = v_room_type_id;
    DELETE FROM departments WHERE department_id = v_dept_id;

    DROP TEMPORARY TABLE IF EXISTS temp_trigger_test_results;

END //

DELIMITER ;

-- Execute test suite
CALL run_trigger_tests();

-- Cleanup procedure definition
DROP PROCEDURE IF EXISTS run_trigger_tests;
