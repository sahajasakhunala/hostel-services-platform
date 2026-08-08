-- HostelFlow Performance Engineering — Baseline EXPLAIN Execution Plans
-- Document ID: HOSTEL-PERF-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. Baseline EXPLAIN: Fee Dues & Debtor Ranking Query
EXPLAIN FORMAT=TREE
SELECT invoice_id, student_id, total_amount, outstanding_balance, due_date
FROM invoices
WHERE outstanding_balance > 0.00
ORDER BY outstanding_balance DESC;

-- 2. Baseline EXPLAIN: Active Resident Occupancy View Join Chain
EXPLAIN FORMAT=TREE
SELECT 
    a.allocation_id, s.registration_number, bd.bed_code, r.room_number, h.name AS hostel_name
FROM allocations a
JOIN students s ON a.student_id = s.student_id
JOIN beds bd ON a.bed_id = bd.bed_id
JOIN rooms r ON bd.room_id = r.room_id
JOIN floors fl ON r.floor_id = fl.floor_id
JOIN blocks b ON fl.block_id = b.block_id
JOIN hostels h ON b.hostel_id = h.hostel_id
WHERE a.status = 'active';

-- 3. Baseline EXPLAIN: Visitor Gate Security Active Log
EXPLAIN FORMAT=TREE
SELECT visitor_id, student_id, visitor_name, phone, check_in_time, check_out_time
FROM visitors
WHERE check_out_time IS NULL
ORDER BY check_in_time DESC;

-- 4. Baseline EXPLAIN: Unresolved Student Grievance Complaints
EXPLAIN FORMAT=TREE
SELECT complaint_id, student_id, category_id, subject, priority, status, filed_at
FROM complaints
WHERE status IN ('open', 'in_progress')
ORDER BY filed_at DESC;

-- 5. Baseline EXPLAIN: Pending Facility Repair Maintenance Requests
EXPLAIN FORMAT=TREE
SELECT request_id, room_id, category, priority, status, reported_at
FROM maintenance_requests
WHERE status != 'completed'
ORDER BY reported_at DESC;

-- 6. Baseline EXPLAIN: Cross-Domain Hostel Dashboard Summary Aggregation
EXPLAIN FORMAT=TREE
SELECT 
    h.name AS hostel_name,
    COUNT(DISTINCT bd.bed_id) AS total_beds,
    SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds
FROM hostels h
LEFT JOIN blocks b ON h.hostel_id = b.hostel_id
LEFT JOIN floors fl ON b.block_id = fl.block_id
LEFT JOIN rooms r ON fl.floor_id = r.floor_id
LEFT JOIN beds bd ON r.room_id = bd.room_id
GROUP BY h.hostel_id, h.name;
