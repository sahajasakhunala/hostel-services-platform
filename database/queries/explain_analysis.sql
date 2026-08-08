-- HostelFlow Query Performance Review & EXPLAIN Execution Plans
-- Document ID: HOSTEL-QRY-006
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. EXPLAIN Plan for Bed Allocation Active Uniqueness Lookup
EXPLAIN SELECT allocation_id, student_id, bed_id, status 
FROM allocations 
WHERE active_student_key = 1 AND status = 'active';

-- 2. EXPLAIN Plan for Active Resident Occupancy Join Chain
EXPLAIN SELECT 
    a.allocation_id, s.registration_number, bd.bed_code, r.room_number, h.name AS hostel_name
FROM allocations a
JOIN students s ON a.student_id = s.student_id
JOIN beds bd ON a.bed_id = bd.bed_id
JOIN rooms r ON bd.room_id = r.room_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
WHERE a.status = 'active';

-- 3. EXPLAIN Plan for Fee Dues Outstanding Balance Lookup
EXPLAIN SELECT invoice_id, student_id, total_amount, outstanding_balance, due_date
FROM invoices
WHERE outstanding_balance > 0.00
ORDER BY outstanding_balance DESC;

-- 4. EXPLAIN Plan for Cross-Domain Dashboard Aggregation Query
EXPLAIN SELECT 
    h.name AS hostel_name,
    COUNT(DISTINCT bd.bed_id) AS total_beds,
    SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds
FROM hostels h
LEFT JOIN blocks b ON h.hostel_id = b.hostel_id
LEFT JOIN floors fl ON b.block_id = fl.block_id
LEFT JOIN rooms r ON fl.floor_id = r.floor_id
LEFT JOIN beds bd ON r.room_id = bd.room_id
GROUP BY h.hostel_id, h.name;
