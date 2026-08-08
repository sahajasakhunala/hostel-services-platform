-- HostelFlow Operational View: Security Visitor Log Report
-- Document ID: HOSTEL-VIW-005
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_visitor_report AS
SELECT 
    v.visitor_id,
    v.visitor_name,
    v.phone AS visitor_phone,
    v.id_type,
    v.id_number,
    v.purpose,
    v.check_in_time,
    v.check_out_time,
    IF(v.check_out_time IS NULL, 'currently_checked_in', 'checked_out') AS visitor_status,
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    h.name AS hostel_name,
    b.name AS block_name,
    r.room_number
FROM visitors v
JOIN students s ON v.student_id = s.student_id
LEFT JOIN allocations a ON s.student_id = a.student_id AND a.status = 'active'
LEFT JOIN beds bd ON a.bed_id = bd.bed_id
LEFT JOIN rooms r ON bd.room_id = r.room_id
LEFT JOIN floors fl ON r.floor_id = fl.floor_id
LEFT JOIN blocks b ON fl.block_id = b.block_id
LEFT JOIN hostels h ON b.hostel_id = h.hostel_id;
