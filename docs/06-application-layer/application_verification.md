# HostelFlow Phase 6 — Application Layer & RBAC Verification Report
**Document Identifier**: HOSTEL-DOC-006  
**Target Application**: HostelFlow Platform v1.0.0  
**Repository Branch**: `develop`  
**Database Backend**: MySQL 9.7.1+ (`hostelflow_db`)  

---

## 1. Executive Summary

Phase 6 turns the Phase 4 database schema, triggers, and stored procedures, and Phase 5 analytical SQL reports into a complete end-to-end web application platform. The application is built using **Flask (Application Factory Pattern)**, **PyMySQL** (explicit raw SQL / stored procedure execution, strictly avoiding ORM overhead), **Werkzeug Password Hashing**, **Flask Server-Side Session Authentication**, **Role-Based Access Control (RBAC)**, and a **Vanilla CSS / JavaScript Single-Page Management Interface**.

---

## 2. Multi-Layer Application Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
│ Jinja2 HTML5 Templates / HSL Design Tokens / Vanilla JS │
└────────────────────────────┬────────────────────────────┘
                             │ REST API Fetch Requests (/api/*)
┌────────────────────────────▼────────────────────────────┐
│                    APPLICATION LAYER                    │
│  Flask Blueprints / Session Auth / RBAC @role_required  │
└────────────────────────────┬────────────────────────────┘
                             │ Python DTOs & Validation
┌────────────────────────────▼────────────────────────────┐
│                      SERVICE LAYER                      │
│   Business Logic Rules & Stored Procedure Output Parsing│
└────────────────────────────┬────────────────────────────┘
                             │ Direct Method Calls
┌────────────────────────────▼────────────────────────────┐
│                    REPOSITORY LAYER                     │
│  PyMySQL DictCursor Context Managers (get_db_cursor)    │
└────────────────────────────┬────────────────────────────┘
                             │ CALL sp_* / SELECT FROM v_*
┌────────────────────────────▼────────────────────────────┐
│                     DATABASE LAYER                      │
│ MySQL 9.7.1 (Constraints, FOR UPDATE Triggers, Views)   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Role-Based Access Control (RBAC) Security Matrix

| User Role | Students | Allocations | Finance | Visitors | Complaints | Maintenance | Reports |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Administrator** | Full Access | Full Access | Full Access | Full Access | Full Access | Full Access | Full Access |
| **Warden (Hostel Manager)** | Full Access | Full Access | Read Dues | Read Logs | Status Update | Status Update | Full Access |
| **Finance Staff** | — | — | Full Access | — | — | — | Fee Reports |
| **Gate Security Staff** | — | — | — | Check-In/Out | — | — | — |
| **Maintenance Staff** | — | — | — | — | — | Repair Updates | — |
| **Resident Student** | Own Profile | Own Bed | Own Invoices | — | File/View Own | — | — |

* **401 Unauthorized**: Returned when an unauthenticated request attempts access to protected `/api/*` endpoints.
* **403 Forbidden**: Returned when an authenticated user lacks the required role or attempts unauthorized access to another student's financial/allocation records.

---

## 4. API Endpoints Specification

### Authentication (`/api/auth`)
* `POST /api/auth/login`: Authenticates credentials & starts session
* `POST /api/auth/logout`: Clears session
* `GET /api/auth/me`: Retrieves current session profile & roles

### Student Directory (`/api/students`)
* `GET /api/students`: Lists registered students
* `GET /api/students/<id>`: Retrieves student details
* `POST /api/students`: Registers a new resident student

### Bed Allocation Lifecycle (`/api/allocations`)
* `GET /api/allocations`: Lists active allocations from `v_current_occupancy`
* `GET /api/allocations/student/<id>`: Active allocation for student
* `GET /api/allocations/history/<id>`: Stay timeline from `v_allocation_history`
* `POST /api/allocations`: Allocates bed via `sp_allocate_bed`
* `POST /api/allocations/transfer`: Transfers student via `sp_transfer_student`
* `POST /api/allocations/vacate`: Vacates student via `sp_vacate_student`

### Finance & Billing (`/api/finance`)
* `GET /api/finance/dues`: Outstanding fee dues from `v_fee_dues`
* `GET /api/finance/invoices/<id>`: Invoice details
* `GET /api/finance/students/<id>/invoices`: All invoices for student
* `GET /api/finance/students/<id>/payments`: Payment ledger for student
* `POST /api/finance/payments`: Processes payment via `sp_process_payment`

### Gate Security Visitors (`/api/visitors`)
* `GET /api/visitors`: Visitor log from `v_visitor_report`
* `GET /api/visitors/active`: Currently checked-in visitors
* `POST /api/visitors`: Gate security check-in
* `POST /api/visitors/<id>/checkout`: Gate security check-out

### Grievances & Complaints (`/api/complaints`)
* `GET /api/complaints`: List complaints
* `GET /api/complaints/unresolved`: Unresolved complaints from `v_unresolved_complaints`
* `POST /api/complaints`: File new complaint
* `PATCH /api/complaints/<id>/status`: Update complaint status & resolution notes

### Facility Maintenance (`/api/maintenance`)
* `GET /api/maintenance`: List repair requests
* `GET /api/maintenance/pending`: Incomplete repair requests from `v_maintenance_status`
* `POST /api/maintenance`: Create repair request
* `PATCH /api/maintenance/<id>/assign`: Assign repair staff
* `PATCH /api/maintenance/<id>/status`: Update repair status & cost

### Business Intelligence Reports (`/api/reports`)
* `GET /api/reports/occupancy`: Hostel occupancy analysis
* `GET /api/reports/occupancy/blocks`: Block occupancy rankings (`ROW_NUMBER`)
* `GET /api/reports/fees/ranking`: Fee debtor rankings (`DENSE_RANK`)
* `GET /api/reports/allocations/stays`: Stay duration analytics
* `GET /api/reports/complaints`: Complaint resolution rates & times
* `GET /api/reports/maintenance`: Maintenance cost analytics
* `GET /api/reports/visitors`: Visitor traffic trends
* `GET /api/reports/hostel-summary`: **Multi-Domain Operational Dashboard Summary**

---

## 5. Verification Sign-Off Matrix

```text
============================================================
HOSTELFLOW APPLICATION VERIFICATION SIGN-OFF
============================================================
[PASS] 6.1 Application Environment & Dependencies
[PASS] 6.2 Environment Configuration & Secret Management
[PASS] 6.3 PyMySQL Database Connection Layer
[PASS] 6.4 Repository & Service Layer Architecture
[PASS] 6.5 Student Registration Vertical Slice
[PASS] 6.6 Allocation Lifecycle Slice (Allocations, Transfers, Vacate)
[PASS] 6.7 Finance & Fee Collection Slice (Payments, Dues, History)
[PASS] 6.8 Visitor Management Slice (Check-In, Check-Out, Gate Reports)
[PASS] 6.9 Complaints & Maintenance Slice (Grievances, Staff, Repairs)
[PASS] 6.10 Reporting API & BI Integration (8 Analytical Reports)
[PASS] 6.11 Authentication & RBAC (Session Auth, Roles, 401/403 Enforcement)
[PASS] 6.12 Frontend / Admin Dashboard UI (Design Tokens, REST Client, Pages)
[PASS] 6.13 Cross-Domain End-to-End Master Lifecycle Verification
============================================================
PHASE 6 APPLICATION LAYER COMPLETED & VERIFIED SUCCESSFULLY.
============================================================
```
