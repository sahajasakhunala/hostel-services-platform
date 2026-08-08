# HostelFlow — Actor Use Cases

**Document ID**: HOSTEL-UC-001  
**Version**: 1.0  
**Status**: Draft  

This document details the functional workflows supported by HostelFlow, organized by Actor. These use cases define the business processes that must be mapped to database state transitions.

---

## 1. Administrator Use Cases

```mermaid
usecaseDiagram
    actor Admin
    Admin --> (Register Student)
    Admin --> (Deactivate Student)
    Admin --> (Create Physical Asset)
    Admin --> (Allocate Bed)
    Admin --> (Approve Transfer)
    Admin --> (Process Vacating)
    Admin --> (Define Fee Structure)
    Admin --> (Generate Invoice)
    Admin --> (Record Payment)
```

### UC-AD-01: Register Student
* **Primary Actor**: Administrator
* **Preconditions**: Student has been admitted to the university.
* **Flow**:
  1. Admin enters student demographics (reg number, name, DOB, gender, email, phone, address).
  2. Admin selects academic details (department, course, academic year).
  3. Admin enters optional guardian details (relationship, contact numbers).
  4. System validates registration number uniqueness and field formats.
  5. System persists records to database.

### UC-AD-02: Manage Physical Infrastructure
* **Primary Actor**: Administrator
* **Flow**:
  1. Admin defines Hostels, Blocks, Floors, Rooms, and Room Types.
  2. Admin adds Beds to Rooms.
  3. System triggers verify bed count does not exceed room capacity.

### UC-AD-03: Manage Fee Structures & Invoicing
* **Primary Actor**: Administrator
* **Flow**:
  1. Admin defines fee schedules per Room Type per Academic Year.
  2. Admin triggers invoice generation for an active student allocation.
  3. System calculates due amount and creates invoice record.

### UC-AD-04: Record Student Payment
* **Primary Actor**: Administrator
* **Flow**:
  1. Admin inputs payment details against student invoice (amount, method, receipt number).
  2. System triggers verify payment amount ≤ outstanding dues.
  3. System updates invoice outstanding balance and records transaction.

---

## 2. Warden Use Cases

```mermaid
usecaseDiagram
    actor Warden
    Warden --> (View Room Status Grid)
    Warden --> (Initiate Transfer Request)
    Warden --> (Review Branch Complaints)
    Warden --> (Prioritize Maintenance)
```

### UC-WA-01: View Room Status Grid
* **Primary Actor**: Warden
* **Flow**:
  1. Warden requests structural grid view for their assigned Hostel/Block.
  2. System queries active allocations and returns color-coded layout (occupied/available) of all rooms and beds.

### UC-WA-02: Initiate Student Transfer
* **Primary Actor**: Warden
* **Preconditions**: Student has an active allocation.
* **Flow**:
  1. Warden selects student and target bed.
  2. System checks target bed availability.
  3. System closes current allocation and starts new allocation within a transaction block.

---

## 3. Security Staff Use Cases

```mermaid
usecaseDiagram
    actor Security
    Security --> (Log Visitor Check-In)
    Security --> (Log Visitor Check-Out)
    Security --> (Search Visitor History)
```

### UC-SE-01: Log Visitor Check-In
* **Primary Actor**: Security Staff
* **Flow**:
  1. Security records visitor identification, purpose, and targeted student.
  2. System validates student active status.
  3. System records entry timestamp.

### UC-SE-02: Log Visitor Check-Out
* **Primary Actor**: Security Staff
* **Flow**:
  1. Security checks out visitor from active visitor log.
  2. System records departure timestamp.
  3. System checks that checkout time ≥ check-in time.

---

## 4. Maintenance Staff Use Cases

```mermaid
usecaseDiagram
    actor Maintenance
    Maintenance --> (View Assigned Tasks)
    Maintenance --> (Update Request Status)
    Maintenance --> (Log Maintenance Cost)
```

### UC-MN-01: Resolve Maintenance Request
* **Primary Actor**: Maintenance Staff
* **Flow**:
  1. Staff views assigned plumbing, electrical, or structural tasks.
  2. Staff updates status (Pending ➔ In-Progress ➔ Completed).
  3. Upon completion, staff inputs material/labor cost and resolution comments.

---

## 5. Student Use Cases

```mermaid
usecaseDiagram
    actor Student
    Student --> (View Stay Profile)
    Student --> (File Complaint)
    Student --> (File Maintenance Request)
    Student --> (Track Dues)
```

### UC-ST-01: File Complaint
* **Primary Actor**: Student
* **Flow**:
  1. Student enters complaint details, selects category and priority level.
  2. System logs complaint under student ID with status 'Open'.

### UC-ST-02: File Maintenance Request
* **Primary Actor**: Student
* **Flow**:
  1. Student requests repair for their room/equipment.
  2. System creates maintenance record linked to student's room.
