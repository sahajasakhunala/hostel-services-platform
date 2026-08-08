# HostelFlow — Formal Relational Schema Specification

**Document ID**: HOSTEL-SCH-001  
**Version**: 1.0  
**Status**: Frozen — Phase 3 Steps 1–3 Complete  

---

## 1. Frozen Entity & Relationship Inventory

The database design is frozen based on the validated Phase 2 Domain Model (`HOSTEL-DM-001`). No unverified entities or ad-hoc tables have been added.

```
DOMAIN MODULE 1: PHYSICAL INFRASTRUCTURE (hostels, blocks, floors, room_types, rooms, beds)
DOMAIN MODULE 2: ACADEMIC & DEMOGRAPHICS (departments, courses, academic_years, students, guardians)
DOMAIN MODULE 3: ALLOCATION & TRANSITIONS (allocations, transfers, vacating_records)
DOMAIN MODULE 4: FINANCIAL MANAGEMENT (fee_structures, invoices, payments)
DOMAIN MODULE 5: SERVICES & INCIDENTS (visitors, complaint_categories, complaints, maintenance_requests, maintenance_staff)
DOMAIN MODULE 6: SECURITY & AUDIT (users, roles, user_roles, audit_logs)
```

---

## 2. Table Specifications

### 2.1 Domain Module 1: Physical Infrastructure

#### TABLE 1: `hostels`
* **Purpose**: Represents physical hostel buildings on campus.
* **Columns**:
  * `hostel_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(100)` **NOT NULL** **UNIQUE**
  * `gender_type` `ENUM('M', 'F', 'Co-ed')` **NOT NULL**
  * `address` `VARCHAR(255)` **NULL**
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{hostel_id}`, `{name}`
* **Foreign Keys**: None

---

#### TABLE 2: `blocks`
* **Purpose**: Represents wings or blocks within a hostel building.
* **Columns**:
  * `block_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `hostel_id` `BIGINT` **NOT NULL** (**FK** ➔ `hostels.hostel_id` ON DELETE RESTRICT)
  * `name` `VARCHAR(50)` **NOT NULL**
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{block_id}`, `{hostel_id, name}`
* **Foreign Keys**: `hostel_id` references `hostels(hostel_id)`
* **Constraints**: `UNIQUE (hostel_id, name)`

---

#### TABLE 3: `floors`
* **Purpose**: Represents physical floor levels in a block.
* **Columns**:
  * `floor_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `block_id` `BIGINT` **NOT NULL** (**FK** ➔ `blocks.block_id` ON DELETE RESTRICT)
  * `floor_number` `INT` **NOT NULL**
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{floor_id}`, `{block_id, floor_number}`
* **Foreign Keys**: `block_id` references `blocks(block_id)`
* **Constraints**: `UNIQUE (block_id, floor_number)`

---

#### TABLE 4: `room_types`
* **Purpose**: Lookup entity for room configurations and base capacities.
* **Columns**:
  * `room_type_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(50)` **NOT NULL** **UNIQUE**
  * `base_capacity` `INT` **NOT NULL**
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{room_type_id}`, `{name}`
* **Constraints**: `CHECK (base_capacity > 0)`

---

#### TABLE 5: `rooms`
* **Purpose**: Represents physical rooms on a floor.
* **Columns**:
  * `room_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `floor_id` `BIGINT` **NOT NULL** (**FK** ➔ `floors.floor_id` ON DELETE RESTRICT)
  * `room_type_id` `BIGINT` **NOT NULL** (**FK** ➔ `room_types.room_type_id` ON DELETE RESTRICT)
  * `room_number` `VARCHAR(20)` **NOT NULL**
  * `capacity` `INT` **NOT NULL**
  * `status` `ENUM('active', 'under_maintenance', 'inactive')` **DEFAULT** `'active'`
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{room_id}`, `{floor_id, room_number}`
* **Foreign Keys**:
  * `floor_id` references `floors(floor_id)`
  * `room_type_id` references `room_types(room_type_id)`
* **Constraints**:
  * `UNIQUE (floor_id, room_number)`
  * `CHECK (capacity > 0)`

---

