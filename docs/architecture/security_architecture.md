# HostelFlow Security Architecture Guide

## 1. Application Layer Security Boundaries

HostelFlow implements a defense-in-depth security model to protect application entry points and maintain boundaries between tenants.

### Session Cookies & Cookie Hardening
User authentication session contexts are managed via standard Flask secure cookie sessions. Hardening controls applied:
- `SESSION_COOKIE_HTTPONLY = True`: Blocks client-side JavaScript access, mitigating Cross-Site Scripting (XSS) session hijacking.
- `SESSION_COOKIE_SAMESITE = 'Lax'`: Instructs browsers not to send session cookies in cross-site requests, mitigating Cross-Site Request Forgery (CSRF).
- `SESSION_COOKIE_SECURE = True` (Production): Restricts cookie transmission exclusively over encrypted HTTPS connections.

### Role-Based Access Control (RBAC)
Role authorization is enforced on REST API endpoints via decorators:
- `@role_required('administrator')`: Enforces administrative permissions.
- `@role_required('warden')`: Enforces warden permissions.
- `@role_required('student')`: Enforces student permissions.

### Horizontal Tenant Ownership Check
The `@student_ownership_required` decorator checks that non-administrative users can only access resources matching their own session `student_id`. This prevents horizontal privilege escalation (e.g., a student trying to view another student's profile or invoices).

---

## 2. Input Validation, Limits & Error Sanitization

### Reusable Input Validation Layer
All incoming parameters (students, visitors, complaints, maintenance, payments) are validated in `app/utils/validation.py` using helper functions before database transactions are invoked.

### Payload Limits
To prevent Denial of Service (DoS) attacks via memory exhaustion, the Flask configuration enforces a strict payload size limit:
- `MAX_CONTENT_LENGTH = 16 * 1024 * 1024` (16 Megabytes).

### Centralized Error Sanitization
To prevent database structure and environment leakage:
- In production, unhandled exceptions are caught globally by the `@app.errorhandler(500)` handler.
- Detailed traceback messages are written server-side to `logs/error.log` along with the request correlation ID (`request_id`).
- The client receives a sanitized, generic error response: `{"status": "error", "message": "An internal server error occurred."}`.
