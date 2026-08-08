# HostelOS — Requirements Specification

**Document ID**: HOSTEL-REQ-001  
**Version**: 1.0  
**Status**: Draft — Pending Review  

---

## 1. Problem Statement

University hostels manage a complex web of physical assets (buildings, blocks, floors, rooms, beds), people (students, guardians, staff, visitors), processes (allocation, transfer, vacating, payments), and incidents (complaints, maintenance). When these operations are handled manually or through disconnected systems, several failure modes emerge:

| Problem | Consequence |
|---|---|
| Manual bed allocation | Room capacity exceeded; duplicate bed assignments |
| Paper-based visitor logs | Untraceable visitor history; security gaps |
| Spreadsheet fee tracking | Payment discrepancies; outstanding dues undetected |
| Verbal complaint reporting | Complaints lost; no resolution tracking; no accountability |
| Ad-hoc maintenance requests | Requests forgotten; no assignment or completion tracking |
| No historical records | Transfer history lost; allocation patterns invisible |
| No access control | Unauthorized changes to allocation, fees, or records |

**HostelOS addresses this** by providing a centralized, database-backed platform where every operation is recorded, validated, constrained, and auditable — with the database itself enforcing critical integrity rules independently of the application layer.

---

## 2. System Scope

### 2.1 In Scope

HostelOS manages hostel accommodation and student services for **a single university campus containing multiple hostel buildings**.

| Domain | What's Covered |
|---|---|
| **Physical Infrastructure** | Hostels, blocks, floors, rooms (with types and capacities), beds |
| **Student Records** | Student registration, academic details, guardian/emergency contacts |
| **Bed Allocation** | Student-to-bed assignment with eligibility checks and capacity enforcement |
| **Transfers** | Moving a student from one bed to another with historical tracking |
| **Vacating** | Formal check-out with reason, clearance status, deposit return |
| **Financial Management** | Fee structures, invoice generation, payment recording, outstanding dues |
| **Visitor Management** | Visitor check-in/check-out, purpose, ID verification, student visited |
| **Complaint System** | Filing, categorizing, prioritizing, assigning, tracking, resolving complaints |
| **Maintenance** | Room/equipment repair requests, staff assignment, status tracking, cost |
| **Authentication & Authorization** | Role-based login for Admin, Warden, Security, Maintenance Staff, Student |
| **Audit Trail** | Logging of critical operations (who, what, when, old value, new value) |
| **Reporting** | Occupancy, vacancies, fee dues, allocation history, visitors, complaints, maintenance |

### 2.2 Out of Scope (Explicit Exclusions)

These are deliberately excluded to maintain focus and avoid scope creep:

| Exclusion | Rationale |
|---|---|
| Multi-campus / multi-university support | Our scope is one campus with multiple hostels |
| Academic management (courses, grades, attendance) | We store department/course as reference data only; academic workflows belong to a separate system |
| Mess/canteen management | Different operational domain |
| Laundry services | Out of hostel accommodation scope |
| Transport/bus management | Different operational domain |
| Student admission/enrollment | We register students who have already been admitted |
| Email/SMS notifications | Stretch goal, not core requirement |
| Mobile application | Web-based only for this version |
| Cloud deployment | Local-first; cloud is a stretch goal |
| Biometric/facial recognition | Out of scope |
| Inventory management (furniture, appliances) | Maintenance covers repair requests, not asset tracking |

---

## 3. System Objectives

| # | Objective |
|---|---|
| O1 | Provide a normalized (3NF) relational database that accurately models the hostel domain |
| O2 | Enforce data integrity through database-level constraints, triggers, and generated columns — not just application logic |
| O3 | Implement a transaction-safe bed allocation engine that prevents double-booking, capacity violations, and invalid states |
| O4 | Support role-based access control so that each user type sees only what they're authorized to see and do |
| O5 | Track the complete lifecycle of a hostel stay: registration → allocation → (optional transfer) → vacating |
| O6 | Manage financial records: fee structures, invoices, payments, and outstanding dues |
| O7 | Provide visitor logging, complaint tracking, and maintenance request management |
| O8 | Generate meaningful reports: occupancy rates, vacancies, fee dues, allocation history, visitor logs, unresolved complaints, and maintenance status |
| O9 | Maintain an audit trail of all critical operations for accountability and traceability |
| O10 | Demonstrate professional software engineering practices: clean architecture, version control, testing, and documentation |

