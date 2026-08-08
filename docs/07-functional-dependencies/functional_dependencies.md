# HostelFlow — Functional Dependencies Specification

**Document ID**: HOSTEL-FD-001  
**Version**: 1.0  
**Status**: Step 4 Complete — Formal Functional Dependencies & Key Closures  

---

## 1. Overview & Notation

Functional dependencies (FDs) describe mathematical constraints between attributes in a relation $R$. An FD $X \rightarrow Y$ states that for any two tuples $t_1, t_2 \in R$, if $t_1[X] = t_2[X]$, then $t_1[Y] = t_2[Y]$.

* **Full Dependency**: An attribute $Y$ is fully functionally dependent on $X$ if $X \rightarrow Y$, and for any proper subset $Z \subset X$, $Z \not\rightarrow Y$.
* **Partial Dependency**: $Y$ is partially dependent on a composite candidate key $X$ if there exists a proper subset $Z \subset X$ such that $Z \rightarrow Y$.
* **Transitive Dependency**: $Z$ is transitively dependent on $X$ if $X \rightarrow Y$ and $Y \rightarrow Z$, where $Y \not\rightarrow X$ and $Z \notin (X \cup Y)$.

---

## 2. Functional Dependencies per Relation

### 2.1 Physical Infrastructure Domain

#### 1. `hostels`
* **Candidate Keys**: `{hostel_id}`, `{name}`
* **FDs**:
  1. `hostel_id` $\rightarrow$ `name, gender_type, address, created_at` (Full)
  2. `name` $\rightarrow$ `hostel_id, gender_type, address, created_at` (Full)
* **Dependency Type**: All non-prime attributes are fully functionally dependent on candidate keys. No partial or transitive dependencies.

#### 2. `blocks`
* **Candidate Keys**: `{block_id}`, `{hostel_id, name}`
* **FDs**:
  1. `block_id` $\rightarrow$ `hostel_id, name, created_at` (Full)
  2. `{hostel_id, name}` $\rightarrow$ `block_id, created_at` (Full)
* **Dependency Type**: All non-key attributes fully depend on candidate keys.

#### 3. `floors`
* **Candidate Keys**: `{floor_id}`, `{block_id, floor_number}`
* **FDs**:
  1. `floor_id` $\rightarrow$ `block_id, floor_number, created_at` (Full)
  2. `{block_id, floor_number}` $\rightarrow$ `floor_id, created_at` (Full)

#### 4. `room_types`
* **Candidate Keys**: `{room_type_id}`, `{name}`
* **FDs**:
  1. `room_type_id` $\rightarrow$ `name, base_capacity, created_at` (Full)
  2. `name` $\rightarrow$ `room_type_id, base_capacity, created_at` (Full)

#### 5. `rooms`
* **Candidate Keys**: `{room_id}`, `{floor_id, room_number}`
* **FDs**:
  1. `room_id` $\rightarrow$ `floor_id, room_type_id, room_number, capacity, status, created_at` (Full)
  2. `{floor_id, room_number}` $\rightarrow$ `room_id, room_type_id, capacity, status, created_at` (Full)

#### 6. `beds`
* **Candidate Keys**: `{bed_id}`, `{room_id, bed_code}`
* **FDs**:
  1. `bed_id` $\rightarrow$ `room_id, bed_code, status, created_at` (Full)
  2. `{room_id, bed_code}` $\rightarrow$ `bed_id, status, created_at` (Full)

---

### 2.2 Academic & Demographics Domain

#### 7. `departments`
* **Candidate Keys**: `{department_id}`, `{name}`, `{code}`
* **FDs**:
  1. `department_id` $\rightarrow$ `name, code` (Full)
  2. `name` $\rightarrow$ `department_id, code` (Full)
  3. `code` $\rightarrow$ `department_id, name` (Full)

#### 8. `courses`
* **Candidate Keys**: `{course_id}`, `{department_id, name}`
* **FDs**:
  1. `course_id` $\rightarrow$ `department_id, name, degree_level` (Full)
  2. `{department_id, name}` $\rightarrow$ `course_id, degree_level` (Full)

#### 9. `academic_years`
* **Candidate Keys**: `{academic_year_id}`, `{year_label}`
* **FDs**:
  1. `academic_year_id` $\rightarrow$ `year_label, start_date, end_date` (Full)
  2. `year_label` $\rightarrow$ `academic_year_id, start_date, end_date` (Full)

#### 10. `students`
* **Candidate Keys**: `{student_id}`, `{registration_number}`, `{email}`
* **FDs**:
  1. `student_id` $\rightarrow$ `registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id, status, created_at` (Full)
  2. `registration_number` $\rightarrow$ `student_id, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id, status, created_at` (Full)
  3. `email` $\rightarrow$ `student_id, registration_number, first_name, last_name, dob, gender, phone, department_id, course_id, academic_year_id, status, created_at` (Full)