#### TABLE 6: `beds`
* **Purpose**: Atomic allocatable sleeping slot in a room.
* **Columns**:
  * `bed_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `room_id` `BIGINT` **NOT NULL** (**FK** ➔ `rooms.room_id` ON DELETE RESTRICT)
  * `bed_code` `VARCHAR(20)` **NOT NULL**
  * `status` `ENUM('available', 'occupied', 'under_maintenance')` **DEFAULT** `'available'`
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{bed_id}`, `{room_id, bed_code}`
* **Foreign Keys**: `room_id` references `rooms(room_id)`
* **Constraints**: `UNIQUE (room_id, bed_code)`

---

### 2.2 Domain Module 2: Academic & Demographics

#### TABLE 7: `departments`
* **Purpose**: Lookup entity for academic departments.
* **Columns**:
  * `department_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(100)` **NOT NULL** **UNIQUE**
  * `code` `VARCHAR(20)` **NOT NULL** **UNIQUE**
* **Candidate Keys**: `{department_id}`, `{name}`, `{code}`

---

#### TABLE 8: `courses`
* **Purpose**: Degree program lookup entity.
* **Columns**:
  * `course_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `department_id` `BIGINT` **NOT NULL** (**FK** ➔ `departments.department_id` ON DELETE RESTRICT)
  * `name` `VARCHAR(100)` **NOT NULL**
  * `degree_level` `ENUM('UG', 'PG', 'PhD')` **NOT NULL**
* **Candidate Keys**: `{course_id}`, `{department_id, name}`
* **Foreign Keys**: `department_id` references `departments(department_id)`
* **Constraints**: `UNIQUE (department_id, name)`

---

#### TABLE 9: `academic_years`
* **Purpose**: Academic cycle context (e.g., 2025-2026).
* **Columns**:
  * `academic_year_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `year_label` `VARCHAR(20)` **NOT NULL** **UNIQUE**
  * `start_date` `DATE` **NOT NULL**
  * `end_date` `DATE` **NOT NULL**
* **Candidate Keys**: `{academic_year_id}`, `{year_label}`
* **Constraints**: `CHECK (end_date > start_date)`

---

#### TABLE 10: `students`
* **Purpose**: Master record of resident students.
* **Columns**:
  * `student_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `registration_number` `VARCHAR(50)` **NOT NULL** **UNIQUE**
  * `first_name` `VARCHAR(50)` **NOT NULL**
  * `last_name` `VARCHAR(50)` **NOT NULL**
  * `dob` `DATE` **NOT NULL**
  * `gender` `ENUM('M', 'F', 'Other')` **NOT NULL**
  * `email` `VARCHAR(100)` **NOT NULL** **UNIQUE**
  * `phone` `VARCHAR(20)` **NOT NULL**
  * `department_id` `BIGINT` **NOT NULL** (**FK** ➔ `departments.department_id` ON DELETE RESTRICT)
  * `course_id` `BIGINT` **NOT NULL** (**FK** ➔ `courses.course_id` ON DELETE RESTRICT)
  * `academic_year_id` `BIGINT` **NOT NULL** (**FK** ➔ `academic_years.academic_year_id` ON DELETE RESTRICT)
  * `status` `ENUM('active', 'inactive', 'graduated')` **DEFAULT** `'active'`
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{student_id}`, `{registration_number}`, `{email}`
* **Foreign Keys**:
  * `department_id` references `departments(department_id)`
  * `course_id` references `courses(course_id)`
  * `academic_year_id` references `academic_years(academic_year_id)`

---

#### TABLE 11: `guardians`
* **Purpose**: Emergency contacts for students (1NF separation).
* **Columns**:
  * `guardian_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `student_id` `BIGINT` **NOT NULL** (**FK** ➔ `students.student_id` ON DELETE CASCADE)
  * `name` `VARCHAR(100)` **NOT NULL**
  * `relationship` `VARCHAR(50)` **NOT NULL**
  * `phone` `VARCHAR(20)` **NOT NULL**
  * `email` `VARCHAR(100)` **NULL**
* **Candidate Keys**: `{guardian_id}`
* **Foreign Keys**: `student_id` references `students(student_id)`

---

### 2.3 Domain Module 3: Allocation & Transitions

#### TABLE 12: `allocations`
* **Purpose**: Core stay relationship linking student and bed over time.
* **Columns**:
  * `allocation_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `student_id` `BIGINT` **NOT NULL** (**FK** ➔ `students.student_id` ON DELETE RESTRICT)
  * `bed_id` `BIGINT` **NOT NULL** (**FK** ➔ `beds.bed_id` ON DELETE RESTRICT)
  * `start_date` `DATE` **NOT NULL**
  * `end_date` `DATE` **NULL**
  * `status` `ENUM('active', 'vacated', 'transferred')` **DEFAULT** `'active'`
  * `active_bed_key` `BIGINT GENERATED ALWAYS AS (IF(status = 'active', bed_id, NULL)) STORED`
  * `active_student_key` `BIGINT GENERATED ALWAYS AS (IF(status = 'active', student_id, NULL)) STORED`
