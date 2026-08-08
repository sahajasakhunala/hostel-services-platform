# HostelFlow — Systematic Domain Model & Entity Derivation

**Document ID**: HOSTEL-DM-001  
**Version**: 2.0  
**Status**: Steps 2–5 Complete — Entity Derivation, Attributes, Relationships & Ambiguity Resolution  

---

## 1. Step 2: Requirements ➔ Candidate Entity Derivation

Every entity in HostelFlow is derived directly from a functional requirement defined in `HOSTEL-REQ-001`. No entity is added without an explicit requirement justification.

| Requirement IDs | Functional Requirement Concept | Derived Candidate Entity | Justification |
|---|---|---|---|
| SM-01, SM-02, SM-04, SM-05, SM-06, SM-07, SM-08 | Student master registration, unique ID, demographic tracking | **`Student`** | Core subject of hostel stays. |
| SM-03 | Store one or more parent/emergency contacts per student | **`Guardian`** | Multivalued attribute separated into distinct entity to satisfy 1NF. |
| SM-01 | Academic department classification | **`Department`** | Lookup table preventing string duplication and transitive dependency (3NF). |
| SM-01 | Academic course/program enrollment | **`Course`** | Lookup table for degree programs (B.Tech, MBA, etc.). |
| SM-01, FM-01 | Billing and registration academic cycle context | **`AcademicYear`** | Temporal lookup context for fee schedules and allocations. |
| BA-05, BA-09 | Physical hostel building management | **`Hostel`** | Campus contains multiple hostel buildings (Boys Hostel, Girls Hostel). |
| BA-05, BA-09 | Subdivision of hostel buildings into wings | **`Block`** | Named physical wings (Block A, North Wing). |
| BA-05, BA-09 | Vertical levels within a block | **`Floor`** | Physical floor levels (Ground Floor, Floor 1, Floor 2). |
| BA-05, BA-09 | Room layout classification (Single, Double, Triple) | **`RoomType`** | Categorizes room capacity and fee structures (1NF). |
| BA-02, BA-05, BA-09, MM-01 | Physical room containing beds and requiring maintenance | **`Room`** | Physical container of beds; holds room capacity invariant. |
| BA-01, BA-02, BA-03, BA-06, BA-07 | Atomic allocatable sleeping position | **`Bed`** | Atomic allocatable unit enforcing bed-level uniqueness. |
| BA-01, BA-04, BA-06, BA-07, BA-08, BA-10 | Student ↔ Bed stay relationship over time | **`Allocation`** | Core transactional entity tracking current and historical stays. |
| TR-01, TR-02, TR-03, TR-04, TR-05, TR-06 | Historical movement linking old ➔ new allocation | **`Transfer`** | Captures causal transfer events linking allocation records. |
| VA-01, VA-02, VA-03, VA-04, VA-05 | Formal checkout with deposit/clearance status | **`VacatingRecord`** | Tracks exit clearance, refund status, and exit dates. |
| FM-01 | Room rate schedule per academic year | **`FeeStructure`** | Financial lookup defining base accommodation costs. |
| FM-02, FM-04, FM-06 | Billing statement generated for student | **`Invoice`** | Tracks student financial liabilities and outstanding balances. |
| FM-03, FM-04, FM-05 | Financial payment transactions against invoice | **`Payment`** | Records partial or full payment transactions. |
| VI-01, VI-02, VI-03, VI-04, VI-05 | Gate security check-in/out logs for guests | **`Visitor`** | Tracks external visitor identity, purpose, and time logs. |
| CM-01, CM-02 | Controlled classification of student grievances | **`ComplaintCategory`** | Reference lookup for complaint reporting and classification. |
| CM-01, CM-03, CM-04, CM-05, CM-06, CM-07 | Student-filed complaints | **`Complaint`** | Grievance tracking with priority, status, and resolution notes. |
| MM-01, MM-02, MM-03, MM-04, MM-05 | Room/equipment repair requests | **`MaintenanceRequest`** | Infrastructure repair request tracking. |
| MM-02, MM-03, MM-05 | Staff personnel assigned to repair tasks | **`MaintenanceStaff`** | Maintenance personnel assigned to requests. |
| AS-01, AS-08 | Authentication credentials | **`User`** | System login credentials (bcrypt hashes). |
| AS-02, AS-03, AS-04 | User access roles (Admin, Warden, Security, etc.) | **`Role`** | Named permission scopes. |
| AS-02, AS-03 | User ↔ Role assignment junction | **`UserRole`** | Many-to-many junction mapping users to roles. |
| AS-06, AS-07 | Audit trail for critical system actions | **`AuditLog`** | Immutable historical log of system modifications. |

---

## 2. Step 3: Entity Attribute Specifications & Lifecycles

### 2.1 Core Physical Infrastructure

* **`Hostel`**: `hostel_id` (PK), `name` (UNIQUE), `gender_type` (ENUM: 'M','F','Co-ed'), `address`
* **`Block`**: `block_id` (PK), `hostel_id` (FK), `name`
* **`Floor`**: `floor_id` (PK), `block_id` (FK), `floor_number` (INT)
* **`RoomType`**: `room_type_id` (PK), `name` (ENUM: 'Single','Double','Triple','Dormitory'), `capacity` (INT)
* **`Room`**: `room_id` (PK), `floor_id` (FK), `room_type_id` (FK), `room_number` (VARCHAR), `capacity` (INT)
* **`Bed`**: `bed_id` (PK), `room_id` (FK), `bed_code` (VARCHAR), `status` (ENUM: 'available','occupied','under_maintenance')
  * *Bed Lifecycle*: `available` ➔ `occupied` (on allocation) ➔ `available` (on vacating/transfer) or `under_maintenance`.