#### 11. `guardians`
* **Candidate Keys**: `{guardian_id}`
* **FDs**:
  1. `guardian_id` $\rightarrow$ `student_id, name, relationship, phone, email` (Full)

---

### 2.3 Allocation & Transition Domain

#### 12. `allocations`
* **Candidate Keys**: `{allocation_id}`, `{active_bed_key}` (when not null), `{active_student_key}` (when not null)
* **FDs**:
  1. `allocation_id` $\rightarrow$ `student_id, bed_id, start_date, end_date, status, active_bed_key, active_student_key` (Full)
  2. `status, bed_id` $\rightarrow$ `active_bed_key` (Full - generated)
  3. `status, student_id` $\rightarrow$ `active_student_key` (Full - generated)

#### 13. `transfers`
* **Candidate Keys**: `{transfer_id}`
* **FDs**:
  1. `transfer_id` $\rightarrow$ `old_allocation_id, new_allocation_id, transfer_date, reason` (Full)

#### 14. `vacating_records`
* **Candidate Keys**: `{vacating_id}`, `{allocation_id}`
* **FDs**:
  1. `vacating_id` $\rightarrow$ `allocation_id, vacating_date, reason, clearance_status, deposit_refund_amount, remarks` (Full)
  2. `allocation_id` $\rightarrow$ `vacating_id, vacating_date, reason, clearance_status, deposit_refund_amount, remarks` (Full)

---

### 2.4 Financial Domain

#### 15. `fee_structures`
* **Candidate Keys**: `{fee_structure_id}`, `{room_type_id, academic_year_id}`
* **FDs**:
  1. `fee_structure_id` $\rightarrow$ `room_type_id, academic_year_id, amount` (Full)
  2. `{room_type_id, academic_year_id}` $\rightarrow$ `fee_structure_id, amount` (Full)

#### 16. `invoices`
* **Candidate Keys**: `{invoice_id}`
* **FDs**:
  1. `invoice_id` $\rightarrow$ `student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status` (Full)

#### 17. `payments`
* **Candidate Keys**: `{payment_id}`, `{receipt_number}`
* **FDs**:
  1. `payment_id` $\rightarrow$ `invoice_id, amount, payment_date, payment_method, receipt_number, remarks` (Full)
  2. `receipt_number` $\rightarrow$ `payment_id, invoice_id, amount, payment_date, payment_method, remarks` (Full)

---

### 2.5 Services & Incidents Domain

#### 18. `visitors`
* **Candidate Keys**: `{visitor_id}`
* **FDs**:
  1. `visitor_id` $\rightarrow$ `student_id, visitor_name, phone, id_type, id_number, purpose, check_in_time, check_out_time` (Full)

#### 19. `complaint_categories`
* **Candidate Keys**: `{category_id}`, `{name}`
* **FDs**:
  1. `category_id` $\rightarrow$ `name` (Full)
  2. `name` $\rightarrow$ `category_id` (Full)

#### 20. `complaints`
* **Candidate Keys**: `{complaint_id}`
* **FDs**:
  1. `complaint_id` $\rightarrow$ `student_id, category_id, subject, description, priority, status, resolution_notes, assigned_staff_id, filed_at, resolved_at` (Full)

#### 21. `maintenance_staff`
* **Candidate Keys**: `{staff_id}`
* **FDs**:
  1. `staff_id` $\rightarrow$ `name, specialty, phone` (Full)

#### 22. `maintenance_requests`
* **Candidate Keys**: `{request_id}`
* **FDs**:
  1. `request_id` $\rightarrow$ `room_id, assigned_staff_id, category, description, priority, status, cost, reported_at, completed_at` (Full)

---

### 2.6 Security & Audit Domain

#### 23. `users`
* **Candidate Keys**: `{user_id}`, `{username}`, `{student_id}` (when not null), `{staff_id}` (when not null)
* **FDs**:
  1. `user_id` $\rightarrow$ `username, password_hash, student_id, staff_id, is_active, created_at` (Full)
  2. `username` $\rightarrow$ `user_id, password_hash, student_id, staff_id, is_active, created_at` (Full)

#### 24. `roles`
* **Candidate Keys**: `{role_id}`, `{name}`
* **FDs**:
  1. `role_id` $\rightarrow$ `name, description` (Full)
  2. `name` $\rightarrow$ `role_id, description` (Full)

#### 25. `user_roles`
* **Candidate Keys**: `{user_id, role_id}`
* **FDs**:
  1. `{user_id, role_id}` $\rightarrow$ $\emptyset$ (Trivial dependency only, acts as junction set)

#### 26. `audit_logs`
* **Candidate Keys**: `{log_id}`
* **FDs**:
  1. `log_id` $\rightarrow$ `user_id, action, table_name, record_id, old_values, new_values, timestamp` (Full)

---

Step 4 is complete. All functional dependencies are explicitly specified.
