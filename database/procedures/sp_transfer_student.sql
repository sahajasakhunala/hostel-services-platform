-- HostelFlow Stored Procedure: sp_transfer_student
-- Document ID: HOSTEL-PRC-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS sp_transfer_student;

DELIMITER //

CREATE PROCEDURE sp_transfer_student(
    IN p_student_id BIGINT,
    IN p_new_bed_id BIGINT,
    IN p_transfer_date DATE,
    IN p_reason TEXT,
    OUT p_status_code VARCHAR(20),
    OUT p_message VARCHAR(255),
    OUT p_transfer_id BIGINT
)
proc_label: BEGIN
    DECLARE v_old_alloc_id BIGINT;
    DECLARE v_old_bed_id BIGINT;
    DECLARE v_new_bed_status VARCHAR(20);
    DECLARE v_new_alloc_id BIGINT;

    -- Error handler for unexpected transaction failures
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Transfer transaction aborted due to unexpected database exception.';
        SET p_transfer_id = NULL;
    END;

    SET p_transfer_id = NULL;
    START TRANSACTION;

    -- 1. Lock student active allocation
    SELECT allocation_id, bed_id INTO v_old_alloc_id, v_old_bed_id
    FROM allocations
    WHERE student_id = p_student_id AND status = 'active'
    FOR UPDATE;

    IF v_old_alloc_id IS NULL THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'No active bed allocation found for the specified student.';
        LEAVE proc_label;
    END IF;

    -- 2. Prevent transfer to the exact same bed
    IF v_old_bed_id = p_new_bed_id THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Target bed is identical to current allocated bed.';
        LEAVE proc_label;
    END IF;

    -- 3. Lock and validate target bed availability
    SELECT status INTO v_new_bed_status
    FROM beds
    WHERE bed_id = p_new_bed_id
    FOR UPDATE;

    IF v_new_bed_status IS NULL THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Target bed ID does not exist.';
        LEAVE proc_label;
    END IF;

    IF v_new_bed_status != 'available' THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Target bed is occupied or under maintenance.';
        LEAVE proc_label;
    END IF;

    -- 4. Close old allocation
    UPDATE allocations
    SET status = 'transferred', end_date = p_transfer_date
    WHERE allocation_id = v_old_alloc_id;

    -- 5. Release old bed
    UPDATE beds SET status = 'available' WHERE bed_id = v_old_bed_id;

    -- 6. Create new allocation
    INSERT INTO allocations (student_id, bed_id, start_date, status)
    VALUES (p_student_id, p_new_bed_id, p_transfer_date, 'active');
    SET v_new_alloc_id = LAST_INSERT_ID();

    -- 7. Mark new bed occupied
    UPDATE beds SET status = 'occupied' WHERE bed_id = p_new_bed_id;

    -- 8. Create transfer record linking allocations
    INSERT INTO transfers (old_allocation_id, new_allocation_id, transfer_date, reason)
    VALUES (v_old_alloc_id, v_new_alloc_id, p_transfer_date, p_reason);
    SET p_transfer_id = LAST_INSERT_ID();

    COMMIT;
    SET p_status_code = 'SUCCESS';
    SET p_message = 'Student transfer processed successfully.';
END //

DELIMITER ;
