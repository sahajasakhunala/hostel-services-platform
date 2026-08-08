# HostelFlow — Comprehensive Actor & Use Case Model

**Document ID**: HOSTEL-UC-001  
**Version**: 2.0  
**Status**: Step 1 Complete — Actor / Use Case Traceability Matrix  

---

## 1. Overview & Traceability Matrix

Every use case in HostelFlow maps directly to one or more functional requirements defined in `HOSTEL-REQ-001`. This matrix establishes the complete operational surface area of the system before any entity modeling begins.

### 1.1 Actor Summary

| Actor | Description | Primary Responsibility |
|---|---|---|
| **Administrator** | System-wide administrative user with full privilege scope | System configuration, infrastructure management, fee definition, student onboarding |
| **Warden** | Operational manager assigned to specific hostel(s) / block(s) | Student oversight, bed allocation, transfer approval, hostel complaint/maintenance review |
| **Security Staff** | Gate security officer | Visitor logging (check-in / check-out), gate pass verification |
| **Maintenance Staff** | Infrastructure repair personnel | Resolving assigned maintenance requests, logging work notes and costs |
| **Student** | Resident student assigned to or requesting hostel accommodation | Profile view, fee tracking, filing complaints, filing maintenance requests |

---

### 1.2 Full Actor / Use Case Matrix

| Use Case ID | Use Case Name | Primary Actor | Secondary Actors | Mapped Requirement IDs |
|---|---|---|---|---|
| **UC-AD-01** | Register Student | Administrator | — | SM-01, SM-02, SM-03 |
| **UC-AD-02** | Search & Update Student Profile | Administrator | Warden | SM-04, SM-05, SM-08 |
| **UC-AD-03** | Deactivate Student Record | Administrator | — | SM-06, SM-07 |
| **UC-AD-04** | Manage Hostel Hierarchy (Hostel/Block/Floor/Room/Bed) | Administrator | — | BA-05 |
| **UC-AD-05** | Define Fee Structures | Administrator | — | FM-01 |
| **UC-AD-06** | Generate Student Invoice | Administrator | System | FM-02, FM-06 |
| **UC-AD-07** | Record Fee Payment | Administrator | Student | FM-03, FM-04, FM-05, FM-06 |
| **UC-AD-08** | Manage System Users & Roles | Administrator | — | AS-01, AS-02, AS-03, AS-08 |
| **UC-AD-09** | View Audit Logs | Administrator | — | AS-06, AS-07 |
| **UC-WA-01** | View Visual Room Grid | Warden | Administrator | BA-09 |
| **UC-WA-02** | Allocate Student to Bed | Warden | Administrator | BA-01, BA-02, BA-03, BA-04, BA-06, BA-07, BA-08, BA-10 |
| **UC-WA-03** | Initiate & Process Student Transfer | Warden | Administrator | TR-01, TR-02, TR-03, TR-04, TR-05, TR-06 |
| **UC-WA-04** | Process Student Vacating | Warden | Administrator | VA-01, VA-02, VA-03, VA-04, VA-05 |
| **UC-WA-05** | Assign & Resolve Complaints | Warden | Administrator | CM-03, CM-04, CM-06 |
| **UC-WA-06** | Assign Maintenance Tasks | Warden | Administrator | MM-03 |
| **UC-SE-01** | Visitor Check-In | Security Staff | — | VI-01 |
| **UC-SE-02** | Visitor Check-Out | Security Staff | — | VI-02, VI-03 |
| **UC-SE-03** | Search Today's Visitor Logs | Security Staff | Warden | VI-04, VI-05 |
| **UC-MN-01** | View Assigned Maintenance Requests | Maintenance Staff | — | MM-02, MM-05 |
| **UC-MN-02** | Update Maintenance Status & Record Cost | Maintenance Staff | Warden | MM-02, MM-05 |
| **UC-ST-01** | View My Profile & Allocation | Student | — | SM-08, BA-06 |
| **UC-ST-02** | View My Invoices & Payment History | Student | — | FM-06, FM-07 |
| **UC-ST-03** | File Complaint | Student | — | CM-01, CM-02 |
| **UC-ST-04** | Track Complaint Status | Student | — | CM-05 |
| **UC-ST-05** | Submit Maintenance Request | Student | — | MM-01 |
| **UC-RP-01** | Generate Occupancy & Vacancy Reports | Administrator | Warden | RP-01, RP-02 |
| **UC-RP-02** | Generate Fee Dues & Revenue Reports | Administrator | — | RP-03, RP-08 |
| **UC-RP-03** | Generate Student Allocation History | Administrator | Warden | RP-04 |
| **UC-RP-04** | Generate Unresolved Complaints & Maintenance Reports | Administrator | Warden | RP-06, RP-07 |

