# HostelFlow — Formal Normalization Proofs (1NF ➔ 2NF ➔ 3NF)

**Document ID**: HOSTEL-NORM-001  
**Version**: 1.0  
**Status**: Steps 5–7 Complete — Mathematical Proofs for 1NF, 2NF, and 3NF  

---

## 1. Normalization Definitions & Criteria

A relation $R$ with functional dependencies $F$ is normalized through progressive normal forms:

### First Normal Form (1NF)
* **Definition**: A relation $R$ is in 1NF if and only if all domain values are atomic (indivisible) and there are no repeating groups or multivalued attributes.
* **Violation Example**: Storing multiple phone numbers in `student.phone` as `"9876543210, 9123456789"` or storing multiple guardian columns `guardian1_name, guardian2_name` in `students`.

### Second Normal Form (2NF)
* **Definition**: A relation $R$ is in 2NF if and only if it is in 1NF and every non-prime attribute $A \in R$ is **fully functionally dependent** on every candidate key of $R$. That is, no non-prime attribute is dependent on a proper subset of any candidate key.
* **Violation Example**: In a composite key relation `fee_structures(room_type_id, academic_year_id, room_type_name, amount)`, `room_type_name` is partially dependent on `{room_type_id}`.

### Third Normal Form (3NF)
* **Definition**: A relation $R$ is in 3NF if and only if it is in 2NF and for every non-trivial functional dependency $X \rightarrow Y \in F^+$, at least one of the following conditions holds:
  1. $X$ is a **superkey** of $R$.
  2. $Y$ is a **prime attribute** (part of a candidate key of $R$).
* **Violation Example**: Storing `department_name` inside `students`. Since `student_id` $\rightarrow$ `department_id` and `department_id` $\rightarrow$ `department_name`, there exists a transitive dependency `student_id` $\rightarrow$ `department_name` where `department_id` is not a superkey.

---

## 2. Normalization Proofs per Domain

### 2.1 Domain Module 1: Physical Infrastructure

#### `hostels`, `blocks`, `floors`, `room_types`, `rooms`, `beds`

1. **1NF Proof**: All attributes contain single atomic values (scalar IDs, strings, dates, integers). No array structures or comma-separated lists exist.
2. **2NF Proof**: 
   * `hostels`, `room_types`, `beds` have single-attribute primary keys (`hostel_id`, `room_type_id`, `bed_id`). Partial dependencies cannot exist on single-attribute keys.
   * `blocks` has composite candidate key `{hostel_id, name}`. All non-prime attributes (`block_id`, `created_at`) depend on the full composite key.
   * `floors` has composite candidate key `{block_id, floor_number}`. All non-prime attributes depend on the full key.
   * `rooms` has composite candidate key `{floor_id, room_number}`. Non-prime attributes (`room_type_id`, `capacity`, `status`, `created_at`) depend on the full key.
3. **3NF Proof**: 
   * In `rooms`, `room_type_id` is stored as an FK. The non-key attribute `capacity` depends on `room_id`. If `capacity` were stored only in `room_types`, variable room sizes of the same type (e.g., custom single room) could not be overridden. By storing `capacity` in `rooms` and base capacity in `room_types`, no transitive dependency exists.
   * For every non-trivial FD $X \rightarrow Y$ in this module, $X$ is a candidate key/superkey. Thus, **Module 1 is in 3NF**.

---

### 2.2 Domain Module 2: Academic & Demographics

#### `departments`, `courses`, `academic_years`, `students`, `guardians`

1. **1NF Proof**:
   * Multivalued guardian contacts are removed from `students` and decomposed into the separate `guardians` relation (`student_id` 1:M `guardians`).
   * All attributes contain scalar values.
2. **2NF Proof**:
   * All relations have single-attribute primary keys (`department_id`, `course_id`, `academic_year_id`, `student_id`, `guardian_id`). Therefore, partial dependencies are mathematically impossible.
