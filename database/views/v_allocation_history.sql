-- HostelFlow Operational View: Allocation Lifecycle History Report
-- Document ID: HOSTEL-VIW-004
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_allocation_history AS
SELECT 
    a.allocation_id,
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    h.name AS hostel_name,
    b.name AS block_name,
    fl.floor_number,
    r.room_number,
    bd.bed_code,
    a.start_date,
    a.end_date,
    a.status AS allocation_status,
    DATEDIFF(COALESCE(a.end_date, CURRENT_DATE), a.start_date) AS stay_duration_days,
    vr.reason AS vacating_reason,
    t.reason AS transfer_reason
FROM allocations a
JOIN students s ON a.student_id = s.student_id
JOIN beds bd ON a.bed_id = bd.bed_id
JOIN rooms r ON bd.room_id = r.room_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
LEFT JOIN vacating_records vr ON a.allocation_id = vr.allocation_id
LEFT JOIN transfers t ON a.allocation_id = t.old_allocation_id;
