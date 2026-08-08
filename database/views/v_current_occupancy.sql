-- HostelFlow Operational View: Current Occupancy Report
-- Document ID: HOSTEL-VIW-001
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_current_occupancy AS
SELECT 
    a.allocation_id,
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email AS student_email,
    s.phone AS student_phone,
    h.hostel_id,
    h.name AS hostel_name,
    b.block_id,
    b.name AS block_name,
    fl.floor_number,
    r.room_id,
    r.room_number,
    rt.name AS room_type,
    bd.bed_id,
    bd.bed_code,
    a.start_date AS allocated_since
FROM allocations a
JOIN students s ON a.student_id = s.student_id
JOIN beds bd ON a.bed_id = bd.bed_id
JOIN rooms r ON bd.room_id = r.room_id
JOIN room_types rt ON r.room_type_id = rt.room_type_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
WHERE a.status = 'active';
