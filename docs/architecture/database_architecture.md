# HostelFlow Database Architecture Guide

## 1. Relational Schema & Normalization

The HostelFlow database model is built on **26 relational tables**, structured to enforce Referential Integrity and normalized up to **Third Normal Form (3NF)** to eliminate data redundancy and anomalies.

### Core Tables

1. **Campuses**: Reference entry for university campus locations.
2. **Hostels**: Hostel structures tied to campuses, enforcing gender policies.
3. **Blocks**: Distinct building blocks within a hostel.
4. **Floors**: Floor layout mapping within blocks.
5. **Room Types**: Configurable room models (capacity, monthly rent).
6. **Rooms**: Physical rooms referencing floors and room types.
7. **Beds**: Distinct bed units referencing rooms (`is_occupied` state flag).
8. **Students**: Master record of students (registration details, resident status).
9. **Academic Years**: Reference calendar bounds for allocations.
10. **Allocations**: Active/archived resident bed assignments.
11. **Transfers**: Records historical student room transfer parameters.
12. **Vacations**: Records historical student room vacating parameters.
13. **Fee Structures**: Configurable academic billing models.
14. **Invoices**: Outstanding balances generated against residents.
15. **Payments**: Financial transaction receipts settling invoice balances.
16. **Visitors**: Guest traffic log tied to residents.
17. **Complaints**: Grievance reporting and status tracking.
18. **Maintenance Requests**: Facility repair orders with room references.
19. **Audit Logs**: Centralized JSON-based schema audit log target.
20. **Users**: Authentication records containing username and password hash.
21. **Roles**: Available RBAC permission roles (e.g. administrator, warden).
22. **User Roles**: Many-to-many relationship mapping users to roles.
23. **Student Users**: Links user authentication credentials to student profiles.
24. **Staff**: Employee profiles mapped to roles.
25. **Payment Methods**: Allowed options (Cash, Card, UPI, NetBanking).
26. **System Settings**: Application configuration flags stored in DB.

---

## 2. Programmable Objects

### Stored Procedures
- `sp_allocate_bed`: Atomically allocates a bed unit to a student.
- `sp_transfer_student`: Handles transition of a student from one bed to another.
- `sp_vacate_student`: Process departure of a resident, freeing bed occupancy.
- `sp_process_payment`: Atomically records a payment and updates invoice balances.

### Views
- `v_current_occupancy`: Shows all active allocations with resident and room metadata.
- `v_vacant_beds`: Lists currently unassigned bed codes and rooms.
- `v_fee_dues`: Ranks unpaid and partially paid invoices by student.
- `v_allocation_history`: Historical log of resident allocations.
- `v_visitor_report`: Lists active and completed visitor log entries.
- `v_unresolved_complaints`: Filters pending grievances.
- `v_maintenance_status`: Highlights pending facility repairs.

### Triggers
- `trg_allocations_prevent_double_booking`: Prevents allocating occupied beds.
- `trg_payments_update_invoice`: Automatically subtracts payment amount from invoice outstanding balances.
- `trg_allocations_after_insert_audit`: Logs allocation creation.
- `trg_allocations_after_update_audit`: Logs allocation updates.
- `trg_payments_after_insert_audit`: Logs payment transactions.
- `trg_transfers_after_insert_audit`: Logs room transfers.

---

## 3. Indexing & Optimization Strategy

The following query-covering composite indexes are maintained for performance optimization:
- `idx_invoices_outstanding_due`: Indexes outstanding balance, due dates, and student IDs to accelerate debtor reports.
- `idx_allocations_status_bed_student`: Accelerates resident occupancy views.
- `idx_visitors_checkout_checkin`: Optimizes visitor gate logs.
- `idx_complaints_status_filed`: Indexes grievance reports.
- `idx_maint_reported_status`: Indexes maintenance queues by report date and status.
