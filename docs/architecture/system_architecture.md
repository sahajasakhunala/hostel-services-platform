# HostelFlow System Architecture Guide

## 1. End-to-End System Flow

HostelFlow implements a classic layered architecture with strict separation of concerns, routing control flow from the client browser down to the database storage engine.

```text
  [ Client Browser / Admin UI ]  (HTML5, Vanilla CSS/JS, Fetch API)
               │
               ▼
     [ Flask Routing Layer ]     (Blueprints, REST endpoints, JSON responses)
               │
               ▼
     [ Service Control Layer ]   (Business logic validation, coordination)
               │
               ▼
    [ Repository Access Layer ]  (PyMySQL execution, raw SQL parameterization)
               │
               ▼
    [ Database Storage Engine ]  (MySQL 9.7: Tables, Views, Stored Procedures, Triggers)
```

### Layer Responsibilities

1. **Client Browser / Admin UI**: Displays interfaces for student lifecycles, allocations, billing, maintenance, and gate logs. Interacts with the backend via asynchronous `fetch()` API calls, submitting and receiving JSON payloads.
2. **Flask Routing Layer**: Defines REST API endpoints (`/api/*`). Handles session-based authentication, Role-Based Access Control (RBAC) authorization, request payload size limits (16 MB), correlation ID mapping (`X-Request-ID`), and safe exception handling.
3. **Service Control Layer**: Encapsulates business logic rules (e.g., verifying eligibility for bed allocations, calculating invoice balances, coordinating payment processing).
4. **Repository Access Layer**: Manages database query execution. Avoids thick ORM overhead, utilizing raw parameterized SQL statements executed via PyMySQL database connection contexts to prevent SQL injection.
5. **Database Storage Engine**: Maintains state and enforces relational integrity. Incorporates transactional stored procedures, operational views, triggers, and composite query indexes.

---

## 2. Cross-Cutting Infrastructure Components

### Authentication & Authorization (RBAC)
User authentication is managed via session-based cookies. Authorized access to routes is validated using custom decorators:
- `@login_required`: Restricts routes to users with active sessions.
- `@role_required`: Restricts routes to users holding authorized roles (e.g., `Administrator`, `Warden`, `Security Staff`, `Maintenance Staff`, `Student`).
- `@student_ownership_required`: Standardizes horizontal boundary checks, ensuring student users can only access their own profile and financial records.

### Structured Logging & Request Correlation
Structured logs are separated across three dedicated log files in `logs/`:
- `application.log`: Application operations.
- `security.log`: Authentication, authorization, and privilege violations.
- `error.log`: Server-side unhandled exception tracebacks.
A unique correlation ID (`request_id`) is attached to every incoming HTTP request and propagated throughout all log records to facilitate debugging.

### Fail-Fast Configuration & Safety
The application factory audits and validates the environment configuration (`validate_config()`) during startup. If required variables are missing or insecure configurations are detected in production (e.g., `DEBUG = True` or default development secrets), the startup halts immediately.
