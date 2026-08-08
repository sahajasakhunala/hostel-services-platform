-- HostelFlow View Verification Suite
-- Document ID: HOSTEL-TST-004
-- Target Views: v_current_occupancy, v_vacant_beds, v_fee_dues, v_allocation_history, v_visitor_report, v_unresolved_complaints, v_maintenance_status
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS run_view_tests;

DELIMITER //

CREATE PROCEDURE run_view_tests()
BEGIN
    -- Fixture IDs
    DECLARE v_dept_id BIGINT;
    DECLARE v_room_type_id BIGINT;
    DECLARE v_year_id BIGINT;
    DECLARE v_course_id BIGINT;
    DECLARE v_student_id BIGINT;
    DECLARE v_hostel_id BIGINT;
    DECLARE v_block_id BIGINT;
    DECLARE v_floor_id BIGINT;
    DECLARE v_room_id BIGINT;
    DECLARE v_bed1_id BIGINT;
    DECLARE v_bed2_id BIGINT;
    DECLARE v_fee_id BIGINT;
    DECLARE v_invoice_id BIGINT;
    DECLARE v_complaint_cat_id BIGINT;
    DECLARE v_complaint1_id BIGINT;
    DECLARE v_complaint2_id BIGINT;
    DECLARE v_maint_req1_id BIGINT;

    -- Procedure return variables
    DECLARE v_status_code VARCHAR(20);
    DECLARE v_message VARCHAR(255);
    DECLARE v_alloc_id BIGINT;
    DECLARE v_transfer_id BIGINT;
    DECLARE v_vacating_id BIGINT;
    DECLARE v_payment_id BIGINT;

    -- Verification counts
    DECLARE v_count INT;

    -- Temporary results table
    DROP TEMPORARY TABLE IF EXISTS temp_view_test_results;
    CREATE TEMPORARY TABLE temp_view_test_results (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        test_code VARCHAR(20) NOT NULL,
        test_description VARCHAR(150) NOT NULL,
        result VARCHAR(10) NOT NULL,
        detail TEXT NULL
    );

    -- =========================================================================
    -- FIXTURE SETUP
    -- =========================================================================
    DELETE FROM maintenance_requests WHERE description = 'TEST-VIEW-MAINT';
    DELETE FROM complaints WHERE subject LIKE 'TEST-VIEW-COMP-%';
    DELETE FROM complaint_categories WHERE name = 'TEST-VIEW-CAT';
    DELETE FROM payments WHERE receipt_number = 'TEST-VIW-REC';
    DELETE FROM invoices WHERE total_amount = 20000.00;
    DELETE FROM fee_structures WHERE amount = 20000.00;
    DELETE FROM vacating_records WHERE remarks = 'TEST-VIW-VACATE';
    DELETE FROM transfers WHERE reason = 'TEST-VIW-TRANSFER';
    DELETE FROM allocations WHERE student_id IN (SELECT student_id FROM students WHERE registration_number = 'TEST-VIW-REG-001');
    DELETE FROM students WHERE registration_number = 'TEST-VIW-REG-001';
    DELETE FROM beds WHERE bed_code LIKE 'TEST-VIW-BED-%';
    DELETE FROM rooms WHERE room_number = 'TEST-VIW-ROOM-400';
    DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'TEST-VIW-BLOCK-D');
    DELETE FROM blocks WHERE name = 'TEST-VIW-BLOCK-D';
    DELETE FROM hostels WHERE name = 'TEST-VIW-HOSTEL-DELTA';
    DELETE FROM courses WHERE name = 'TEST-VIW-COURSE';
    DELETE FROM departments WHERE code = 'TEST-VIW-DEPT';
    DELETE FROM academic_years WHERE year_label = 'TEST-VIW-YEAR-2026';
    DELETE FROM room_types WHERE name = 'TEST-VIW-TYPE';

    INSERT INTO departments (name, code) VALUES ('Test View Dept', 'TEST-VIW-DEPT');
    SET v_dept_id = LAST_INSERT_ID();

    INSERT INTO room_types (name, base_capacity) VALUES ('TEST-VIW-TYPE', 2);
    SET v_room_type_id = LAST_INSERT_ID();

    INSERT INTO academic_years (year_label, start_date, end_date) VALUES ('TEST-VIW-YEAR-2026', '2026-01-01', '2026-12-31');
    SET v_year_id = LAST_INSERT_ID();

    INSERT INTO courses (department_id, name, degree_level) VALUES (v_dept_id, 'TEST-VIW-COURSE', 'UG');
    SET v_course_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-VIW-REG-001', 'ViwStudent', 'One', '2003-05-05', 'M', 'viw1@hostelflow.local', '9995550001', v_dept_id, v_course_id, v_year_id);
    SET v_student_id = LAST_INSERT_ID();

    INSERT INTO hostels (name, gender_type, address) VALUES ('TEST-VIW-HOSTEL-DELTA', 'Co-ed', 'Campus View Test');
    SET v_hostel_id = LAST_INSERT_ID();

    INSERT INTO blocks (hostel_id, name) VALUES (v_hostel_id, 'TEST-VIW-BLOCK-D');
    SET v_block_id = LAST_INSERT_ID();

    INSERT INTO floors (block_id, floor_number) VALUES (v_block_id, 4);
    SET v_floor_id = LAST_INSERT_ID();

    INSERT INTO rooms (floor_id, room_type_id, room_number, capacity) VALUES (v_floor_id, v_room_type_id, 'TEST-VIW-ROOM-400', 2);
    SET v_room_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-VIW-BED-01');
    SET v_bed1_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-VIW-BED-02');
    SET v_bed2_id = LAST_INSERT_ID();

    INSERT INTO fee_structures (room_type_id, academic_year_id, amount) VALUES (v_room_type_id, v_year_id, 20000.00);
    SET v_fee_id = LAST_INSERT_ID();

    INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status)
    VALUES (v_student_id, v_fee_id, 20000.00, 20000.00, '2026-12-31', 'unpaid');
    SET v_invoice_id = LAST_INSERT_ID();


    -- =========================================================================
    -- VIEW TESTS
    -- =========================================================================

    -- VIEW-BED-01: Verify v_vacant_beds reports both Bed 1 and Bed 2 as vacant initially
    SELECT COUNT(*) INTO v_count FROM v_vacant_beds WHERE bed_id IN (v_bed1_id, v_bed2_id);
    IF v_count = 2 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-BED-01', 'Available beds correctly reported in v_vacant_beds', 'PASS', 'Both unallocated beds appear in v_vacant_beds.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-BED-01', 'Available beds correctly reported in v_vacant_beds', 'FAIL', CONCAT('Expected 2 vacant beds, found: ', v_count));
    END IF;

    -- VIEW-OCC-01: Allocate Bed 1 to Student 1 via sp_allocate_bed and test v_current_occupancy
    CALL sp_allocate_bed(v_student_id, v_bed1_id, '2026-08-01', v_status_code, v_message, v_alloc_id);

    SELECT COUNT(*) INTO v_count FROM v_current_occupancy WHERE student_id = v_student_id AND bed_id = v_bed1_id;
    IF v_count = 1 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-OCC-01', 'Current occupancy view updates dynamically on allocation', 'PASS', 'v_current_occupancy accurately reflects active resident after allocation.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-OCC-01', 'Current occupancy view updates dynamically on allocation', 'FAIL', 'Active resident missing from v_current_occupancy.');
    END IF;

    -- VIEW-FEE-01: Verify v_fee_dues reports outstanding invoice balance
    SELECT COUNT(*) INTO v_count FROM v_fee_dues WHERE invoice_id = v_invoice_id AND outstanding_balance = 20000.00;
    IF v_count = 1 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-FEE-01', 'Fee dues view accurately reports outstanding balances', 'PASS', 'v_fee_dues reports unpaid invoice and 20000.00 outstanding balance.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-FEE-01', 'Fee dues view accurately reports outstanding balances', 'FAIL', 'Invoice missing or balance incorrect in v_fee_dues.');
    END IF;

    -- VIEW-HIST-01: Transfer student from Bed 1 to Bed 2 and check v_allocation_history
    CALL sp_transfer_student(v_student_id, v_bed2_id, '2026-08-05', 'TEST-VIW-TRANSFER', v_status_code, v_message, v_transfer_id);

    SELECT COUNT(*) INTO v_count FROM v_allocation_history WHERE student_id = v_student_id;
    IF v_count = 2 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-HIST-01', 'Allocation history preserves transferred stay records', 'PASS', 'v_allocation_history preserves both historical transferred allocation and new active allocation.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-HIST-01', 'Allocation history preserves transferred stay records', 'FAIL', CONCAT('Expected 2 history entries for student, found: ', v_count));
    END IF;

    -- VIEW-COMP-01: Test v_unresolved_complaints filtering
    INSERT INTO complaint_categories (name) VALUES ('TEST-VIEW-CAT');
    SET v_complaint_cat_id = LAST_INSERT_ID();

    INSERT INTO complaints (student_id, category_id, subject, description, priority, status)
    VALUES (v_student_id, v_complaint_cat_id, 'TEST-VIEW-COMP-OPEN', 'Open test complaint', 'medium', 'open');
    SET v_complaint1_id = LAST_INSERT_ID();

    INSERT INTO complaints (student_id, category_id, subject, description, priority, status)
    VALUES (v_student_id, v_complaint_cat_id, 'TEST-VIEW-COMP-RESOLVED', 'Resolved test complaint', 'medium', 'resolved');
    SET v_complaint2_id = LAST_INSERT_ID();

    SELECT COUNT(*) INTO v_count FROM v_unresolved_complaints WHERE student_id = v_student_id;
    IF v_count = 1 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-COMP-01', 'Unresolved complaints view includes open and excludes resolved', 'PASS', 'v_unresolved_complaints correctly isolates open complaint and excludes resolved entry.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-COMP-01', 'Unresolved complaints view includes open and excludes resolved', 'FAIL', CONCAT('Expected 1 unresolved complaint, found: ', v_count));
    END IF;

    -- VIEW-MAINT-01: Test v_maintenance_status reporting
    INSERT INTO maintenance_requests (room_id, category, description, priority, status)
    VALUES (v_room_id, 'Electrical', 'TEST-VIEW-MAINT', 'high', 'pending');
    SET v_maint_req1_id = LAST_INSERT_ID();

    SELECT COUNT(*) INTO v_count FROM v_maintenance_status WHERE request_id = v_maint_req1_id AND maintenance_status = 'pending';
    IF v_count = 1 THEN
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-MAINT-01', 'Maintenance status view accurately reports repair requests', 'PASS', 'v_maintenance_status correctly joined room, floor, block, and hostel for pending repair.');
    ELSE
        INSERT INTO temp_view_test_results (test_code, test_description, result, detail)
        VALUES ('VIEW-MAINT-01', 'Maintenance status view accurately reports repair requests', 'FAIL', 'Maintenance request missing or invalid in v_maintenance_status.');
    END IF;


    -- =========================================================================
    -- OUTPUT RESULTS & CLEANUP
    -- =========================================================================

    SELECT 
        CONCAT('[', result, '] ', test_code, ' — ', test_description) AS test_summary,
        detail
    FROM temp_view_test_results
    ORDER BY test_id ASC;

    -- Cleanup test data
    DELETE FROM maintenance_requests WHERE request_id = v_maint_req1_id;
    DELETE FROM complaints WHERE complaint_id IN (v_complaint1_id, v_complaint2_id);
    DELETE FROM complaint_categories WHERE category_id = v_complaint_cat_id;
    DELETE FROM payments WHERE receipt_number = 'TEST-VIW-REC';
    DELETE FROM invoices WHERE invoice_id = v_invoice_id;
    DELETE FROM fee_structures WHERE fee_structure_id = v_fee_id;
    DELETE FROM vacating_records WHERE remarks = 'TEST-VIW-VACATE';
    DELETE FROM transfers WHERE transfer_id = v_transfer_id;
    DELETE FROM allocations WHERE student_id = v_student_id;
    DELETE FROM students WHERE student_id = v_student_id;
    DELETE FROM beds WHERE bed_id IN (v_bed1_id, v_bed2_id);
    DELETE FROM rooms WHERE room_id = v_room_id;
    DELETE FROM floors WHERE floor_id = v_floor_id;
    DELETE FROM blocks WHERE block_id = v_block_id;
    DELETE FROM hostels WHERE hostel_id = v_hostel_id;
    DELETE FROM courses WHERE course_id = v_course_id;
    DELETE FROM academic_years WHERE academic_year_id = v_year_id;
    DELETE FROM room_types WHERE room_type_id = v_room_type_id;
    DELETE FROM departments WHERE department_id = v_dept_id;

    DROP TEMPORARY TABLE IF EXISTS temp_view_test_results;

END //

DELIMITER ;

-- Execute view test suite
CALL run_view_tests();

-- Cleanup procedure
DROP PROCEDURE IF EXISTS run_view_tests;
