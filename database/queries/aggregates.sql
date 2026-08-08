-- HostelFlow Query Suite 4: Aggregate Queries & Grouping
-- Document ID: HOSTEL-QRY-004
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. GROUP BY with Aggregates: Bed status summary per room
SELECT 
    room_id,
    COUNT(bed_id) AS total_beds,
    SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) AS available_beds,
    SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds,
    SUM(CASE WHEN status = 'under_maintenance' THEN 1 ELSE 0 END) AS maintenance_beds
FROM beds
GROUP BY room_id;

-- 2. GROUP BY & HAVING: Departments with more than 1 student registered
SELECT 
    d.department_id,
    d.code AS department_code,
    d.name AS department_name,
    COUNT(s.student_id) AS total_students
FROM departments d
JOIN students s ON d.department_id = s.department_id
GROUP BY d.department_id, d.code, d.name
HAVING COUNT(s.student_id) > 1;

-- 3. Financial Aggregate Summary per Academic Year
SELECT 
    ay.year_label AS academic_year,
    COUNT(i.invoice_id) AS total_invoices,
    COALESCE(SUM(i.total_amount), 0.00) AS gross_billed_amount,
    COALESCE(SUM(i.total_amount - i.outstanding_balance), 0.00) AS total_collected_amount,
    COALESCE(SUM(i.outstanding_balance), 0.00) AS total_outstanding_amount
FROM academic_years ay
LEFT JOIN fee_structures fs ON ay.academic_year_id = fs.academic_year_id
LEFT JOIN invoices i ON fs.fee_structure_id = i.fee_structure_id
GROUP BY ay.academic_year_id, ay.year_label;

-- 4. Complaint statistics grouped by category and priority
SELECT 
    cc.name AS complaint_category,
    c.priority,
    COUNT(c.complaint_id) AS total_complaints,
    SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN c.status IN ('open', 'in_progress') THEN 1 ELSE 0 END) AS pending_count
FROM complaint_categories cc
LEFT JOIN complaints c ON cc.category_id = c.category_id
GROUP BY cc.category_id, cc.name, c.priority;
