-- HostelFlow Performance Engineering — Optimized EXPLAIN Verification Plans
-- Document ID: HOSTEL-PERF-004
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. Optimized EXPLAIN: Fee Dues Ranking (idx_invoices_outstanding_due)
EXPLAIN FORMAT=TREE
SELECT invoice_id, student_id, total_amount, outstanding_balance, due_date
FROM invoices
WHERE outstanding_balance > 0.00
ORDER BY outstanding_balance DESC;

-- 2. Optimized EXPLAIN: Active Occupancy (idx_allocations_status_bed_student)
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

-- 3. Optimized EXPLAIN: Active Visitor Log (idx_visitors_checkout_checkin)
EXPLAIN FORMAT=TREE
SELECT visitor_id, student_id, visitor_name, phone, check_in_time, check_out_time
FROM visitors
WHERE check_out_time IS NULL
ORDER BY check_in_time DESC;

-- 4. Optimized EXPLAIN: Unresolved Complaints (idx_complaints_status_filed)
EXPLAIN FORMAT=TREE
SELECT complaint_id, student_id, category_id, subject, priority, status, filed_at
FROM complaints
WHERE status IN ('open', 'in_progress')
ORDER BY filed_at DESC;

-- 5. Optimized EXPLAIN: Pending Maintenance (idx_maint_reported_status)
EXPLAIN FORMAT=TREE
SELECT request_id, room_id, category, priority, status, reported_at
FROM maintenance_requests
WHERE status != 'completed'
ORDER BY reported_at DESC;
