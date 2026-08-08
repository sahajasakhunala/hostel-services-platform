# HostelFlow — Domain Model

**Document ID**: HOSTEL-DM-001  
**Version**: 1.0  
**Status**: Draft  

This document defines the structural entities, their justifications, and relationship properties (cardinality and participation) of the HostelFlow system.

---

## 1. Entity Inventory & Justifications

Every entity is designed to meet normalization requirements (3NF) and business flows.

### 1.1 Structural Entities

| Entity | Attributes | Justification |
|---|---|---|
| `Hostel` | `hostel_id`, `name`, `type` (M/F), `warden_name` | Supports multi-hostel operations (e.g., Boys vs Girls hostels). |
| `Block` | `block_id`, `hostel_id`, `name` | Separates physical wings of large hostels (e.g., Block A, Block B). |
| `Floor` | `floor_id`, `block_id`, `floor_number` | Organizes rooms on physical floors (e.g., Floor 1, Floor 2). |
| `RoomType` | `room_type_id`, `name`, `base_capacity` | Standardizes room layout configurations (Single, Double, Triple) and prevents repeating metadata (1NF). |
| `Room` | `room_id`, `floor_id`, `room_type_id`, `room_number`, `capacity` | Physical room containing beds. Capacity is validated against bed count. |
| `Bed` | `bed_id`, `room_id`, `bed_code`, `status` | The atomic allocatable unit. Enforces the *Capacity-through-Beds* invariant. |

### 1.2 Core Domain Entities

| Entity | Attributes | Justification |
|---|---|---|
| `Student` | `student_id`, `registration_number`, `name`, `dob`, `gender`, `email`, `phone`, `status` | Captures student demographics. Linked to academic details. |
| `Guardian` | `guardian_id`, `student_id`, `name`, `relationship`, `phone` | Emergency contacts. Separated because a student can have multiple guardians (1NF). |
| `Department` | `department_id`, `name` | Academic department lookup to avoid transitive dependencies (3NF). |
| `Course` | `course_id`, `department_id`, `name` | Academic program lookup. |
| `AcademicYear` | `academic_year_id`, `name` | Separates context of billing, fees, and stays by academic cycle. |

### 1.3 Transactional Entities

| Entity | Attributes | Justification |
|---|---|---|
| `Allocation` | `allocation_id`, `student_id`, `bed_id`, `start_date`, `end_date`, `status` | Core transition record tracking student stays. Holds generated uniqueness keys. |
| `Transfer` | `transfer_id`, `old_allocation_id`, `new_allocation_id`, `transfer_date`, `reason` | Records structural shifts in residency and provides causal history. |
| `VacatingRecord` | `vacating_id`, `allocation_id`, `vacating_date`, `reason`, `clearance_status` | Formally checks out a resident. Separated due to distinct post-occupancy attributes. |

### 1.4 Financial Entities

| Entity | Attributes | Justification |
|---|---|---|
| `FeeStructure` | `fee_structure_id`, `room_type_id`, `academic_year_id`, `amount` | Holds lookup amounts for invoicing (3NF). |
| `Invoice` | `invoice_id`, `student_id`, `fee_structure_id`, `total_amount`, `outstanding_balance` | Tracks financial liabilities of a student stay. |
| `Payment` | `payment_id`, `invoice_id`, `amount`, `payment_date`, `method`, `receipt_number` | Tracks financial transactions against outstanding invoices. |

### 1.5 Service & Incident Entities

| Entity | Attributes | Justification |
|---|---|---|
| `Visitor` | `visitor_id`, `student_id`, `name`, `phone`, `id_type`, `id_number`, `check_in_time`, `check_out_time` | Tracks security entry/exit logs at gate level. |
| `ComplaintCategory` | `category_id`, `name` | Normalizes categories (3NF) to ensure reporting statistics. |
| `Complaint` | `complaint_id`, `student_id`, `category_id`, `subject`, `description`, `priority`, `status` | grievance filing and resolution path. |
| `MaintenanceRequest` | `request_id`, `room_id`, `staff_id`, `category`, `description`, `status`, `cost` | Room repair logging. |
| `MaintenanceStaff` | `staff_id`, `name`, `specialty`, `phone` | Resolving resource assignments. |

---

## 2. Relationship Analysis

| Relationship | Cardinality | Participation | Description |
|---|---|---|---|
| Hostel ➔ Block | 1 : M | Mandatory (Block) : Optional (Hostel) | A hostel has one or more blocks. |
| Block ➔ Floor | 1 : M | Mandatory (Floor) : Optional (Block) | A block has one or more floors. |
| Floor ➔ Room | 1 : M | Mandatory (Room) : Optional (Floor) | A floor has one or more rooms. |
| RoomType ➔ Room | 1 : M | Mandatory (Room) : Optional (RoomType) | A room must belong to a defined room type. |
| Room ➔ Bed | 1 : M | Mandatory (Bed) : Optional (Room) | A room holds one or more beds (up to room capacity). |
| Student ➔ Guardian | 1 : M | Mandatory (Guardian) : Optional (Student) | A student can have multiple guardians. |
| Course ➔ Student | 1 : M | Mandatory (Student) : Optional (Course) | A student is enrolled in exactly one course. |
| Student ➔ Allocation | 1 : M | Optional (Student) : Mandatory (Allocation) | A student may have historical stays, but at most one active. |
| Bed ➔ Allocation | 1 : M | Optional (Bed) : Mandatory (Allocation) | A bed can have historical occupancies, but at most one active. |
| Allocation ➔ VacatingRecord | 1 : 1 | Optional (Allocation) : Mandatory (Vacating) | An allocation may end in vacating. |
| Transfer ➔ Allocation | 2 : 1 | Optional (Allocation) : Mandatory (Transfer) | A transfer record links one old and one new allocation. |
| Invoice ➔ Payment | 1 : M | Optional (Invoice) : Mandatory (Payment) | An invoice may have multiple payments applied. |
| Student ➔ Complaint | 1 : M | Optional (Student) : Mandatory (Complaint) | A student files complaints. |
| Room ➔ MaintenanceRequest | 1 : M | Optional (Room) : Mandatory (Request) | Maintenance is requested for a room. |