---

## 4. Stakeholders

| Stakeholder | Interest |
|---|---|
| **University Administration** | Overall hostel management oversight, policy enforcement, financial reporting |
| **Hostel Warden** | Day-to-day operations of assigned hostel/block; student welfare |
| **Security Staff** | Visitor control, access monitoring |
| **Maintenance Staff** | Repair and upkeep of hostel infrastructure |
| **Students** | Accommodation, fee payments, complaint filing, visitor hosting |
| **Parents/Guardians** | Emergency contact information; indirect stakeholders |
| **Examiners** (meta) | Evaluating database design, SQL proficiency, application quality |

---

## 5. Actors and Responsibilities

### 5.1 Administrator

The system administrator has full access to all modules and is responsible for system-wide configuration and management.

| Responsibility | Description |
|---|---|
| Hostel management | Create and manage hostels, blocks, floors, rooms, room types, beds |
| Student management | Register students, update records, deactivate accounts |
| Allocation management | Allocate beds, approve transfers, process vacating |
| Fee management | Define fee structures, generate invoices, record payments |
| User management | Create staff accounts, assign roles |
| Reporting | Access all system reports |
| System configuration | Manage complaint categories, academic years, reference data |

### 5.2 Warden

A warden is assigned to one or more hostels/blocks and manages day-to-day operations within their jurisdiction.

| Responsibility | Description |
|---|---|
| Student oversight | View students in their hostel/block |
| Allocation | Allocate beds, initiate transfers within their hostel |
| Complaints | View, assign, and resolve complaints for their hostel |
| Maintenance | View and prioritize maintenance requests for their hostel |
| Visitors | Monitor visitor logs for their hostel |
| Reports | Access hostel-specific occupancy, complaint, and maintenance reports |

### 5.3 Security Staff

Manages visitor entry and exit at the hostel gate.

| Responsibility | Description |
|---|---|
| Visitor check-in | Record visitor details, purpose, ID, student being visited |
| Visitor check-out | Record departure time |
| Visitor search | Look up visitor history |

### 5.4 Maintenance Staff

Handles maintenance requests assigned to them.

| Responsibility | Description |
|---|---|
| View assignments | See maintenance requests assigned to them |
| Update status | Mark requests as in-progress, completed |
| Record cost | Log material/labor cost for completed work |

### 5.5 Student

A registered student with an active or past hostel allocation.

| Responsibility | Description |
|---|---|
| View profile | See their own registration details, allocation, fee status |
| View allocation | See current bed assignment, room details, hostel |
| View fees | See invoices, payments made, outstanding balance |
| File complaint | Submit a complaint with category, description, priority |
| Track complaints | View status of their filed complaints |
| View notices | See hostel announcements |
| Request maintenance | Submit a maintenance request for their room |

---

## 6. Functional Requirements

### 6.1 Module: Student Management (SM)

| ID | Requirement | Priority |
|---|---|---|
| SM-01 | The system shall allow administrators to register a new student with: registration number, name, date of birth, gender, email, phone, address, department, course, academic year, admission date, status, and optional photo path and medical notes | Must |
| SM-02 | Each student shall have a unique registration number | Must |
| SM-03 | The system shall allow storing one or more guardian/parent contacts per student with: name, relationship, phone, email, address | Must |
| SM-04 | The system shall allow administrators to search students by registration number, name, department, or course | Must |
| SM-05 | The system shall allow administrators to update student details | Must |
| SM-06 | The system shall allow administrators to deactivate a student record (soft delete) | Must |
| SM-07 | The system shall not allow deletion of students who have active allocations or outstanding dues | Must |
| SM-08 | The system shall display a student's complete profile including guardian details, current allocation, fee status, and complaint history | Should |

### 6.2 Module: Bed Allocation (BA)

