# HostelFlow — University Hostel Services Platform

HostelFlow is a secure, transaction-safe, and high-performance university hostel management platform. It incorporates robust domain rules, transactional integrity controls, multi-threaded concurrency safety, and comprehensive audit observability.

---

## 1. System & Architecture Overview

HostelFlow is built using a layered software architecture:
- **Presentation UI**: Modern web administration dashboard built using HTML5, Vanilla CSS, and JavaScript.
- **Application Factory**: Configured with Flask app factory patterns, route correlations (`X-Request-ID`), and centralized exception logging.
- **Repository Access Layer**: Database queries implemented as raw parameterized SQL executed via PyMySQL contexts.
- **Relational Schema**: 26 relational tables normalized to Third Normal Form (3NF), executing point-lookups and complex reporting.

---

## 2. Hardened Security & Resilience

- **Authentication & Authorization**: Werkzeug password hashing, secure session cookies (`HttpOnly`, `SameSite=Lax`, `Secure` in production), and decorator-driven Role-Based Access Control (RBAC).
- **Tenant Boundary Enforcement**: Decorator-driven student ownership checks block horizontal privilege escalation attempts.
- **Resilience Controls**: strict request payload limits (16 MB), safe 500 error sanitization, and fail-fast startup configuration validation.
- **Logical Recovery**: Logical backup (`backup.py` / `backup_database.sh`) and isolated database restoration utilities (`restore.py` / `restore_database.sh`) verified under a 1.15-second Recovery Time Objective (RTO).

---

## 3. Quick Start & Setup

### Requirements
- Python 3.10+
- MySQL 9.7+

### Installation
1. Clone the repository and configure virtual environment:
   ```bash
   git clone https://github.com/sahajasakhunala/hostel-services-platform.git
   cd hostel-services-platform
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Initialize database configuration:
   ```bash
   cp .env.example .env
   # Configure your local credentials inside .env
   ```
3. Verify installation and start Flask:
   ```bash
   # Run full verification
   .\venv\Scripts\python tests/run_full_verification.py
   
   # Start local development server
   python run.py
   ```

---

## 4. Documentation Directory Index

Detailed guides are located in the [docs/](file:///c:/Users/LENOVO/hostel-services-platform/docs) directory:

- **System Architecture**: [docs/architecture/system_architecture.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/architecture/system_architecture.md)
- **Database Schema & Normalization**: [docs/architecture/database_architecture.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/architecture/database_architecture.md)
- **Application Design Layer**: [docs/architecture/application_architecture.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/architecture/application_architecture.md)
- **REST API Endpoints**: [docs/architecture/api_architecture.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/architecture/api_architecture.md)
- **Security Engineering**: [docs/architecture/security_architecture.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/architecture/security_architecture.md)
- **Developer Guide**: [docs/guides/development.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/guides/development.md)
- **Database Setup Runbook**: [docs/guides/database_setup.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/guides/database_setup.md)
- **Testing Reference**: [docs/guides/testing.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/guides/testing.md)
- **Logical Backup & Recovery**: [docs/operations/backup_restore.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/operations/backup_restore.md)
- **Troubleshooting Operations**: [docs/operations/troubleshooting.md](file:///c:/Users/LENOVO/hostel-services-platform/docs/operations/troubleshooting.md)

---

## 5. Future Roadmap

The following cloud-native enhancements are planned as future roadmap extensions:
- **Containerization**: Dockerizing application and database layers.
- **Continuous Integration**: Setting up GitHub Actions workflows.
- **External Notifications**: Integrating email and SMS gateways.
