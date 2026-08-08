-- HostelFlow Stored Procedure: sp_allocate_bed
-- Document ID: HOSTEL-PRC-001
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS sp_allocate_bed;

DELIMITER //

CREATE PROCEDURE sp_allocate_bed(
    IN p_student_id BIGINT,
    IN p_bed_id BIGINT,
    IN p_start_date DATE,
    OUT p_status_code VARCHAR(20),
    OUT p_message VARCHAR(255),
    OUT p_allocation_id BIGINT
)
proc_label: BEGIN
    DECLARE v_student_exists INT DEFAULT 0;
    DECLARE v_bed_status VARCHAR(20);
    DECLARE v_active_alloc_count INT DEFAULT 0;

    -- Error handler for unexpected transaction failures
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Transaction aborted due to unexpected database exception.';
        SET p_allocation_id = NULL;
    END;

    SET p_allocation_id = NULL;
    START TRANSACTION;

    -- 1. Validate student existence
    SELECT COUNT(*) INTO v_student_exists
    FROM students
    WHERE student_id = p_student_id AND status = 'active';

    IF v_student_exists = 0 THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Invalid or inactive student ID specified.';
        LEAVE proc_label;
    END IF;

    -- 2. Validate bed existence and status with row lock
    SELECT status INTO v_bed_status
    FROM beds
    WHERE bed_id = p_bed_id
    FOR UPDATE;

    IF v_bed_status IS NULL THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Target bed ID does not exist.';
        LEAVE proc_label;
    END IF;

    IF v_bed_status != 'available' THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Target bed is occupied or under maintenance.';
        LEAVE proc_label;
    END IF;

    -- 3. Verify student has no active allocation
    SELECT COUNT(*) INTO v_active_alloc_count
    FROM allocations
    WHERE student_id = p_student_id AND status = 'active';

    IF v_active_alloc_count > 0 THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Student already holds an active bed allocation.';
        LEAVE proc_label;
    END IF;

    -- 4. Create allocation record
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (p_student_id, p_bed_id, p_start_date, 'active');
    SET p_allocation_id = LAST_INSERT_ID();

    -- 5. Mark bed status as occupied
    UPDATE beds SET status = 'occupied' WHERE bed_id = p_bed_id;

    COMMIT;
    SET p_status_code = 'SUCCESS';
    SET p_message = 'Bed allocation created successfully.';
END //

DELIMITER ;