| ID | Requirement | Priority |
|---|---|---|
| BA-01 | The system shall allow authorized users to allocate a student to a specific bed | Must |
| BA-02 | Before allocation, the system shall verify: (a) student exists and is active, (b) student has no current active allocation, (c) bed exists and belongs to an active room, (d) bed is currently unoccupied | Must |
| BA-03 | Each bed shall have at most one active allocation at any time | Must |
| BA-04 | Each student shall have at most one active allocation at any time | Must |
| BA-05 | The number of beds in a room shall not exceed the room's defined capacity | Must |
| BA-06 | Allocation shall record: student, bed, start date, end date (initially NULL), and status | Must |
| BA-07 | The allocation operation shall be transaction-safe: either all changes succeed (allocation record + bed status update + audit log) or none do | Must |
| BA-08 | The allocation end date, if set, must not precede the start date | Must |
| BA-09 | The system shall provide a visual room grid showing bed occupancy status (available/occupied) | Should |
| BA-10 | The system shall prevent allocation even when accessed directly through the database (not through the application) | Must |

### 6.3 Module: Transfers (TR)

| ID | Requirement | Priority |
|---|---|---|
| TR-01 | The system shall allow authorized users to transfer a student from their current bed to a different bed | Must |
| TR-02 | Transfer shall: close the old allocation, create a new allocation, update both bed statuses, and record the causal link between old and new allocations | Must |
| TR-03 | A transfer shall not be allowed to the student's current bed | Must |
| TR-04 | The target bed must satisfy the same availability checks as a new allocation (BA-02 c, d) | Must |
| TR-05 | Transfer shall record: old allocation, new allocation, transfer date, reason | Must |
| TR-06 | The entire transfer operation shall be transaction-safe | Must |

### 6.4 Module: Vacating (VA)

| ID | Requirement | Priority |
|---|---|---|
| VA-01 | The system shall allow authorized users to formally vacate a student from their allocated bed | Must |
| VA-02 | Vacating shall: close the active allocation, update bed status to available, and create a vacating record | Must |
| VA-03 | The vacating date must not precede the allocation start date | Must |
| VA-04 | Vacating record shall capture: allocation reference, vacating date, reason (graduation, transfer to another hostel, disciplinary, personal, other), clearance status, deposit refund status, and remarks | Must |
| VA-05 | The vacating operation shall be transaction-safe | Must |

### 6.5 Module: Financial Management (FM)

| ID | Requirement | Priority |
|---|---|---|
| FM-01 | The system shall maintain fee structures defining the amount per room type per academic year | Must |
| FM-02 | The system shall allow administrators to generate invoices for students based on their allocation and applicable fee structure | Must |
| FM-03 | The system shall allow recording payments against an invoice with: amount, payment date, payment method, receipt number, remarks | Must |
| FM-04 | A payment amount shall not exceed the outstanding balance on the invoice | Must |
| FM-05 | Multiple partial payments shall be allowed against a single invoice | Must |
| FM-06 | The system shall calculate outstanding dues as: invoice amount − sum of payments | Must |
| FM-07 | The system shall provide a fee dues report showing students with outstanding balances | Must |
| FM-08 | The system shall provide a revenue summary report by period | Should |

### 6.6 Module: Visitor Management (VI)

| ID | Requirement | Priority |
|---|---|---|
| VI-01 | The system shall allow security staff to record visitor check-in with: visitor name, phone, ID type, ID number, purpose, student being visited, check-in time | Must |
| VI-02 | The system shall allow recording visitor check-out with: check-out time | Must |
| VI-03 | Check-out time must not precede check-in time | Must |
| VI-04 | The system shall provide a view of today's visitors (checked-in and checked-out) | Must |
| VI-05 | The system shall allow searching visitor history by visitor name, student visited, or date range | Should |

### 6.7 Module: Complaint Management (CM)

| ID | Requirement | Priority |
|---|---|---|
| CM-01 | The system shall allow students to file complaints with: category (from predefined list), subject, description, priority (low/medium/high/urgent) | Must |
| CM-02 | Complaint categories shall be maintained as a reference table (e.g., Noise, Hygiene, Bullying, Infrastructure, Electrical, Plumbing, Other) | Must |
| CM-03 | Each complaint shall track: status (open, in-progress, resolved, closed), assigned staff, resolution notes, filed date, resolved date | Must |
| CM-04 | A complaint shall not be marked as resolved without resolution notes | Must |
| CM-05 | Students shall be able to view the status of their own complaints | Must |
| CM-06 | Wardens/admins shall be able to view, assign, and resolve complaints in their jurisdiction | Must |
| CM-07 | The system shall provide an unresolved complaints report with aging information | Must |

