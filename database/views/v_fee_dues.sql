-- HostelFlow Operational View: Fee Dues Report
-- Document ID: HOSTEL-VIW-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

CREATE OR REPLACE VIEW v_fee_dues AS
SELECT 
    i.invoice_id,
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email AS student_email,
    s.phone AS student_phone,
    ay.year_label AS academic_year,
    rt.name AS room_type,
    i.total_amount,
    (i.total_amount - i.outstanding_balance) AS paid_amount,
    i.outstanding_balance,
    i.due_date,
    i.status AS invoice_status,
    COALESCE(DATEDIFF(CURRENT_DATE, i.due_date), 0) AS days_overdue
FROM invoices i
JOIN students s ON i.student_id = s.student_id
JOIN fee_structures fs ON i.fee_structure_id = fs.fee_structure_id
JOIN academic_years ay ON fs.academic_year_id = ay.academic_year_id
JOIN room_types rt ON fs.room_type_id = rt.room_type_id
WHERE i.outstanding_balance > 0.00;
