# HostelFlow

[![Database](https://img.shields.io/badge/Database-MySQL%209.7.1-blue?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Backend](https://img.shields.io/badge/Backend-Python%203.10%20%7C%20Flask-green?logo=python&logoColor=white)](https://www.python.org/)
[![Testing](https://img.shields.io/badge/Tests-pytest-orange?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![VCS](https://img.shields.io/badge/VCS-Git%202.53-lightgrey?logo=git&logoColor=white)](https://git-scm.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **HostelFlow** is a production-inspired, highly-normalized relational database management system (RDBMS) and transactional service layer for hostel accommodation and student service lifecycle orchestration. 

Specifically architected around **MySQL 9.7.1**, this system eliminates typical application-level data corruption risks by using the database engine as the ultimate authority on referential integrity and state transitions.

---

## Architectural Core

The project implements a layered service-oriented architecture designed to handle concurrent operations safely:

```
[ Web Interface: Jinja2/HTML/CSS/JS ]
                 │
                 ▼
[ Application Layer: Flask Blueprints & WTForms ]
                 │
                 ▼
[ Service Layer: Transaction-Safe Business Engines ]
                 │ (Atomic Workflows & Python Validation)
                 ▼
[ Data Access Layer: SQLAlchemy Core / Raw SQL Queries ]
                 │
                 ▼
[ Database Layer: MySQL 9.7.1 Engine ]
  ├── Generated-Column State-Derived Uniqueness Constraints
  ├── Transaction-Safe State Isolation (Row Locking)
  ├── Cross-Row Business Rule Triggers
  ├── Performance-Optimized Indexes
  └── CTE/Window-Function Reporting Views
```

---

## Core Engineering Innovations

### 1. State-Derived Structural Invariants (Generated Columns)
To enforce that a student can have at most one active bed allocation, and a bed can host at most one active student, HostelFlow bypasses manual state synchronization. It uses MySQL virtual/stored generated columns that compute active keys dynamically from the allocation status:
* `active_bed_key = IF(status = 'active', bed_id, NULL)`
* `active_student_key = IF(status = 'active', student_id, NULL)`

Applying a `UNIQUE` index on these generated columns forces the database engine to guarantee one-active-resident-per-bed and one-active-allocation-per-student structurally, even if the application layer is bypassed entirely.

### 2. The Capacity-Through-Beds Invariant
Instead of executing complex cross-table aggregate subqueries during every student allocation to verify room capacity, HostelFlow models physical beds as the atomic resource. 
A `BEFORE INSERT` trigger on `beds` enforces that the number of physical beds in a room never exceeds the room's physical capacity. Uniqueness constraints on bed allocations then automatically prevent room over-occupancy.

### 3. Concurrency-Safe Transactional Orchestration
All core transitions (allocations, student transfers, payments) utilize transaction blocks with explicit locking semantics (e.g., `SELECT ... FOR UPDATE` row locks) to prevent race conditions during simultaneous warden approvals or payment processing.

---

## Repository Structure

```
hostel-services-platform/
│
├── app/                         # Flask Web Application Root
│   ├── __init__.py              # Application Factory
│   ├── config.py                # Environment configurations
│   ├── extensions.py            # Extensions (SQLAlchemy, LoginManager)
│   ├── models/                  # Declarative SQLAlchemy ORM Models
│   ├── repositories/            # Data Access Layer / SQL Execution
│   ├── services/                # Business Logic (Allocation Engine)
│   ├── routes/                  # Controller blueprints (Auth, Admin, etc.)
│   ├── validators/              # WTForms validation & custom rules
│   ├── templates/               # Offline-first CSS-enhanced UI templates
│   └── static/                  # Bundled assets (CSS, JS, local fonts)
│
├── database/                    # SQL Scripts & Engine Definitions
│   ├── 00_database.sql          # DB Initialization
│   ├── schema/                  # Domain-segregated DDL tables
│   ├── constraints/             # Structural CHECK/UNIQUE constraints
│   ├── triggers/                # State-validation triggers
│   ├── procedures/              # Stored Procedures (viva requirements)
│   ├── views/                   # Business views (occupancy, dues, etc.)
│   └── seed/                    # Reference lookups and sample dataset
│
├── tests/                       # Automated Test Suite
│   ├── unit/                    # Validator & logic testing
│   ├── integration/             # Route & endpoint testing
│   └── database/                # Direct SQL constraint/trigger testing
│
├── docs/                        # Complete Engineering Documentation
│   ├── 01-requirements/         # Functional and Non-functional specifications
│   ├── 02-use-cases/            # Detailed actor workflows
│   ├── 03-domain-model/         # Detailed RDBMS candidate domain models
│   ├── 15-viva-preparation/     # Design rationale Q&A for academic review
│   └── diagrams/                # System diagrams (ER, architectural, sequences)
│
├── .gitignore
├── requirements.txt
├── README.md
└── run.py                       # App entry point
```

---

## Getting Started (Development Setup)

### Prerequisites
* Python 3.10.x
* MySQL Community Server 9.7.1
* Git 2.53.x

### 1. Clone & Set Up Directory
```bash
git clone <repository-url>
cd hostel-services-platform
```

### 2. Configure Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
```

### 3. Initialize MySQL Database
Run the schema scripts in the `database/` directory against your local instance:
```bash
mysql -u root -p < database/00_database.sql
# ... (Proceed with running schema, constraint, trigger, and seed scripts)
```

### 4. Running the App
```bash
python run.py
```
The app will spin up locally on `http://localhost:5000`.

---

## License
Distributed under the MIT License. See `LICENSE` for details.
