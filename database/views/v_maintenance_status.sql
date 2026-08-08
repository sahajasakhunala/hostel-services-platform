-- HostelFlow Operational View: Maintenance Status Report
-- Document ID: HOSTEL-VIW-007
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_maintenance_status AS
SELECT 
    mr.request_id,
    mr.category,
    mr.description,
    mr.priority,
    mr.status AS maintenance_status,
    mr.cost,
    mr.reported_at,
    mr.completed_at,
    h.name AS hostel_name,
    b.name AS block_name,
    fl.floor_number,
    r.room_id,
    r.room_number,
    ms.staff_id AS assigned_staff_id,
    ms.name AS assigned_staff_name,
    ms.specialty AS staff_specialty
FROM maintenance_requests mr
JOIN rooms r ON mr.room_id = r.room_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
LEFT JOIN maintenance_staff ms ON mr.assigned_staff_id = ms.staff_id;
