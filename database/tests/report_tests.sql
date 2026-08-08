-- HostelFlow Analytical Report Verification Suite
-- Document ID: HOSTEL-TST-005
-- Target Reports: Hostel Occupancy, Block Ranking, Fee Ranking, Stay Durations, Complaints, Maintenance, Visitors, Cross-Domain Dashboard
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS run_report_tests;

DELIMITER //

CREATE PROCEDURE run_report_tests()
BEGIN
    -- Fixture IDs
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
    DECLARE v_fee_id BIGINT;
    DECLARE v_invoice1_id BIGINT;
    DECLARE v_invoice2_id BIGINT;

    -- Verification variables
    DECLARE v_status_code VARCHAR(20);
    DECLARE v_message VARCHAR(255);
    DECLARE v_alloc1_id BIGINT;
    DECLARE v_alloc2_id BIGINT;
    DECLARE v_count INT;
    DECLARE v_pct DECIMAL(5,2);
    DECLARE v_rank INT;

    -- Temporary results table
    DROP TEMPORARY TABLE IF EXISTS temp_report_test_results;
    CREATE TEMPORARY TABLE temp_report_test_results (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        test_code VARCHAR(20) NOT NULL,
        test_description VARCHAR(150) NOT NULL,
        result VARCHAR(10) NOT NULL,
        detail TEXT NULL
    );

    -- =========================================================================
    -- FIXTURE SETUP
    -- =========================================================================
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-RPT-REC-%';
    DELETE FROM invoices WHERE total_amount IN (30000.00, 40000.00);
    DELETE FROM fee_structures WHERE amount = 30000.00;
    DELETE FROM allocations WHERE student_id IN (SELECT student_id FROM students WHERE registration_number LIKE 'TEST-RPT-REG-%');
    DELETE FROM students WHERE registration_number LIKE 'TEST-RPT-REG-%';
    DELETE FROM beds WHERE bed_code LIKE 'TEST-RPT-BED-%';
    DELETE FROM rooms WHERE room_number = 'TEST-RPT-ROOM-500';
    DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'TEST-RPT-BLOCK-E');
    DELETE FROM blocks WHERE name = 'TEST-RPT-BLOCK-E';
    DELETE FROM hostels WHERE name = 'TEST-RPT-HOSTEL-ECHO';
    DELETE FROM courses WHERE name = 'TEST-RPT-COURSE';
    DELETE FROM departments WHERE code = 'TEST-RPT-DEPT';
    DELETE FROM academic_years WHERE year_label = 'TEST-RPT-YEAR-2026';
    DELETE FROM room_types WHERE name = 'TEST-RPT-TYPE';

    INSERT INTO departments (name, code) VALUES ('Test Report Dept', 'TEST-RPT-DEPT');
    SET v_dept_id = LAST_INSERT_ID();

    INSERT INTO room_types (name, base_capacity) VALUES ('TEST-RPT-TYPE', 2);
    SET v_room_type_id = LAST_INSERT_ID();

    INSERT INTO academic_years (year_label, start_date, end_date) VALUES ('TEST-RPT-YEAR-2026', '2026-01-01', '2026-12-31');
    SET v_year_id = LAST_INSERT_ID();

    INSERT INTO courses (department_id, name, degree_level) VALUES (v_dept_id, 'TEST-RPT-COURSE', 'UG');
    SET v_course_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-RPT-REG-001', 'RptStudent', 'One', '2003-06-06', 'M', 'rpt1@hostelflow.local', '9994440001', v_dept_id, v_course_id, v_year_id);
    SET v_student1_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-RPT-REG-002', 'RptStudent', 'Two', '2003-07-07', 'F', 'rpt2@hostelflow.local', '9994440002', v_dept_id, v_course_id, v_year_id);
    SET v_student2_id = LAST_INSERT_ID();

    INSERT INTO hostels (name, gender_type, address) VALUES ('TEST-RPT-HOSTEL-ECHO', 'Co-ed', 'Campus Report Test');
    SET v_hostel_id = LAST_INSERT_ID();

    INSERT INTO blocks (hostel_id, name) VALUES (v_hostel_id, 'TEST-RPT-BLOCK-E');
    SET v_block_id = LAST_INSERT_ID();

    INSERT INTO floors (block_id, floor_number) VALUES (v_block_id, 5);
    SET v_floor_id = LAST_INSERT_ID();

    INSERT INTO rooms (floor_id, room_type_id, room_number, capacity) VALUES (v_floor_id, v_room_type_id, 'TEST-RPT-ROOM-500', 2);
    SET v_room_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-RPT-BED-01');
    SET v_bed1_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-RPT-BED-02');
    SET v_bed2_id = LAST_INSERT_ID();

    INSERT INTO fee_structures (room_type_id, academic_year_id, amount) VALUES (v_room_type_id, v_year_id, 30000.00);
    SET v_fee_id = LAST_INSERT_ID();

    INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status)
    VALUES (v_student1_id, v_fee_id, 40000.00, 40000.00, '2026-12-31', 'unpaid');
    SET v_invoice1_id = LAST_INSERT_ID();

    INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status)
    VALUES (v_student2_id, v_fee_id, 30000.00, 30000.00, '2026-12-31', 'unpaid');
    SET v_invoice2_id = LAST_INSERT_ID();


    -- =========================================================================
    -- REPORT TESTS
    -- =========================================================================

    -- RPT-OCC-01: Allocate 1 of 2 beds (50% occupancy) and verify calculation
    CALL sp_allocate_bed(v_student1_id, v_bed1_id, '2026-08-01', v_status_code, v_message, v_alloc1_id);

    SELECT 
        CASE WHEN COUNT(bd.bed_id) = 0 THEN 0.00
             ELSE ROUND((SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) / COUNT(bd.bed_id)) * 100.0, 2)
        END INTO v_pct
    FROM hostels h
    JOIN blocks b ON h.hostel_id = b.hostel_id
    JOIN floors fl ON b.block_id = fl.block_id
    JOIN rooms r ON fl.floor_id = r.floor_id
    JOIN beds bd ON r.room_id = bd.room_id
    WHERE h.hostel_id = v_hostel_id;

    IF v_pct = 50.00 THEN
        INSERT INTO temp_report_test_results (test_code, test_description, result, detail)
        VALUES ('RPT-OCC-01', 'Hostel occupancy percentage calculated correctly', 'PASS', '1 occupied bed out of 2 total beds correctly evaluated to 50.00% occupancy.');
    ELSE
        INSERT INTO temp_report_test_results (test_code, test_description, result, detail)
        VALUES ('RPT-OCC-01', 'Hostel occupancy percentage calculated correctly', 'FAIL', CONCAT('Expected 50.00%, found: ', v_pct));
    END IF;

    -- RPT-FEE-01: Verify DENSE_RANK() ordering for Student 1 (40000) vs Student 2 (30000)
    SELECT fee_due_rank INTO v_rank FROM (
        SELECT student_id, DENSE_RANK() OVER (ORDER BY outstanding_balance DESC) AS fee_due_rank
        FROM v_fee_dues
    ) rank_sub
    WHERE student_id = v_student1_id;

    IF v_rank = 1 THEN
        INSERT INTO temp_report_test_results (test_code, test_description, result, detail)
        VALUES ('RPT-FEE-01', 'Outstanding dues ranking evaluated correctly with DENSE_RANK', 'PASS', 'Student with 40000.00 outstanding balance correctly assigned rank 1.');
    ELSE
        INSERT INTO temp_report_test_results (test_code, test_description, result, detail)
        VALUES ('RPT-FEE-01', 'Outstanding dues ranking evaluated correctly with DENSE_RANK', 'FAIL', CONCAT('Expected rank 1, found: ', v_rank));
    END IF;


    -- =========================================================================
    -- OUTPUT RESULTS & CLEANUP
    -- =========================================================================

    SELECT 
        CONCAT('[', result, '] ', test_code, ' — ', test_description) AS test_summary,
        detail
    FROM temp_report_test_results
    ORDER BY test_id ASC;

    -- Cleanup test data
    DELETE FROM payments WHERE receipt_number LIKE 'TEST-RPT-REC-%';
    DELETE FROM invoices WHERE invoice_id IN (v_invoice1_id, v_invoice2_id);
    DELETE FROM fee_structures WHERE fee_structure_id = v_fee_id;
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

    DROP TEMPORARY TABLE IF EXISTS temp_report_test_results;

END //

DELIMITER ;

-- Execute report verification test suite
CALL run_report_tests();

-- Cleanup procedure declaration
DROP PROCEDURE IF EXISTS run_report_tests;
