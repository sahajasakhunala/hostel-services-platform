-- HostelFlow Database Integrity Verification Suite
-- Document ID: HOSTEL-TST-001
-- Target Rules: BR-02 (Bed Uniqueness), BR-03 (Student Uniqueness), BR-05 (Date Validity)
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS run_integrity_tests;

DELIMITER //

CREATE PROCEDURE run_integrity_tests()
BEGIN
    -- Local variables for fixture primary keys
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
    DECLARE v_alloc1_id BIGINT;
    DECLARE v_alloc2_id BIGINT;

    -- Exception handling variables
    DECLARE v_caught_error INT DEFAULT 0;
    
    -- Handler for catching SQL exceptions in negative test cases
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
    BEGIN
        SET v_caught_error = 1;
    END;

    -- Create temporary table to store test results
    DROP TEMPORARY TABLE IF EXISTS temp_test_results;
    CREATE TEMPORARY TABLE temp_test_results (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        test_code VARCHAR(20) NOT NULL,
        test_description VARCHAR(150) NOT NULL,
        result VARCHAR(10) NOT NULL,
        detail TEXT NULL
    );

    -- =========================================================================
    -- FIXTURE SETUP: Create isolated test environment
    -- =========================================================================
    
    -- Cleanup any existing test fixtures with test prefix
    DELETE FROM allocations WHERE student_id IN (SELECT student_id FROM students WHERE registration_number LIKE 'TEST-REG-%');
    DELETE FROM students WHERE registration_number LIKE 'TEST-REG-%';
    DELETE FROM beds WHERE bed_code LIKE 'TEST-BED-%';
    DELETE FROM rooms WHERE room_number = 'TEST-ROOM-101';
    DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'TEST-BLOCK-A');
    DELETE FROM blocks WHERE name = 'TEST-BLOCK-A';
    DELETE FROM hostels WHERE name = 'TEST-HOSTEL-ALPHA';
    DELETE FROM courses WHERE name = 'TEST-COURSE-CS';
    DELETE FROM departments WHERE code = 'TEST-DEPT';
    DELETE FROM academic_years WHERE year_label = 'TEST-YEAR-2026';
    DELETE FROM room_types WHERE name = 'TEST-SINGLE-TYPE';

    -- Insert Test Reference Data
    INSERT INTO departments (name, code) VALUES ('Test Department', 'TEST-DEPT');
    SET v_dept_id = LAST_INSERT_ID();

    INSERT INTO room_types (name, base_capacity) VALUES ('TEST-SINGLE-TYPE', 1);
    SET v_room_type_id = LAST_INSERT_ID();

    INSERT INTO academic_years (year_label, start_date, end_date) VALUES ('TEST-YEAR-2026', '2026-01-01', '2026-12-31');
    SET v_year_id = LAST_INSERT_ID();

    INSERT INTO courses (department_id, name, degree_level) VALUES (v_dept_id, 'TEST-COURSE-CS', 'UG');
    SET v_course_id = LAST_INSERT_ID();

    -- Insert Test Students
    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-REG-001', 'TestStudent', 'One', '2002-05-15', 'M', 'test1@hostelflow.local', '9998880001', v_dept_id, v_course_id, v_year_id);
    SET v_student1_id = LAST_INSERT_ID();

    INSERT INTO students (registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id)
    VALUES ('TEST-REG-002', 'TestStudent', 'Two', '2002-09-20', 'F', 'test2@hostelflow.local', '9998880002', v_dept_id, v_course_id, v_year_id);
    SET v_student2_id = LAST_INSERT_ID();

    -- Insert Test Infrastructure Hierarchy
    INSERT INTO hostels (name, gender_type, address) VALUES ('TEST-HOSTEL-ALPHA', 'Co-ed', 'Campus Test Area');
    SET v_hostel_id = LAST_INSERT_ID();

    INSERT INTO blocks (hostel_id, name) VALUES (v_hostel_id, 'TEST-BLOCK-A');
    SET v_block_id = LAST_INSERT_ID();

    INSERT INTO floors (block_id, floor_number) VALUES (v_block_id, 1);
    SET v_floor_id = LAST_INSERT_ID();

    INSERT INTO rooms (floor_id, room_type_id, room_number, capacity) VALUES (v_floor_id, v_room_type_id, 'TEST-ROOM-101', 2);
    SET v_room_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-BED-01');
    SET v_bed1_id = LAST_INSERT_ID();

    INSERT INTO beds (room_id, bed_code) VALUES (v_room_id, 'TEST-BED-02');
    SET v_bed2_id = LAST_INSERT_ID();


    -- =========================================================================
    -- TEST CATEGORY 1: BR-02 — One Active Resident Per Bed
    -- =========================================================================

    -- Setup initial active allocation for Student 1 on Bed 1
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student1_id, v_bed1_id, '2026-08-01', 'active');
    SET v_alloc1_id = LAST_INSERT_ID();

    -- Test BR-02.1 (Negative): Attempt allocating Student 2 to Bed 1 while active
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student2_id, v_bed1_id, '2026-08-01', 'active');

    IF v_caught_error = 1 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-02.1', 'Duplicate active bed rejected', 'PASS', 'MySQL UNIQUE(active_bed_key) constraint correctly rejected duplicate active allocation.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-02.1', 'Duplicate active bed rejected', 'FAIL', 'Duplicate active bed allocation was incorrectly allowed.');
    END IF;

    -- Test BR-02.2 (Positive): Vacate Student 1 allocation, then allocate Student 2 to Bed 1
    UPDATE allocations SET status = 'vacated', end_date = '2026-08-05' WHERE allocation_id = v_alloc1_id;

    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student2_id, v_bed1_id, '2026-08-06', 'active');
    SET v_alloc2_id = LAST_INSERT_ID();

    IF v_caught_error = 0 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-02.2', 'Same bed allowed after previous allocation is inactive', 'PASS', 'Bed reuse accepted after previous active allocation status changed to vacated.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-02.2', 'Same bed allowed after previous allocation is inactive', 'FAIL', 'Bed reuse was incorrectly rejected.');
    END IF;


    -- =========================================================================
    -- TEST CATEGORY 2: BR-03 — One Active Allocation Per Student
    -- =========================================================================

    -- At this point, Student 2 is active on Bed 1 (v_alloc2_id)
    -- Test BR-03.1 (Negative): Attempt allocating Student 2 to Bed 2 while already active on Bed 1
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student2_id, v_bed2_id, '2026-08-07', 'active');

    IF v_caught_error = 1 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-03.1', 'Duplicate active student rejected', 'PASS', 'MySQL UNIQUE(active_student_key) constraint correctly rejected duplicate active allocation.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-03.1', 'Duplicate active student rejected', 'FAIL', 'Student was allowed to hold multiple active allocations simultaneously.');
    END IF;

    -- Test BR-03.2 (Positive): Transfer Student 2 allocation to 'transferred', then allocate Student 2 to Bed 2
    UPDATE allocations SET status = 'transferred', end_date = '2026-08-07' WHERE allocation_id = v_alloc2_id;

    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (v_student2_id, v_bed2_id, '2026-08-08', 'active');

    IF v_caught_error = 0 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-03.2', 'Student allowed after previous allocation is inactive', 'PASS', 'New allocation accepted after previous allocation status changed to transferred.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-03.2', 'Student allowed after previous allocation is inactive', 'FAIL', 'New allocation was incorrectly rejected for student with inactive historical record.');
    END IF;


    -- =========================================================================
    -- TEST CATEGORY 3: BR-05 — Allocation Start/End Date Invariants
    -- =========================================================================

    -- Test BR-05.1 (Positive): Valid date range (end_date > start_date)
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, end_date, status)
    VALUES (v_student1_id, v_bed1_id, '2026-08-10', '2026-08-20', 'vacated');

    IF v_caught_error = 0 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.1', 'Valid allocation dates accepted', 'PASS', 'Allocation with end_date > start_date accepted.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.1', 'Valid allocation dates accepted', 'FAIL', 'Valid date range was incorrectly rejected.');
    END IF;

    -- Test BR-05.2 (Positive): Same-day allocation (end_date = start_date)
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, end_date, status)
    VALUES (v_student1_id, v_bed1_id, '2026-08-21', '2026-08-21', 'vacated');

    IF v_caught_error = 0 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.2', 'Same-day allocation dates accepted', 'PASS', 'Allocation with end_date = start_date accepted.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.2', 'Same-day allocation dates accepted', 'FAIL', 'Same-day allocation was incorrectly rejected.');
    END IF;

    -- Test BR-05.3 (Negative): Invalid date range (end_date < start_date)
    SET v_caught_error = 0;
    INSERT INTO allocations (student_id, bed_id, start_date, end_date, status)
    VALUES (v_student1_id, v_bed1_id, '2026-08-25', '2026-08-20', 'vacated');

    IF v_caught_error = 1 THEN
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.3', 'End date before start date rejected', 'PASS', 'CHECK constraint chk_allocations_dates correctly rejected invalid date range.');
    ELSE
        INSERT INTO temp_test_results (test_code, test_description, result, detail)
        VALUES ('BR-05.3', 'End date before start date rejected', 'FAIL', 'Invalid date range (end_date < start_date) was incorrectly allowed.');
    END IF;


    -- =========================================================================
    -- OUTPUT RESULTS & CLEANUP
    -- =========================================================================

    -- Output formatted test results
    SELECT 
        CONCAT('[', result, '] ', test_code, ' — ', test_description) AS test_summary,
        detail
    FROM temp_test_results
    ORDER BY test_id ASC;

    -- Cleanup test fixtures from database tables
    DELETE FROM allocations WHERE student_id IN (v_student1_id, v_student2_id);
    DELETE FROM students WHERE student_id IN (v_student1_id, v_student2_id);
    DELETE FROM beds WHERE bed_id IN (v_bed1_id, v_bed2_id);
    DELETE FROM rooms WHERE room_id = v_room_id;
    DELETE FROM floors WHERE floor_id = v_floor_id;
    DELETE FROM blocks WHERE block_id = v_block_id;
    DELETE FROM hostels WHERE hostel_id = v_hostel_id;
    DELETE FROM courses WHERE course_id = v_course_id;
    DELETE FROM academic_years WHERE academic_year_id = v_year_id;
    DELETE FROM room_types WHERE room_type_id = v_room_type_id;
    DELETE FROM departments WHERE department_id = v_dept_id;

    DROP TEMPORARY TABLE IF EXISTS temp_test_results;

END //

DELIMITER ;

-- Execute test suite
CALL run_integrity_tests();

-- Clean up test runner procedure after execution
DROP PROCEDURE IF EXISTS run_integrity_tests;
