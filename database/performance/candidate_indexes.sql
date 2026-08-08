-- HostelFlow Performance Engineering — Candidate Index Experiments
-- Document ID: HOSTEL-PERF-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Candidate 1: Fee Dues & Debtor Ranking Index
-- Target Query: WHERE outstanding_balance > 0 ORDER BY outstanding_balance DESC
-- Hypothesis: Indexing (outstanding_balance, due_date, student_id) avoids full table scan & filesort.
CREATE INDEX idx_invoices_outstanding_due ON invoices (outstanding_balance, due_date, student_id);

-- Candidate 2: Active Resident Allocations Index
-- Target Query: WHERE status = 'active' JOIN beds JOIN students
-- Hypothesis: Indexing (status, bed_id, student_id) provides covering index for active allocation joins.
CREATE INDEX idx_allocations_status_bed_student ON allocations (status, bed_id, student_id);

-- Candidate 3: Visitor Gate Security Active Log Index
-- Target Query: WHERE check_out_time IS NULL ORDER BY check_in_time DESC
-- Hypothesis: Indexing (check_out_time, check_in_time, student_id) optimizes active visitor filtering.
CREATE INDEX idx_visitors_checkout_checkin ON visitors (check_out_time, check_in_time, student_id);

-- Candidate 4: Unresolved Student Complaints Index
-- Target Query: WHERE status IN ('open', 'in_progress') ORDER BY filed_at DESC
-- Hypothesis: Indexing (status, filed_at, student_id) reduces rows examined for unresolved complaints.
CREATE INDEX idx_complaints_status_filed ON complaints (status, filed_at, student_id);

-- Candidate 5: Pending Maintenance Requests Index (Tested Alternative: reported_at leading)
-- Target Query: WHERE status != 'completed' ORDER BY reported_at DESC
-- Hypothesis: Indexing (reported_at, status, room_id) with reported_at leading maintains sort order across inequality !=.
CREATE INDEX idx_maint_reported_status ON maintenance_requests (reported_at, status, room_id);
