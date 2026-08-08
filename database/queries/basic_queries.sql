-- HostelFlow Query Suite 1: Basic SQL Statements
-- Document ID: HOSTEL-QRY-001
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. Select all active students sorted by registration number
SELECT student_id, registration_number, first_name, last_name, email, phone, status
FROM students
WHERE status = 'active'
ORDER BY registration_number ASC;

-- 2. Select all single occupancy room types
SELECT room_type_id, name, base_capacity, created_at
FROM room_types
WHERE base_capacity = 1;

-- 3. Select active room inventory with capacity > 1
SELECT room_id, floor_id, room_number, capacity, status
FROM rooms
WHERE capacity > 1 AND status = 'active'
ORDER BY room_number ASC;

-- 4. Select unpaid invoices due before the end of the year
SELECT invoice_id, student_id, total_amount, outstanding_balance, due_date, status
FROM invoices
WHERE status IN ('unpaid', 'partially_paid') AND due_date <= '2026-12-31'
ORDER BY due_date ASC;

-- 5. Search students by department code or name pattern
SELECT student_id, registration_number, first_name, last_name, email
FROM students
WHERE email LIKE '%@hostelflow.local' OR registration_number REGEXP '^TEST-REG-[0-9]+$'
ORDER BY student_id DESC;
