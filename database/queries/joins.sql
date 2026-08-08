-- HostelFlow Query Suite 2: Relational JOIN Statements
-- Document ID: HOSTEL-QRY-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. Multi-table INNER JOIN: Complete student academic details
SELECT 
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.code AS department_code,
    c.name AS course_name,
    c.degree_level,
    ay.year_label AS academic_year
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
INNER JOIN courses c ON s.course_id = c.course_id
INNER JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
WHERE s.status = 'active';

-- 2. Multi-table INNER JOIN: Full physical hierarchy location for each bed
SELECT 
    bd.bed_id,
    bd.bed_code,
    bd.status AS bed_status,
    r.room_number,
    rt.name AS room_type,
    fl.floor_number,
    b.name AS block_name,
    h.name AS hostel_name
FROM beds bd
INNER JOIN rooms r ON bd.room_id = r.room_id
INNER JOIN room_types rt ON r.room_type_id = rt.room_type_id
INNER JOIN floors fl ON r.floor_id = fl.floor_id
INNER JOIN blocks b ON fl.block_id = b.block_id
INNER JOIN hostels h ON b.hostel_id = h.hostel_id;

-- 3. LEFT JOIN: Students and their active bed allocations (including unallocated students)
SELECT 
    s.student_id,
    s.registration_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    a.allocation_id,
    a.status AS allocation_status,
    bd.bed_code,
    r.room_number
FROM students s
LEFT JOIN allocations a ON s.student_id = a.student_id AND a.status = 'active'
LEFT JOIN beds bd ON a.bed_id = bd.bed_id
LEFT JOIN rooms r ON bd.room_id = r.room_id;

-- 4. LEFT JOIN: Invoices and their payment history
SELECT 
    i.invoice_id,
    i.student_id,
    i.total_amount,
    i.outstanding_balance,
    p.payment_id,
    p.amount AS payment_amount,
    p.payment_method,
    p.payment_date,
    p.receipt_number
FROM invoices i
LEFT JOIN payments p ON i.invoice_id = p.invoice_id
ORDER BY i.invoice_id ASC, p.payment_date DESC;