### 6.8 Module: Maintenance Management (MM)

| ID | Requirement | Priority |
|---|---|---|
| MM-01 | The system shall allow submitting maintenance requests with: room, description, category (electrical, plumbing, furniture, civil, cleaning, other), priority | Must |
| MM-02 | Each request shall track: status (pending, assigned, in-progress, completed), assigned staff member, reported date, completed date, cost | Must |
| MM-03 | Authorized users shall be able to assign requests to maintenance staff | Must |
| MM-04 | The system shall provide a maintenance status report showing pending, in-progress, and completed requests | Must |
| MM-05 | Maintenance staff shall be able to update the status of requests assigned to them | Must |

### 6.9 Module: Administration & Security (AS)

| ID | Requirement | Priority |
|---|---|---|
| AS-01 | The system shall support user registration with: username, password (hashed), linked person (student or staff) | Must |
| AS-02 | The system shall support role-based access: Administrator, Warden, Security, Maintenance, Student | Must |
| AS-03 | A user may have multiple roles | Should |
| AS-04 | Each route/action shall check the user's role before granting access | Must |
| AS-05 | Unauthorized access attempts shall be rejected with an appropriate error (403) | Must |
| AS-06 | The system shall maintain audit logs for critical operations: allocations, transfers, vacating, payments, complaint status changes | Must |
| AS-07 | Audit logs shall record: action type, table affected, record ID, old value (where applicable), new value, user who performed the action, timestamp | Must |
| AS-08 | Passwords shall be stored using bcrypt hashing, never in plaintext | Must |

### 6.10 Module: Reporting (RP)

| ID | Requirement | Priority |
|---|---|---|
| RP-01 | **Occupancy Report**: Current occupancy by hostel, block, floor — showing total beds, occupied, available, and percentage | Must |
| RP-02 | **Vacancy Report**: List of all currently available beds with full location details (hostel → block → floor → room → bed) | Must |
| RP-03 | **Fee Dues Report**: Students with outstanding balances, sorted by amount, filterable by hostel/department | Must |
| RP-04 | **Allocation History Report**: Complete allocation history for a student, including transfers and vacating | Must |
| RP-05 | **Visitor Report**: Visitor log filterable by date range, student, or hostel | Must |
| RP-06 | **Unresolved Complaints Report**: Open complaints with age (days since filed), priority, category, and assignment status | Must |
| RP-07 | **Maintenance Status Report**: Pending, in-progress, and completed requests with aging and cost data | Must |
| RP-08 | **Revenue Summary**: Total payments received by period (monthly/yearly), by hostel, by payment method | Should |

---

## 7. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NF-01 | The database shall be designed in Third Normal Form (3NF) with documented functional dependencies | Design |
| NF-02 | Critical business rules shall be enforced at the database level (constraints, triggers, generated columns), not only in the application | Integrity |
| NF-03 | All allocation, transfer, vacating, and payment operations shall use database transactions with proper COMMIT/ROLLBACK | Reliability |
| NF-04 | Frequently searched attributes (registration number, room number, allocation status, complaint status, payment date) shall be indexed | Performance |
| NF-05 | The application shall validate all user input on the server side before processing | Security |
| NF-06 | The application shall provide meaningful error messages for all rejection scenarios | Usability |
| NF-07 | The application shall work entirely on localhost without requiring internet connectivity | Deployment |
| NF-08 | Fonts shall be bundled locally, not loaded from external CDNs | Deployment |
| NF-09 | The system shall handle concurrent access safely — two simultaneous allocation attempts for the same bed shall result in exactly one success and one failure | Concurrency |
| NF-10 | The codebase shall follow a layered architecture: routes → services → repositories → database | Architecture |
| NF-11 | The project shall maintain a professional Git history with conventional commits and meaningful branches | Engineering |

---

## 8. Business Rules

