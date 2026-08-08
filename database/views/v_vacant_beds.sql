-- HostelFlow Operational View: Vacant Bed Inventory Report
-- Document ID: HOSTEL-VIW-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_vacant_beds AS
SELECT 
    bd.bed_id,
    bd.bed_code,
    r.room_id,
    r.room_number,
    rt.name AS room_type,
    r.capacity AS room_capacity,
    fl.floor_number,
    b.block_id,
    b.name AS block_name,
    h.hostel_id,
    h.name AS hostel_name,
    h.gender_type AS hostel_gender_type
FROM beds bd
JOIN rooms r ON bd.room_id = r.room_id
JOIN room_types rt ON r.room_type_id = rt.room_type_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
WHERE bd.status = 'available' AND r.status = 'active';
