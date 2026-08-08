# HostelFlow — Conceptual ER Diagram

**Document ID**: HOSTEL-ERD-001  
**Version**: 1.0  
**Status**: Draft  

This document contains the conceptual entity-relationship diagram for HostelFlow using Mermaid.js syntax.

---

## 1. ER Diagram

```mermaid
erDiagram
    HOSTELS ||--|{ BLOCKS : contains
    BLOCKS ||--|{ FLOORS : has
    FLOORS ||--|{ ROOMS : has
    ROOM_TYPES ||--|{ ROOMS : defines
    ROOMS ||--|{ BEDS : contains
    
    DEPARTMENTS ||--|{ COURSES : offers
    COURSES ||--|{ STUDENTS : enrolls
    STUDENTS ||--|{ GUARDIANS : emergency_contact
    
    STUDENTS ||--o{ ALLOCATIONS : receives
    BEDS ||--o{ ALLOCATIONS : assigned_to
    
    ALLOCATIONS ||--o| VACATING_RECORDS : ends_with
    ALLOCATIONS ||--o{ TRANSFERS : "old_alloc"
    ALLOCATIONS ||--o{ TRANSFERS : "new_alloc"
    
    STUDENTS ||--o{ INVOICES : billed_to
    FEE_STRUCTURES ||--|{ INVOICES : calculates
    ROOM_TYPES ||--o{ FEE_STRUCTURES : schedules
    ACADEMIC_YEARS ||--o{ FEE_STRUCTURES : applies_to
    INVOICES ||--o{ PAYMENTS : resolves
    
    STUDENTS ||--o{ VISITORS : hosts
    STUDENTS ||--o{ COMPLAINTS : files
    COMPLAINT_CATEGORIES ||--|{ COMPLAINTS : categorizes
    
    ROOMS ||--o{ MAINTENANCE_REQUESTS : reports
    MAINTENANCE_STAFF ||--o{ MAINTENANCE_REQUESTS : resolves
    
    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : holds
    USERS ||--o| STUDENTS : links
```

---

## 2. Key Cardinality Definitions

* **Hostel structural hierarchy** is strictly one-to-many from Hostels ➔ Blocks ➔ Floors ➔ Rooms ➔ Beds. This hierarchy guarantees that traversing downward from a Bed uniquely identifies its exact room, floor, block, and hostel.
* **Allocations** represents a junction entity mapping the many-to-many relationship between Students and Beds over time, resolving historical residency tracking.
* **Transfers** links two allocation records (old and new) for a single student movement, representing a self-referencing style association resolved through foreign keys.
* **Invoices** are calculated based on the room type fee structure and are associated with a single student, while allowing multiple payment transactions.