| # | Rule | Enforcement Layer |
|---|---|---|
| BR-01 | Each student has a unique registration number | Database: `UNIQUE` constraint |
| BR-02 | Each bed can have at most one active allocation | Database: `UNIQUE` on generated column `active_bed_key` |
| BR-03 | Each student can have at most one active allocation | Database: `UNIQUE` on generated column `active_student_key` |
| BR-04 | The number of beds in a room must not exceed the room's capacity | Database: `BEFORE INSERT` trigger on `beds` |
| BR-05 | Allocation end date must not precede start date | Database: `CHECK` constraint |
| BR-06 | Payment amount must not exceed outstanding invoice balance | Database: `BEFORE INSERT` trigger on `payments` |
| BR-07 | Visitor check-out time must not precede check-in time | Database: `CHECK` constraint |
| BR-08 | A complaint cannot be marked resolved without resolution notes | Database: `BEFORE UPDATE` trigger on `complaints` |
| BR-09 | Vacating date must not precede the allocation's start date | Database: `BEFORE INSERT` trigger on `vacating_records` + Application validation |
| BR-10 | A transfer must be to a different bed than the student's current bed | Application: service validation + Database: `CHECK` if feasible |
| BR-11 | Only active students can be allocated a bed | Application: service validation |
| BR-12 | A student with an active allocation cannot be deactivated | Application: service validation |
| BR-13 | A student with outstanding dues cannot be deactivated | Application: service validation |
| BR-14 | All allocation/transfer/vacate operations must be atomic (transaction-safe) | Application: service layer uses `BEGIN`/`COMMIT`/`ROLLBACK` |
| BR-15 | Concurrent allocation requests for the same bed must be handled safely | Database: `UNIQUE` constraint + transaction isolation |
| BR-16 | Concurrent payment requests must not allow total payments to exceed invoice amount | Database: trigger + appropriate locking strategy (e.g., `SELECT ... FOR UPDATE`) |
| BR-17 | Passwords must never be stored in plaintext | Application: bcrypt hashing |
| BR-18 | All critical operations must be audit-logged | Database: `AFTER INSERT/UPDATE/DELETE` triggers on key tables |

---

## 9. System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                        HostelOS                              │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │   Student    │  │  Allocation  │  │    Financial     │    │
│  │  Management  │  │   Engine     │  │    Management    │    │
│  └─────────────┘  └──────────────┘  └──────────────────┘    │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │   Visitor    │  │  Complaint   │  │   Maintenance    │    │
│  │  Management  │  │   Tracker    │  │    Management    │    │
│  └─────────────┘  └──────────────┘  └──────────────────┘    │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │    Auth &    │  │   Audit      │  │    Reporting     │    │
│  │    Roles     │  │   Trail      │  │    Engine        │    │
│  └─────────────┘  └──────────────┘  └──────────────────┘    │
│                                                              │
│                        MySQL 9.7.1                           │
└─────────────────────────────────────────────────────────────┘
         │                                      │
         │                                      │
    ┌────▼────────┐                    ┌────────▼────────┐
    │ University  │                    │   External      │
    │ Admission   │                    │   Systems       │
    │ System      │                    │   (NOT          │
    │ (NOT        │                    │   integrated)   │
    │ integrated) │                    │                 │
    └─────────────┘                    └─────────────────┘