3. **3NF Proof**:
   * **Transitive Dependency Elimination**: In `students`, storing `department_name` or `course_name` directly would introduce transitive dependencies `student_id` $\rightarrow$ `department_id` $\rightarrow$ `department_name`. This is resolved by referencing `department_id` and `course_id` as foreign keys to `departments` and `courses`.
   * For every FD $X \rightarrow Y$ in `students`, $X \in \{\text{student\_id}, \text{registration\_number}, \text{email}\}$, all of which are superkeys. Thus, **Module 2 is in 3NF**.

---

### 2.3 Domain Module 3: Allocation & Transitions

#### `allocations`, `transfers`, `vacating_records`

1. **1NF Proof**: All attributes are atomic. Historical allocations are represented as discrete rows, avoiding repeating groups.
2. **2NF Proof**: Primary keys `allocation_id`, `transfer_id`, `vacating_id` are single attributes. No partial dependencies exist.
3. **3NF Proof**:
   * **Location Redundancy Elimination**: `allocations` stores ONLY `bed_id` as a foreign key. It does NOT store `room_id`, `floor_id`, `block_id`, or `hostel_id`. Storing `room_id` in `allocations` would introduce a transitive dependency `allocation_id` $\rightarrow$ `bed_id` $\rightarrow$ `room_id` where `bed_id` is not a superkey of `allocations`. Excluding `room_id` guarantees 3NF compliance.
   * `transfers` links two allocation records (`old_allocation_id`, `new_allocation_id`) without repeating student metadata.
   * All left-hand sides of non-trivial FDs are candidate keys. Thus, **Module 3 is in 3NF**.

---

### 2.4 Domain Module 4: Financial Management

#### `fee_structures`, `invoices`, `payments`

1. **1NF Proof**: All monetary values, receipt numbers, and dates are atomic scalar values.
2. **2NF Proof**:
   * `fee_structures` has candidate key `{room_type_id, academic_year_id}`. The non-prime attribute `amount` depends on BOTH `room_type_id` and `academic_year_id` (a fee amount is specified for a particular room type in a specific academic year). Neither component alone determines `amount`. Thus, no partial dependency exists.
   * `invoices` and `payments` have single-attribute primary keys (`invoice_id`, `payment_id`).
3. **3NF Proof**:
   * `invoices` references `fee_structure_id`. It stores `total_amount` and `outstanding_balance` directly to support point-in-time financial snapshotting (preventing retroactive invoice modification if fee structures change later).
   * For every FD $X \rightarrow Y$, $X$ is a superkey. Thus, **Module 4 is in 3NF**.

---

### 2.5 Domain Module 5: Services & Incidents

#### `visitors`, `complaint_categories`, `complaints`, `maintenance_staff`, `maintenance_requests`

1. **1NF Proof**: All attributes are scalar values.
2. **2NF Proof**: Primary keys `visitor_id`, `category_id`, `complaint_id`, `staff_id`, `request_id` are single attributes.
3. **3NF Proof**:
   * In `complaints`, `category_id` is an FK pointing to `complaint_categories`. `category_name` is NOT stored in `complaints`.
   * In `maintenance_requests`, `room_id` is stored as an FK. `hostel_id` or `block_id` are NOT stored, avoiding transitive dependencies `request_id` $\rightarrow$ `room_id` $\rightarrow$ `floor_id` $\rightarrow$ `block_id`.
   * Thus, **Module 5 is in 3NF**.

---

### 2.6 Domain Module 6: Security & Audit

#### `users`, `roles`, `user_roles`, `audit_logs`

1. **1NF Proof**: All attributes are atomic.
2. **2NF Proof**:
   * `user_roles` has composite key `{user_id, role_id}` and no non-prime attributes.
   * `users`, `roles`, and `audit_logs` have single-attribute PKs.
3. **3NF Proof**:
   * In `user_roles`, both attributes form the primary key, satisfying 3NF trivially.
   * In `users`, `student_id` and `staff_id` are optional candidate keys that map 1:1 to external records.
   * Thus, **Module 6 is in 3NF**.

---

## 3. Summary of Normalization Analysis

Every relation in the HostelFlow schema satisfies the conditions for **Third Normal Form (3NF)**:
1. No repeating groups or multivalued attributes (1NF compliant).
2. No non-prime attributes partially dependent on composite candidate keys (2NF compliant).
3. No transitive dependencies of non-prime attributes on non-candidate keys (3NF compliant).