* **Candidate Keys**: `{allocation_id}`, `{active_bed_key}`, `{active_student_key}`
* **Foreign Keys**:
  * `student_id` references `students(student_id)`
  * `bed_id` references `beds(bed_id)`
* **Constraints**:
  * `UNIQUE (active_bed_key)` (enforces BR-02)
  * `UNIQUE (active_student_key)` (enforces BR-03)
  * `CHECK (end_date IS NULL OR end_date >= start_date)` (enforces BR-05)

---

#### TABLE 13: `transfers`
* **Purpose**: Causal record linking old allocation to new allocation during student movement.
* **Columns**:
  * `transfer_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `old_allocation_id` `BIGINT` **NOT NULL** (**FK** ➔ `allocations.allocation_id` ON DELETE RESTRICT)
  * `new_allocation_id` `BIGINT` **NOT NULL** (**FK** ➔ `allocations.allocation_id` ON DELETE RESTRICT)
  * `transfer_date` `DATE` **NOT NULL**
  * `reason` `TEXT` **NOT NULL**
* **Candidate Keys**: `{transfer_id}`
* **Foreign Keys**:
  * `old_allocation_id` references `allocations(allocation_id)`
  * `new_allocation_id` references `allocations(allocation_id)`
* **Constraints**: `CHECK (old_allocation_id != new_allocation_id)` (enforces BR-10)

---

#### TABLE 14: `vacating_records`
* **Purpose**: Terminal record generated upon student check-out.
* **Columns**:
  * `vacating_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `allocation_id` `BIGINT` **NOT NULL** **UNIQUE** (**FK** ➔ `allocations.allocation_id` ON DELETE RESTRICT)
  * `vacating_date` `DATE` **NOT NULL**
  * `reason` `ENUM('graduation', 'transfer_out', 'disciplinary', 'personal', 'other')` **NOT NULL**
  * `clearance_status` `ENUM('cleared', 'pending_dues', 'damage_pending')` **NOT NULL**
  * `deposit_refund_amount` `DECIMAL(10,2)` **DEFAULT** `0.00`
  * `remarks` `TEXT` **NULL**
* **Candidate Keys**: `{vacating_id}`, `{allocation_id}`
* **Foreign Keys**: `allocation_id` references `allocations(allocation_id)`

---

### 2.4 Domain Module 4: Financial Management

#### TABLE 15: `fee_structures`
* **Purpose**: Lookup for accommodation fee schedules by room type and academic year.
* **Columns**:
  * `fee_structure_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `room_type_id` `BIGINT` **NOT NULL** (**FK** ➔ `room_types.room_type_id` ON DELETE RESTRICT)
  * `academic_year_id` `BIGINT` **NOT NULL** (**FK** ➔ `academic_years.academic_year_id` ON DELETE RESTRICT)
  * `amount` `DECIMAL(10,2)` **NOT NULL**
* **Candidate Keys**: `{fee_structure_id}`, `{room_type_id, academic_year_id}`
* **Foreign Keys**:
  * `room_type_id` references `room_types(room_type_id)`
  * `academic_year_id` references `academic_years(academic_year_id)`
* **Constraints**:
  * `UNIQUE (room_type_id, academic_year_id)`
  * `CHECK (amount >= 0.00)`

---

#### TABLE 16: `invoices`
* **Purpose**: Billing statements issued to students for hostel stays.
* **Columns**:
  * `invoice_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `student_id` `BIGINT` **NOT NULL** (**FK** ➔ `students.student_id` ON DELETE RESTRICT)
  * `fee_structure_id` `BIGINT` **NOT NULL** (**FK** ➔ `fee_structures.fee_structure_id` ON DELETE RESTRICT)
  * `total_amount` `DECIMAL(10,2)` **NOT NULL**
  * `outstanding_balance` `DECIMAL(10,2)` **NOT NULL**
  * `due_date` `DATE` **NOT NULL**
  * `status` `ENUM('unpaid', 'partially_paid', 'paid')` **DEFAULT** `'unpaid'`
