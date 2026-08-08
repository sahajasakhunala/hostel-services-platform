# HostelFlow REST API Architecture & Contracts Guide

## 1. REST Endpoint Specifications

HostelFlow implements a REST API returning JSON responses. All request payloads must use `Content-Type: application/json`.

### Authentication Endpoints (`/api/auth`)
* **`POST /api/auth/login`**: Authenticates user credentials.
  - Request: `{"username": "admin", "password": "your_secure_password"}`
  - Response (200): `{"status": "success", "message": "Login successful.", "data": {"user_id": 1, "username": "admin", "roles": ["administrator"]}}`
  - Response (401): `{"status": "error", "message": "Invalid username or password."}`
* **`POST /api/auth/logout`**: Terminates the user session.
  - Response (200): `{"status": "success", "message": "Logged out successfully."}`
* **`GET /api/auth/me`**: Retrieves current session context.
  - Response (200): `{"status": "success", "data": {"user_id": 1, "username": "admin", "roles": ["administrator"]}}`

### Student Endpoints (`/api/students`)
* **`GET /api/students`**: Lists student profiles (accessible to Admin/Warden).
* **`POST /api/students`**: Registers a new student profile.
  - Request: `{"first_name": "John", "last_name": "Doe", "registration_number": "REG101", "email": "john@test.com", "phone": "9876543210", "gender": "male", "dob": "2002-01-01", "emergency_contact": "9876543211"}`
* **`GET /api/students/<student_id>`**: Retrieves specific student details (Ownership checked).

### Bed Allocation Endpoints (`/api/allocations`)
* **`POST /api/allocations`**: Allocates a bed to a student.
  - Request: `{"student_id": 1, "bed_id": 12, "start_date": "2026-09-01"}`
  - Response (200): `{"status": "success", "message": "Bed allocated successfully.", "allocation_id": 101}`

### Billing & Payment Endpoints (`/api/finance`)
* **`GET /api/finance/dues`**: Retrieves student outstanding invoice balances.
* **`POST /api/finance/payments`**: Processes a payment.
  - Request: `{"invoice_id": 1, "amount": 5000.00, "payment_method": "UPI", "receipt_number": "REC999"}`
  - Response (200): `{"status": "success", "message": "Payment processed successfully.", "payment_id": 45}`

### Visitor Endpoints (`/api/visitors`)
* **`POST /api/visitors`**: Logs a guest entry.
  - Request: `{"student_id": 1, "visitor_name": "Jane Doe", "relationship": "Parent", "check_in_time": "2026-08-09 10:00:00"}`
* **`POST /api/visitors/<visitor_id>/checkout`**: Logs visitor checkout.

---

## 2. Standardized Error Payload Semantics

Every API endpoint responds with standard HTTP status code envelopes:

* **`400 Bad Request`**: Request payload failed input validation checks.
  - Response: `{"status": "error", "message": "Validation failed.", "errors": {"phone": "Phone number must be exactly 10 digits."}}`
* **`401 Unauthorized`**: Authentication missing or user session expired.
  - Response: `{"status": "error", "message": "Authentication required. Please log in."}`
* **`403 Forbidden`**: Insufficient RBAC role permissions or ownership check failed.
  - Response: `{"status": "error", "message": "Access forbidden: Insufficient role permissions."}`
* **`404 Not Found`**: Target resource or API route does not exist.
  - Response: `{"status": "error", "message": "Requested resource or API endpoint not found."}`
* **`409 Conflict`**: Target operation violates unique database constraints or concurrency locks.
  - Response: `{"status": "error", "message": "Operation conflict: Student already holds active allocation."}`
* **`500 Internal Error`**: Safe error message hides server tracebacks.
  - Response: `{"status": "error", "message": "An internal server error occurred."}`