---

### 2.2 Student & Allocation Core

* **`Student`**: `student_id` (PK), `registration_number` (UNIQUE), `first_name`, `last_name`, `dob`, `gender`, `email` (UNIQUE), `phone`, `department_id` (FK), `course_id` (FK), `academic_year_id` (FK), `admission_date`, `status` (ENUM: 'active','inactive','graduated')
* **`Guardian`**: `guardian_id` (PK), `student_id` (FK), `name`, `relationship`, `phone`, `email`
* **`Allocation`**: `allocation_id` (PK), `student_id` (FK), `bed_id` (FK), `start_date`, `end_date` (NULLable), `status` (ENUM: 'active','vacated','transferred'), `active_bed_key` (GENERATED), `active_student_key` (GENERATED)
  * *Allocation Lifecycle*: `active` ➔ `transferred` OR `vacated`.

---

### 2.3 Financial & Service Entities

* **`FeeStructure`**: `fee_structure_id` (PK), `room_type_id` (FK), `academic_year_id` (FK), `amount` (DECIMAL 10,2)
* **`Invoice`**: `invoice_id` (PK), `student_id` (FK), `fee_structure_id` (FK), `total_amount` (DECIMAL 10,2), `outstanding_balance` (DECIMAL 10,2), `due_date`, `status` (ENUM: 'unpaid','partially_paid','paid')
* **`Payment`**: `payment_id` (PK), `invoice_id` (FK), `amount` (DECIMAL 10,2), `payment_date`, `payment_method`, `receipt_number` (UNIQUE)
* **`Visitor`**: `visitor_id` (PK), `student_id` (FK), `visitor_name`, `phone`, `id_type`, `id_number`, `purpose`, `check_in_time`, `check_out_time` (NULLable)
* **`Complaint`**: `complaint_id` (PK), `student_id` (FK), `category_id` (FK), `subject`, `description`, `priority` (ENUM: 'low','medium','high','urgent'), `status` (ENUM: 'open','in_progress','resolved','closed'), `resolution_notes`, `assigned_staff_id` (FK)
* **`MaintenanceRequest`**: `request_id` (PK), `room_id` (FK), `category` (VARCHAR), `description`, `priority`, `status` (ENUM: 'pending','assigned','in_progress','completed'), `assigned_staff_id` (FK), `cost` (DECIMAL 10,2)

---

## 3. Step 4: Relationship Cardinalities & Dependencies

```
[Hostel] 1 ──── M [Block] 1 ──── M [Floor] 1 ──── M [Room] 1 ──── M [Bed]
                                                      │
                                                      ├── M ──── 1 [RoomType]
                                                      └── 1 ──── M [MaintenanceRequest]

[Department] 1 ──── M [Course] 1 ──── M [Student] 1 ──── M [Guardian]
                                           │
                                           ├── 1 ──── M [Allocation] ──── M ──── 1 [Bed]
                                           ├── 1 ──── M [Invoice] ──── M ──── 1 [Payment]
                                           ├── 1 ──── M [Complaint]
                                           └── 1 ──── M [Visitor]
```

### Relationship Rules
1. **Hierarchy Dependence**: `Block` cannot exist without `Hostel`; `Floor` cannot exist without `Block`; `Room` cannot exist without `Floor`; `Bed` cannot exist without `Room`. (All weak structural entities with non-identifying or identifying FK constraints).
2. **Allocation Junction**: `Allocation` is a conceptual associative entity resolving the temporal M:N relationship between `Student` and `Bed`.
3. **Transfer Causal Link**: `Transfer` holds two foreign keys pointing to `Allocation`: `old_allocation_id` and `new_allocation_id`.

---

## 4. Step 5: Resolution of Ambiguous Entities

We systematically challenge candidate entities to ensure clean 3NF normalization:

| Entity | Challenge Question | Resolution & Design Decision |
|---|---|---|
| **`Course`** | Should this store individual subjects or degree programs? | **Degree Programs**: Stores academic majors (e.g., "B.Tech Computer Science"). Individual course subjects are out of hostel scope. |
| **`Guardian`** | Why separate `Guardian` from `Student` table? | **Normalized to separate table (1NF)**: A student may have multiple contact persons (Father, Mother, Local Guardian). Storing `guardian1`, `guardian2` in `Student` violates 1NF. |
| **`VacatingRecord`** | Why not just set `allocation.end_date` and status to 'vacated'? | **Dedicated table**: Formal vacating captures distinct attributes not present during active allocation: `clearance_status`, `deposit_refund_amount`, `damage_charges`, and `exit_reason`. |
| **`Transfer`** | Why not just update the `bed_id` in `Allocation`? | **Dedicated transaction entity**: Updating `bed_id` in-place loses allocation history. Closing old allocation and creating a new allocation linked by a `Transfer` record preserves complete historical provenance. |
| **`MaintenanceRequest`** | Should maintenance reference a `Bed`, `Room`, or `Hostel`? | **References `Room`**: Maintenance issues (fan, plumbing, civil, door locks) pertain to physical room units, not individual bed slots. |
| **`User` vs `Student` / `Staff`** | Should credentials live directly inside `Student`? | **Separated `User` table**: Administrative, Security, and Maintenance staff log in, but are not hostel residents. `User` handles authentication; `user_id` optionally links to `student_id` or `staff_id`. |

---

Steps 2 through 5 are complete. Every entity is justified, attributes and lifecycles defined, cardinalities mapped, and ambiguities resolved. 

We are ready to construct the formal **Conceptual ER Diagram** in Step 6.