* **Candidate Keys**: `{invoice_id}`
* **Foreign Keys**:
  * `student_id` references `students(student_id)`
  * `fee_structure_id` references `fee_structures(fee_structure_id)`
* **Constraints**:
  * `CHECK (total_amount >= 0.00)`
  * `CHECK (outstanding_balance >= 0.00 AND outstanding_balance <= total_amount)`

---

#### TABLE 17: `payments`
* **Purpose**: Individual financial transaction entries applied to an invoice.
* **Columns**:
  * `payment_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `invoice_id` `BIGINT` **NOT NULL** (**FK** ➔ `invoices.invoice_id` ON DELETE RESTRICT)
  * `amount` `DECIMAL(10,2)` **NOT NULL**
  * `payment_date` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
  * `payment_method` `ENUM('cash', 'card', 'bank_transfer', 'online')` **NOT NULL**
  * `receipt_number` `VARCHAR(50)` **NOT NULL** **UNIQUE**
  * `remarks` `VARCHAR(255)` **NULL**
* **Candidate Keys**: `{payment_id}`, `{receipt_number}`
* **Foreign Keys**: `invoice_id` references `invoices(invoice_id)`
* **Constraints**: `CHECK (amount > 0.00)`

---

### 2.5 Domain Module 5: Services & Incidents

#### TABLE 18: `visitors`
* **Purpose**: Gate security logs for external visitors.
* **Columns**:
  * `visitor_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `student_id` `BIGINT` **NOT NULL** (**FK** ➔ `students.student_id` ON DELETE RESTRICT)
  * `visitor_name` `VARCHAR(100)` **NOT NULL**
  * `phone` `VARCHAR(20)` **NOT NULL**
  * `id_type` `VARCHAR(50)` **NOT NULL**
  * `id_number` `VARCHAR(50)` **NOT NULL**
  * `purpose` `VARCHAR(255)` **NOT NULL**
  * `check_in_time` `TIMESTAMP` **NOT NULL** **DEFAULT** `CURRENT_TIMESTAMP`
  * `check_out_time` `TIMESTAMP` **NULL**
* **Candidate Keys**: `{visitor_id}`
* **Foreign Keys**: `student_id` references `students(student_id)`
* **Constraints**: `CHECK (check_out_time IS NULL OR check_out_time >= check_in_time)` (enforces BR-07)

---

#### TABLE 19: `complaint_categories`
* **Purpose**: Controlled vocabulary lookup for complaint classification.
* **Columns**:
  * `category_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(50)` **NOT NULL** **UNIQUE**
* **Candidate Keys**: `{category_id}`, `{name}`

---

#### TABLE 20: `complaints`
* **Purpose**: Student-filed grievances and resolution logs.
* **Columns**:
  * `complaint_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `student_id` `BIGINT` **NOT NULL** (**FK** ➔ `students.student_id` ON DELETE RESTRICT)
  * `category_id` `BIGINT` **NOT NULL** (**FK** ➔ `complaint_categories.category_id` ON DELETE RESTRICT)
  * `subject` `VARCHAR(150)` **NOT NULL**
  * `description` `TEXT` **NOT NULL**
  * `priority` `ENUM('low', 'medium', 'high', 'urgent')` **DEFAULT** `'medium'`
  * `status` `ENUM('open', 'in_progress', 'resolved', 'closed')` **DEFAULT** `'open'`
  * `resolution_notes` `TEXT` **NULL**
  * `assigned_staff_id` `BIGINT` **NULL**
  * `filed_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
  * `resolved_at` `TIMESTAMP` **NULL**
* **Candidate Keys**: `{complaint_id}`
* **Foreign Keys**:
  * `student_id` references `students(student_id)`
  * `category_id` references `complaint_categories(category_id)`

---

