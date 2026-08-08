-- HostelFlow Operational View: Unresolved Complaints Report
-- Document ID: HOSTEL-VIW-006
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_unresolved_complaints AS
SELECT 
    c.complaint_id,
    c.subject,
    c.description,
    c.priority,
    c.status AS complaint_status,
    c.filed_at,
    cc.name AS category_name,
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.phone AS student_phone,
    ms.staff_id AS assigned_staff_id,
    ms.name AS assigned_staff_name,
    ms.phone AS assigned_staff_phone
FROM complaints c
JOIN complaint_categories cc ON c.category_id = cc.category_id
JOIN students s ON c.student_id = s.student_id
LEFT JOIN maintenance_staff ms ON c.assigned_staff_id = ms.staff_id
WHERE c.status IN ('open', 'in_progress');
