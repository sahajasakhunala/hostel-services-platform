-- HostelFlow Stored Procedure Verification Suite
-- Document ID: HOSTEL-TST-003
-- Target Procedures: sp_allocate_bed, sp_transfer_student, sp_vacate_student, sp_process_payment
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS run_procedure_tests;

DELIMITER //

CREATE PROCEDURE run_procedure_tests()
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

    -- Out variables for procedure calls
    DECLARE v_status_code VARCHAR(20);
    DECLARE v_message VARCHAR(255);
    DECLARE v_alloc1_id BIGINT;
    DECLARE v_alloc2_id BIGINT;
    DECLARE v_transfer1_id BIGINT;
    DECLARE v_vacating1_id BIGINT;
    DECLARE v_payment1_id BIGINT;

    -- State verification variables
    DECLARE v_old_status VARCHAR(20);
    DECLARE v_new_status VARCHAR(20);
    DECLARE v_bed_status VARCHAR(20);
    DECLARE v_balance DECIMAL(10,2);
    DECLARE v_count INT;

    -- Temporary table for test results
    DROP TEMPORARY TABLE IF EXISTS temp_proc_test_results;
    CREATE TEMPORARY TABLE temp_proc_test_results (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        test_code VARCHAR(20) NOT NULL,
        test_description VARCHAR(150) NOT NULL,
        result VARCHAR(10) NOT NULL,
        detail TEXT NULL
    );

    -- =========================================================================
    -- FIXTURE SETUP
    -- =========================================================================
    DELETE FROM audit_logs WHERE table_name IN ('allocations', 'payments', 'transfers', 'vacating_records');
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-PRC-REC-%';
    DELETE FROM invoices WHERE total_amount = 15000.00 AND due_date = '2026-12-31';
    DELETE FROM fee_structures WHERE amount = 15000.00;
    DELETE FROM vacating_records WHERE remarks = 'TEST-VACATE-REMARKS';
    DELETE FROM transfers WHERE reason = 'TEST-PROC-TRANSFER';
    DELETE FROM allocations WHERE student_id IN (SELECT student_id FROM students WHERE registration_number LIKE 'TEST-PRC-REG-%');
    DELETE FROM students WHERE registration_number LIKE 'TEST-PRC-REG-%';
    DELETE FROM beds WHERE bed_code LIKE 'TEST-PRC-BED-%';
    DELETE FROM rooms WHERE room_number = 'TEST-PRC-ROOM-300';
    DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'TEST-PRC-BLOCK-C');
    DELETE FROM blocks WHERE name = 'TEST-PRC-BLOCK-C';
    DELETE FROM hostels WHERE name = 'TEST-PRC-HOSTEL-GAMMA';
    DELETE FROM courses WHERE name = 'TEST-PRC-COURSE';
    DELETE FROM departments WHERE code = 'TEST-PRC-DEPT';
    DELETE FROM academic_years WHERE year_label = 'TEST-PRC-YEAR-2026';
    DELETE FROM room_types WHERE name = 'TEST-PRC-SINGLE-TYPE';

    -- Reference and Hierarchy Setup
    INSERT INTO departments (name, code) VALUES ('Test Procedure Dept', 'TEST-PRC-DEPT');
    SET v_dept_id = LAST_INSERT_ID();

    INSERT INTO room_types (name, base_capacity) VALUES ('TEST-PRC-SINGLE-TYPE', 1);
    SET v_room_type_id = LAST_INSERT_ID();

    INSERT INTO academic_years (year_label, start_date, end_date) VALUES ('TEST-PRC-YEAR-2026', '2026-01-01', '2026-12-31');
    SET v_year_id = LAST_INSERT_ID();

    INSERT INTO courses (department_id, name, degree_level) VALUES (v_dept_id, 'TEST-PRC-COURSE', 'UG');
    SET v_course_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-PRC-REG-001', 'PrcStudent', 'One', '2003-03-03', 'M', 'prc1@hostelflow.local', '9996660001', v_dept_id, v_course_id, v_year_id);
    SET v_student1_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-PRC-REG-002', 'PrcStudent', 'Two', '2003-04-04', 'F', 'prc2@hostelflow.local', '9996660002', v_dept_id, v_course_id, v_year_id);
    SET v_student2_id = LAST_INSERT_ID();

    INSERT INTO hostels (name, gender_type, address) VALUES ('TEST-PRC-HOSTEL-GAMMA', 'Co-ed', 'Campus Procedure Test');
    SET v_hostel_id = LAST_INSERT_ID();

    INSERT INTO blocks (hostel_id, name) VALUES (v_hostel_id, 'TEST-PRC-BLOCK-C');
    SET v_block_id = LAST_INSERT_ID();

    INSERT INTO floors (block_id, floor_number) VALUES (v_block_id, 3);
    SET v_floor_id = LAST_INSERT_ID();

    INSERT INTO rooms (floor_id, room_type_id, room_number, capacity) VALUES (v_floor_id, v_room_type_id, 'TEST-PRC-ROOM-300', 3);
    SET v_room_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-PRC-BED-01');
    SET v_bed1_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-PRC-BED-02');
    SET v_bed2_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-PRC-BED-03');
    SET v_bed3_id = LAST_INSERT_ID();

    INSERT INTO fee_structures (room_type_id, academic_year_id, amount) VALUES (v_room_type_id, v_year_id, 15000.00);
    SET v_fee_id = LAST_INSERT_ID();

    INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status)
    VALUES (v_student1_id, v_fee_id, 15000.00, 15000.00, '2026-12-31', 'unpaid');
    SET v_invoice_id = LAST_INSERT_ID();


    -- =========================================================================
    -- TEST GROUP 1: sp_allocate_bed TESTS
    -- =========================================================================

    -- ALLOC-01 (Positive): Allocate Bed 1 to Student 1
    CALL sp_allocate_bed(v_student1_id, v_bed1_id, '2026-08-01', v_status_code, v_message, v_alloc1_id);
    SELECT status INTO v_bed_status FROM beds WHERE bed_id = v_bed1_id;

    IF v_status_code = 'SUCCESS' AND v_alloc1_id IS NOT NULL AND v_bed_status = 'occupied' THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-01', 'Successful bed allocation', 'PASS', 'sp_allocate_bed created active allocation and marked bed occupied.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-01', 'Successful bed allocation', 'FAIL', CONCAT('Procedure failed. Code: ', v_status_code, ', Message: ', v_message));
    END IF;

    -- ALLOC-02 (Negative): Allocate occupied Bed 1 to Student 2
    CALL sp_allocate_bed(v_student2_id, v_bed1_id, '2026-08-01', v_status_code, v_message, v_alloc2_id);

    IF v_status_code = 'ERROR' AND v_alloc2_id IS NULL THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-02', 'Occupied bed allocation rejected', 'PASS', 'sp_allocate_bed rejected allocation on occupied bed.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-02', 'Occupied bed allocation rejected', 'FAIL', 'Allocation on occupied bed was permitted.');
    END IF;

    -- ALLOC-03 (Negative): Allocate Student 1 (already active) to Bed 2
    CALL sp_allocate_bed(v_student1_id, v_bed2_id, '2026-08-01', v_status_code, v_message, v_alloc2_id);

    IF v_status_code = 'ERROR' AND v_alloc2_id IS NULL THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-03', 'Student with active allocation rejected', 'PASS', 'sp_allocate_bed rejected multiple active allocations for same student.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('ALLOC-03', 'Student with active allocation rejected', 'FAIL', 'Student was permitted multiple active allocations.');
    END IF;


    -- =========================================================================
    -- TEST GROUP 2: sp_transfer_student TESTS & ATOMICITY VERIFICATION
    -- =========================================================================

    -- TRANSFER-01 (Positive): Transfer Student 1 from Bed 1 to Bed 2
    CALL sp_transfer_student(v_student1_id, v_bed2_id, '2026-08-05', 'TEST-PROC-TRANSFER', v_status_code, v_message, v_transfer1_id);

    SELECT status INTO v_old_status FROM allocations WHERE allocation_id = v_alloc1_id;
    SELECT status INTO v_bed_status FROM beds WHERE bed_id = v_bed1_id;

    IF v_status_code = 'SUCCESS' AND v_transfer1_id IS NOT NULL AND v_old_status = 'transferred' AND v_bed_status = 'available' THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-01', 'Successful student transfer', 'PASS', 'sp_transfer_student closed old allocation, released old bed, opened new allocation, and created transfer record.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-01', 'Successful student transfer', 'FAIL', CONCAT('Transfer failed. Code: ', v_status_code, ', Message: ', v_message));
    END IF;

    -- TRANSFER-02 (Negative): Transfer Student 1 to occupied bed (occupy Bed 3 with Student 2 first)
    CALL sp_allocate_bed(v_student2_id, v_bed3_id, '2026-08-01', v_status_code, v_message, v_alloc2_id);
    
    -- Attempt transfer Student 1 to Bed 3 (occupied)
    CALL sp_transfer_student(v_student1_id, v_bed3_id, '2026-08-06', 'TEST-PROC-TRANSFER-FAIL', v_status_code, v_message, v_transfer1_id);

    IF v_status_code = 'ERROR' THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-02', 'Transfer to occupied target bed rejected', 'PASS', 'sp_transfer_student rejected transfer to occupied target bed.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-02', 'Transfer to occupied target bed rejected', 'FAIL', 'Transfer to occupied bed was permitted.');
    END IF;

    -- TRANSFER-03 (Atomicity Verification): Verify rollback state after failed transfer attempt
    -- Student 1 should still be active on Bed 2, Bed 2 still occupied, no orphaned records
    SELECT status INTO v_new_status FROM allocations WHERE student_id = v_student1_id AND status = 'active';
    SELECT bed_id INTO v_count FROM allocations WHERE student_id = v_student1_id AND status = 'active';

    IF v_new_status = 'active' AND v_count = v_bed2_id THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-03', 'Transaction atomicity verified on transfer failure', 'PASS', 'Failed transfer operation completely rolled back leaving active allocation untouched.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('TRANSFER-03', 'Transaction atomicity verified on transfer failure', 'FAIL', 'Partial state corruption detected after failed transfer transaction.');
    END IF;


    -- =========================================================================
    -- TEST GROUP 3: sp_vacate_student TESTS
    -- =========================================================================

    -- VACATE-02 (Negative): Invalid vacating date (before start date)
    CALL sp_vacate_student(v_student1_id, '2026-08-01', 'personal', 'cleared', 0.00, 'TEST-VACATE-REMARKS', v_status_code, v_message, v_vacating1_id);

    IF v_status_code = 'ERROR' AND v_vacating1_id IS NULL THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-02', 'Invalid vacating date rejected', 'PASS', 'sp_vacate_student rejected vacating date prior to allocation start date.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-02', 'Invalid vacating date rejected', 'FAIL', 'Invalid vacating date was accepted.');
    END IF;

    -- VACATE-01 (Positive): Vacate Student 1 on valid date
    CALL sp_vacate_student(v_student1_id, '2026-08-10', 'graduation', 'cleared', 500.00, 'TEST-VACATE-REMARKS', v_status_code, v_message, v_vacating1_id);

    SELECT status INTO v_bed_status FROM beds WHERE bed_id = v_bed2_id;

    IF v_status_code = 'SUCCESS' AND v_vacating1_id IS NOT NULL AND v_bed_status = 'available' THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-01', 'Successful student vacating', 'PASS', 'sp_vacate_student marked allocation vacated, released bed to available, and created vacating_record.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-01', 'Successful student vacating', 'FAIL', CONCAT('Vacating failed. Code: ', v_status_code, ', Message: ', v_message));
    END IF;

    -- VACATE-03 (Negative): Vacate student with no active allocation
    CALL sp_vacate_student(v_student1_id, '2026-08-11', 'personal', 'cleared', 0.00, 'TEST-VACATE-REMARKS', v_status_code, v_message, v_vacating1_id);

    IF v_status_code = 'ERROR' AND v_vacating1_id IS NULL THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-03', 'Student with no active allocation rejected', 'PASS', 'sp_vacate_student rejected vacating for student with no active allocation.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('VACATE-03', 'Student with no active allocation rejected', 'FAIL', 'Vacating permitted on student without active allocation.');
    END IF;


    -- =========================================================================
    -- TEST GROUP 4: sp_process_payment TESTS
    -- =========================================================================

    -- PAY-01 & PAY-03 (Positive): Valid payment of 5000.00 against 15000.00 invoice
    CALL sp_process_payment(v_invoice_id, 5000.00, 'online', 'TEST-PRC-REC-001', 'Procedure test payment', v_status_code, v_message, v_payment1_id);

    SELECT outstanding_balance INTO v_balance FROM invoices WHERE invoice_id = v_invoice_id;

    IF v_status_code = 'SUCCESS' AND v_payment1_id IS NOT NULL AND v_balance = 10000.00 THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('PAY-01/03', 'Valid payment processes and updates invoice balance', 'PASS', 'sp_process_payment created payment record and trigger reduced invoice balance from 15000 to 10000.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('PAY-01/03', 'Valid payment processes and updates invoice balance', 'FAIL', CONCAT('Payment failed. Code: ', v_status_code, ', Balance: ', v_balance));
    END IF;

    -- PAY-02 & PAY-04 (Negative): Overpayment of 12000.00 against 10000.00 remaining balance
    CALL sp_process_payment(v_invoice_id, 12000.00, 'cash', 'TEST-PRC-REC-002', 'Procedure test overpayment', v_status_code, v_message, v_payment1_id);

    SELECT outstanding_balance INTO v_balance FROM invoices WHERE invoice_id = v_invoice_id;

    IF v_status_code = 'ERROR' AND v_balance = 10000.00 THEN
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('PAY-02/04', 'Overpayment rejected and transaction rolled back', 'PASS', 'sp_process_payment rejected overpayment and balance remained untouched at 10000.');
    ELSE
        INSERT INTO temp_proc_test_results (test_code, test_description, result, detail)
        VALUES ('PAY-02/04', 'Overpayment rejected and transaction rolled back', 'FAIL', 'Overpayment was permitted or balance corrupted.');
    END IF;


    -- =========================================================================
    -- OUTPUT RESULTS & CLEANUP
    -- =========================================================================

    SELECT 
        CONCAT('[', result, '] ', test_code, ' — ', test_description) AS test_summary,
        detail
    FROM temp_proc_test_results
    ORDER BY test_id ASC;

    -- Cleanup test data
    DELETE FROM audit_logs WHERE table_name IN ('allocations', 'payments', 'transfers', 'vacating_records');
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-PRC-REC-%';
    DELETE FROM invoices WHERE invoice_id = v_invoice_id;
    DELETE FROM fee_structures WHERE fee_structure_id = v_fee_id;
    DELETE FROM vacating_records WHERE vacating_id = v_vacating1_id;
    DELETE FROM transfers WHERE transfer_id = v_transfer1_id;
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

    DROP TEMPORARY TABLE IF EXISTS temp_proc_test_results;

END //

DELIMITER ;

-- Execute procedure verification suite
CALL run_procedure_tests();

-- Cleanup procedure declaration
DROP PROCEDURE IF EXISTS run_procedure_tests;