---

## 2. Detailed Use Case Specifications

Below are detailed operational specifications for core transaction workflows.

### 2.1 UC-WA-02: Allocate Student to Bed

* **Primary Actor**: Warden / Administrator
* **Preconditions**:
  1. Student is registered and active (`status = 'active'`).
  2. Student does not have an existing active allocation.
  3. Target bed is unoccupied (`status = 'available'`) and belongs to an active room.
* **Main Success Scenario**:
  1. Warden selects an unallocated student and browses the visual room grid.
  2. Warden chooses an available bed in an eligible room.
  3. Warden inputs allocation start date (defaults to today).
  4. System executes transactional allocation block:
     a. Checks student active allocation status.
     b. Checks bed availability.
     c. Inserts new `Allocation` record (`status = 'active'`).
     d. Updates target `Bed` state to `occupied`.
     e. Generates `AuditLog` entry.
  5. System returns success message and updates room grid UI.
* **Exception Flows**:
  * **E1: Student already allocated**: Transaction aborts; returns error "Student already has an active allocation (BR-03)."
  * **E2: Bed occupied**: Transaction aborts; returns error "Bed is currently occupied (BR-02)."
  * **E3: Concurrent allocation race**: MySQL UNIQUE index on `active_bed_key` rejects second commit; returns concurrency conflict error (BR-15).

---

### 2.2 UC-WA-03: Initiate & Process Student Transfer

* **Primary Actor**: Warden / Administrator
* **Preconditions**:
  1. Student has an active allocation record.
  2. Target bed is available, active, and differs from current bed.
* **Main Success Scenario**:
  1. Warden selects an allocated student and clicks "Transfer Student".
  2. System displays current allocation details (Hostel, Block, Room, Bed).
  3. Warden selects new target bed and inputs transfer reason.
  4. System executes transactional transfer block:
     a. Updates old `Allocation` record: sets status to `transferred` (auto-clears active generated keys).
     b. Updates old `Bed` state to `available`.
     c. Inserts new `Allocation` record for target bed (`status = 'active'`).
     d. Updates new `Bed` state to `occupied`.
     e. Inserts `Transfer` audit record linking `old_allocation_id` and `new_allocation_id`.
     f. Generates `AuditLog` entry.
  5. System confirms completion and displays transfer receipt summary.
* **Exception Flows**:
  * **E1: Target bed same as current bed**: System blocks submission; returns "Target bed cannot be the same as current bed (BR-10)."
  * **E2: Target bed unavailable**: System blocks transaction; returns "Selected target bed is no longer available."

---

### 2.3 UC-AD-07: Record Fee Payment

* **Primary Actor**: Administrator
* **Preconditions**:
  1. An open invoice exists for the student.
* **Main Success Scenario**:
  1. Admin searches for student invoice by Registration Number or Invoice ID.
  2. System displays total invoice amount, total payments received to date, and current outstanding balance.
  3. Admin inputs payment amount, payment method (Cash, Bank Transfer, Online), receipt number, and payment date.
  4. System executes transactional payment block:
     a. `BEFORE INSERT` trigger on `payments` verifies `amount <= outstanding_balance`.
     b. Inserts `Payment` record.
     c. Updates `Invoice` outstanding balance.
     d. Generates `AuditLog` entry.
  5. System outputs printable payment receipt.
* **Exception Flows**:
  * **E1: Payment exceeds dues**: `BEFORE INSERT` trigger raises error signal; transaction rolls back; system returns "Payment amount exceeds outstanding dues (BR-06)."

---

## 3. Summary of Use Case Coverage

Every business process specified by the college assignment is represented by a formal use case with defined preconditions, success paths, and transactional boundaries. 

Step 1 is complete. We are ready for **Step 2: Requirements ➔ Candidate Entities**.
