-- HostelFlow Query Suite 3: Subqueries & Set Membership
-- Document ID: HOSTEL-QRY-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- 1. IN Subquery: Students who currently hold an active allocation
SELECT student_id, registration_number, first_name, last_name, email
FROM students
WHERE student_id IN (
    SELECT student_id 
    FROM allocations 
    WHERE status = 'active'
);

-- 2. NOT IN Subquery: Students without any active allocation
SELECT student_id, registration_number, first_name, last_name, email
FROM students
WHERE student_id NOT IN (
    SELECT student_id 
    FROM allocations 
    WHERE status = 'active'
);

-- 3. Correlated EXISTS Subquery: Rooms with at least one maintenance request pending or in_progress
SELECT r.room_id, r.room_number, r.capacity, r.status
FROM rooms r
WHERE EXISTS (
    SELECT 1 
    FROM maintenance_requests mr 
    WHERE mr.room_id = r.room_id 
      AND mr.status IN ('pending', 'in_progress')
);

-- 4. Correlated NOT EXISTS Subquery: Beds that have never been allocated
SELECT bd.bed_id, bd.bed_code, bd.room_id, bd.status
FROM beds bd
WHERE NOT EXISTS (
    SELECT 1 
    FROM allocations a 
    WHERE a.bed_id = bd.bed_id
);

-- 5. Scalar Subquery: Invoices with total amount above the average invoice amount
SELECT invoice_id, student_id, total_amount, outstanding_balance, status
FROM invoices
WHERE total_amount > (SELECT AVG(total_amount) FROM invoices);
