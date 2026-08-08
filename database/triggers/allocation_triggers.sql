-- HostelFlow Allocation & Physical Capacity Triggers
-- Document ID: HOSTEL-TRG-001
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

DROP TRIGGER IF EXISTS trg_beds_before_insert_check_capacity;

DELIMITER //

-- Trigger: trg_beds_before_insert_check_capacity
-- Purpose: Enforce that total beds created in a room cannot exceed the room's physical capacity limit.
-- Concurrency Strategy: Performs a FOR UPDATE lock on the parent room row to serialize concurrent bed creation.
CREATE TRIGGER trg_beds_before_insert_check_capacity
BEFORE INSERT ON beds
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_current_bed_count INT;

    -- Lock room row for update to serialize bed count calculation under concurrent transactions
    SELECT capacity INTO v_capacity
    FROM rooms
    WHERE room_id = NEW.room_id
    FOR UPDATE;

    -- Count existing beds in the room
    SELECT COUNT(*) INTO v_current_bed_count
    FROM beds
    WHERE room_id = NEW.room_id;

    -- Check if adding new bed exceeds capacity
    IF v_current_bed_count >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERR_ROOM_CAPACITY_EXCEEDED: Cannot add bed. Physical bed count would exceed max room capacity.';
    END IF;
END //

DELIMITER ;