#### TABLE 21: `maintenance_staff`
* **Purpose**: Staff assigned to resolve maintenance issues.
* **Columns**:
  * `staff_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(100)` **NOT NULL**
  * `specialty` `VARCHAR(50)` **NOT NULL**
  * `phone` `VARCHAR(20)` **NOT NULL**
* **Candidate Keys**: `{staff_id}`

---

#### TABLE 22: `maintenance_requests`
* **Purpose**: Infrastructure and equipment repair tracking.
* **Columns**:
  * `request_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `room_id` `BIGINT` **NOT NULL** (**FK** ➔ `rooms.room_id` ON DELETE RESTRICT)
  * `assigned_staff_id` `BIGINT` **NULL** (**FK** ➔ `maintenance_staff.staff_id` ON DELETE SET NULL)
  * `category` `VARCHAR(50)` **NOT NULL**
  * `description` `TEXT` **NOT NULL**
  * `priority` `ENUM('low', 'medium', 'high', 'urgent')` **DEFAULT** `'medium'`
  * `status` `ENUM('pending', 'assigned', 'in_progress', 'completed')` **DEFAULT** `'pending'`
  * `cost` `DECIMAL(10,2)` **DEFAULT** `0.00`
  * `reported_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
  * `completed_at` `TIMESTAMP` **NULL**
* **Candidate Keys**: `{request_id}`
* **Foreign Keys**:
  * `room_id` references `rooms(room_id)`
  * `assigned_staff_id` references `maintenance_staff(staff_id)`

---

### 2.6 Domain Module 6: Security & Audit

#### TABLE 23: `users`
* **Purpose**: Authentication user accounts.
* **Columns**:
  * `user_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `username` `VARCHAR(50)` **NOT NULL** **UNIQUE**
  * `password_hash` `VARCHAR(255)` **NOT NULL**
  * `student_id` `BIGINT` **NULL** **UNIQUE** (**FK** ➔ `students.student_id` ON DELETE CASCADE)
  * `staff_id` `BIGINT` **NULL** **UNIQUE** (**FK** ➔ `maintenance_staff.staff_id` ON DELETE CASCADE)
  * `is_active` `BOOLEAN` **DEFAULT** `TRUE`
  * `created_at` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{user_id}`, `{username}`, `{student_id}`, `{staff_id}`
* **Foreign Keys**:
  * `student_id` references `students(student_id)`
  * `staff_id` references `maintenance_staff(staff_id)`

---

#### TABLE 24: `roles`
* **Purpose**: System security roles.
* **Columns**:
  * `role_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `name` `VARCHAR(50)` **NOT NULL** **UNIQUE**
  * `description` `VARCHAR(255)` **NULL**
* **Candidate Keys**: `{role_id}`, `{name}`

---

#### TABLE 25: `user_roles`
* **Purpose**: Junction table mapping users to security roles.
* **Columns**:
  * `user_id` `BIGINT` **NOT NULL** (**FK** ➔ `users.user_id` ON DELETE CASCADE)
  * `role_id` `BIGINT` **NOT NULL** (**FK** ➔ `roles.role_id` ON DELETE CASCADE)
* **PRIMARY KEY**: `{user_id, role_id}`
* **Foreign Keys**:
  * `user_id` references `users(user_id)`
  * `role_id` references `roles(role_id)`

---

#### TABLE 26: `audit_logs`
* **Purpose**: System modification audit trail.
* **Columns**:
  * `log_id` `BIGINT AUTO_INCREMENT` **PRIMARY KEY**
  * `user_id` `BIGINT` **NULL** (**FK** ➔ `users.user_id` ON DELETE SET NULL)
  * `action` `VARCHAR(50)` **NOT NULL**
  * `table_name` `VARCHAR(50)` **NOT NULL**
  * `record_id` `BIGINT` **NOT NULL**
  * `old_values` `JSON` **NULL**
  * `new_values` `JSON` **NULL**
  * `timestamp` `TIMESTAMP` **DEFAULT** `CURRENT_TIMESTAMP`
* **Candidate Keys**: `{log_id}`
* **Foreign Keys**: `user_id` references `users(user_id)`

---

Steps 1 to 3 of Phase 3 are complete. All 26 tables, data types, keys, constraints, and relationships are formally specified.