```

HostelOS is a **self-contained** system. Students are registered manually — the system does not integrate with any external admission, academic, or financial system.

---

## 10. Assumptions

| # | Assumption |
|---|---|
| A1 | The university has already admitted the student before they are registered in HostelOS |
| A2 | Each hostel building has a clearly defined block/floor/room structure |
| A3 | Room capacity is fixed and determined by the physical infrastructure |
| A4 | Fee structures are defined per room type per academic year and do not change mid-year |
| A5 | One bed always represents one physical sleeping position |
| A6 | The system operates on a single server/machine (local deployment) |
| A7 | Users have access to a modern web browser (Chrome, Firefox, Edge) |
| A8 | The administrator is responsible for initial system setup: creating hostels, blocks, floors, rooms, beds, fee structures, and staff accounts |
| A9 | Visitors are external to the hostel and visit registered students |
| A10 | Maintenance staff are pre-registered in the system by the administrator |

---

## 11. Terminology Glossary

Precise definitions to avoid ambiguity during design and development:

| Term | Definition |
|---|---|
| **Hostel** | A residential building within the university campus that provides student accommodation |
| **Block** | A named subdivision of a hostel (e.g., Block A, North Wing). A hostel has one or more blocks |
| **Floor** | A physical level within a block (e.g., Ground Floor, First Floor). A block has one or more floors |
| **Room** | A physical space on a floor that contains one or more beds. Has a defined type and capacity |
| **Room Type** | A classification of rooms by size/configuration: Single (1 bed), Double (2 beds), Triple (3 beds), Dormitory (4+ beds) |
| **Bed** | The atomic allocatable unit. A single sleeping position within a room. One bed can be occupied by at most one student at a time |
| **Student** | A person admitted to the university and registered in HostelOS for hostel accommodation. Has a unique registration number |
| **Guardian** | A parent or emergency contact associated with a student |
| **Department** | An academic department (e.g., Computer Science, Electronics). Stored as reference data |
| **Course** | An academic program (e.g., B.Tech CSE, MBA, M.Sc Physics). NOT individual subjects |
| **Academic Year** | A defined time period (e.g., 2025–2026) used for fee structures and reporting |
| **Allocation** | The assignment of a specific student to a specific bed for a specific period. The core transactional entity |
| **Active Allocation** | An allocation with status = 'active'. A student can have at most one. A bed can have at most one |
| **Transfer** | The process of moving a student from one bed to another, closing the old allocation and creating a new one, with a recorded causal link |
| **Vacating** | The formal process of a student leaving their allocated bed, with recorded reason and clearance status |
| **Fee Structure** | The defined accommodation fee amount per room type per academic year |
| **Invoice** | A generated bill for a student for a specific period, based on their allocation and applicable fee structure |
| **Payment** | A financial transaction recording money received against an invoice |
| **Outstanding Dues** | Invoice amount minus the sum of all payments made against that invoice |
| **Visitor** | An external person visiting a registered student at the hostel |
| **Complaint** | A formal grievance filed by a student regarding hostel conditions |
| **Complaint Category** | A predefined classification for complaints (e.g., Noise, Hygiene, Infrastructure) |
| **Maintenance Request** | A formal request for repair or upkeep of hostel infrastructure or equipment |
| **User** | A person with login credentials in HostelOS. May be a student, warden, security guard, maintenance worker, or administrator |
| **Role** | A named set of permissions (Admin, Warden, Security, Maintenance, Student) |
| **Audit Log** | A record of a critical system action: who performed it, what changed, when, and what the old/new values were |
| **Capacity** | The maximum number of beds a room can physically hold. The number of beds in a room must never exceed this value |
| **Transaction-Safe** | An operation where multiple database changes either all succeed together or all fail together, leaving the database in a consistent state |

---

## 12. Requirement Traceability — College Deliverables

This section maps our requirements to the college's specific deliverables to ensure nothing is missed:

### Review 1 Deliverables

| College Requirement | HostelOS Coverage |
|---|---|
| Problem identification, scope, objectives | Sections 1, 2, 3 of this document |
| Users and functional requirements | Sections 5, 6 of this document |
| Conceptual design / ER diagram | Phase 2 deliverable: `docs/04-er-diagram/` |
| Initial relational schema with PKs and relationships | Phase 3 deliverable: `docs/05-relational-schema/` |

### Review 2 Deliverables

| College Requirement | HostelOS Coverage |
|---|---|
| Normalized database design up to 3NF | Phase 3: `docs/06-normalization/`, `docs/07-functional-dependencies/` |
| Data dictionary | Phase 3: `docs/08-data-dictionary/` |
| DDL scripts with integrity constraints | Phase 4: `database/schema/`, `database/constraints/`, `database/triggers/` |
| Sample data | Phase 5: `database/seed/` |
| SQL queries (joins, subqueries, aggregation, views) | Phase 5: `database/queries/`, `database/views/` |
| Reports (occupancy, vacancies, fee dues, etc.) | Phase 5: `database/queries/reports.sql` |

### Review 3 Deliverables

| College Requirement | HostelOS Coverage |
|---|---|
| Application connected to database | Phase 6–7: Flask application |
| Student registration, bed allocation, transfer | Modules SM, BA, TR |
| Fee collection | Module FM |
| Visitor entry | Module VI |
| Complaint tracking | Module CM |
| Maintenance | Module MM |
| Vacancy reporting | Module RP |
| CRUD operations, search, validation, reports, error handling | All modules |
| Source code, database script, test data, screenshots, report | Phase 8–10 deliverables |
