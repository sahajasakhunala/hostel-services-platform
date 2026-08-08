# HostelFlow Database Setup & Execution Order

Follow this sequence to initialize the MySQL database schema and programmable objects.

## 1. Schema DDL Execution Order
Execute the SQL files in `database/schema/` in numerical order to prevent foreign key dependency errors:
1. `01_reference.sql`: Initializes campus and calendar reference tables.
2. `02_hostel_structure.sql`: Creates hostels, blocks, floors, rooms, and beds.
3. `03_students.sql`: Creates student profiles and user authentication tables.
4. `04_allocations.sql`: Creates room allocation, transfer, and vacation logs.
5. `05_finance.sql`: Creates fee structures, invoices, and payments.
6. `06_services.sql`: Creates complaints and maintenance request tables.
7. `07_security.sql`: Creates RBAC staff, roles, and user assignment tables.

---

## 2. Views, Procedures & Triggers Initialization
Apply database views, triggers, and stored procedures:
- **Views**: Run scripts in `database/views/` (e.g. `v_current_occupancy.sql`, `v_fee_dues.sql`, etc.).
- **Procedures**: Run scripts in `database/procedures/` (e.g. `sp_allocate_bed.sql`, `sp_process_payment.sql`, etc.).
- **Triggers**: Run scripts in `database/triggers/` (e.g. `allocation_triggers.sql`, `audit_triggers.sql`, `payment_triggers.sql`).

---

## 3. Seed Reference Data
Populate reference and test configuration values:
```bash
mysql -u root -p hostelflow_db < database/seed/01_reference_data.sql
```

---

## 4. Verification Check
Run the internal database verification checks:
```bash
mysql -u root -p hostelflow_db < database/tests/full_database_verification.sql
```
