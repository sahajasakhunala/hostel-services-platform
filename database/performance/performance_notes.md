# HostelFlow Performance Benchmarking & Index Evaluation Notes

## 1. Candidate Index Evaluation Summary

### Candidate 1: `idx_invoices_outstanding_due (outstanding_balance, due_date, student_id)`
* **Target Query**: Fee Dues Outstanding Balance & Debtors Ranking (`v_fee_dues`, `DENSE_RANK()`)
* **Baseline EXPLAIN**: Full table scan on `invoices` with `filesort` for `ORDER BY outstanding_balance DESC`.
* **Optimized EXPLAIN**: Index range scan using `idx_invoices_outstanding_due`. Range scan directly provides ordered output for `outstanding_balance > 0`.
* **Decision**: **RETAINED (Proven Benefit)**.

### Candidate 2: `idx_allocations_status_bed_student (status, bed_id, student_id)`
* **Target Query**: Active Occupancy Join (`v_current_occupancy`)
* **Baseline EXPLAIN**: Query already utilizes unique key `uq_allocations_active_student` / `uq_allocations_active_bed` for single student/bed lookups.
* **Optimized EXPLAIN**: For bulk occupancy listings (`WHERE status = 'active'`), candidate index provides covering index scan.
* **Decision**: **RETAINED (Proven Benefit for Bulk Occupancy Views)**.

### Candidate 3: `idx_visitors_checkout_checkin (check_out_time, check_in_time, student_id)`
* **Target Query**: Gate Security Active Visitors (`v_visitor_report`)
* **Baseline EXPLAIN**: Full table scan filtering `check_out_time IS NULL`.
* **Optimized EXPLAIN**: Index lookup on `check_out_time IS NULL` drastically reduces scanned rows.
* **Decision**: **RETAINED (Proven Benefit)**.

### Candidate 4: `idx_complaints_status_filed (status, filed_at, student_id)`
* **Target Query**: Unresolved Student Grievances (`v_unresolved_complaints`)
* **Baseline EXPLAIN**: Full table scan filtering `status IN ('open', 'in_progress')`.
* **Optimized EXPLAIN**: Range scan on `status` reduces rows examined. Note: Because `IN ('open', 'in_progress')` is a multi-range predicate, filesort still occurs for `ORDER BY filed_at DESC`, but overall CPU/IO work is significantly reduced due to fewer rows scanned.
* **Decision**: **RETAINED (Substantial Row Reduction Benefit)**.

### Candidate 5: `idx_maint_reported_status (reported_at, status, room_id)`
* **Target Query**: Facility Maintenance Requests (`v_maintenance_status`)
* **Baseline EXPLAIN**: Query uses `WHERE status != 'completed' ORDER BY reported_at DESC`.
* **Optimized EXPLAIN**: Because `status != 'completed'` is an inequality predicate (`!=`), leading with `status` prevents MySQL from using the index for ordering `reported_at`. Leading with `(reported_at, status, room_id)` allows index-ordered scanning while filtering `status != 'completed'`.
* **Decision**: **RETAINED (Optimized Structure with `reported_at` Leading)**.

---

## 2. Procedural Workload Access Analysis

Critical point lookups in `sp_allocate_bed`, `sp_transfer_student`, `sp_vacate_student`, and `sp_process_payment` use indexed primary (`PRIMARY KEY`) and unique-key (`active_student_key`, `active_bed_key`, `receipt_number`) access, running in point-lookup time with row-level locking. They do not require additional indexes based on current workload demands.
