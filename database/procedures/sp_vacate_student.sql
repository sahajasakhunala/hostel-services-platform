-- HostelFlow Stored Procedure: sp_vacate_student
-- Document ID: HOSTEL-PRC-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP PROCEDURE IF EXISTS sp_vacate_student;

DELIMITER //

CREATE PROCEDURE sp_vacate_student(
    IN p_student_id BIGINT,
    IN p_vacating_date DATE,
    IN p_reason VARCHAR(50),
    IN p_clearance_status VARCHAR(50),
    IN p_refund_amount DECIMAL(10,2),
    IN p_remarks TEXT,
    OUT p_status_code VARCHAR(20),
    OUT p_message VARCHAR(255),
    OUT p_vacating_id BIGINT
)
proc_label: BEGIN
    DECLARE v_alloc_id BIGINT;
    DECLARE v_bed_id BIGINT;
    DECLARE v_start_date DATE;

    -- Error handler for unexpected transaction failures
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Vacating transaction aborted due to unexpected database exception.';
        SET p_vacating_id = NULL;
    END;

    SET p_vacating_id = NULL;
    START TRANSACTION;

    -- 1. Lock active allocation record
    SELECT allocation_id, bed_id, start_date INTO v_alloc_id, v_bed_id, v_start_date
    FROM allocations
    WHERE student_id = p_student_id AND status = 'active'
    FOR UPDATE;

    IF v_alloc_id IS NULL THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'No active allocation found for specified student.';
        LEAVE proc_label;
    END IF;

    -- 2. Validate vacating date against allocation start date
    IF p_vacating_date < v_start_date THEN
        ROLLBACK;
        SET p_status_code = 'ERROR';
        SET p_message = 'Vacating date cannot precede allocation start date.';
        LEAVE proc_label;
    END IF;

    -- 3. Mark allocation vacated
    UPDATE allocations
    SET status = 'vacated', end_date = p_vacating_date
    WHERE allocation_id = v_alloc_id;

    -- 4. Release bed to available status
    UPDATE beds SET status = 'available' WHERE bed_id = v_bed_id;

    -- 5. Create vacating record
    INSERT INTO vacating_records (allocation_id, vacating_date, reason, clearance_status, deposit_refund_amount, remarks)
    VALUES (v_alloc_id, p_vacating_date, p_reason, p_clearance_status, p_refund_amount, p_remarks);
    SET p_vacating_id = LAST_INSERT_ID();

    COMMIT;
    SET p_status_code = 'SUCCESS';
    SET p_message = 'Student vacated successfully.';
END //

DELIMITER ;
