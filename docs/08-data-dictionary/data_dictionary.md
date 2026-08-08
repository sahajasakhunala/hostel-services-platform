# HostelFlow — Comprehensive Data Dictionary

**Document ID**: HOSTEL-DD-001  
**Version**: 1.0  
**Status**: Step 8 Complete — Exhaustive Data Dictionary  

---

## 1. Physical Infrastructure Domain

### 1.1 `hostels`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `hostel_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique identifier for hostel building |
| `name` | `VARCHAR(100)` | NO | None | UK | — | Name of hostel building (must be unique) |
| `gender_type` | `ENUM('M','F','Co-ed')` | NO | None | — | — | Target resident gender demographic |
| `address` | `VARCHAR(255)` | YES | NULL | — | — | Physical building location/address |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

### 1.2 `blocks`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `block_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique identifier for hostel block |
| `hostel_id` | `BIGINT` | NO | None | FK | `hostels.hostel_id` | Parent hostel building |
| `name` | `VARCHAR(50)` | NO | None | — | — | Name of block (e.g., 'Block A') |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

### 1.3 `floors`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `floor_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique identifier for floor |
| `block_id` | `BIGINT` | NO | None | FK | `blocks.block_id` | Parent block |
| `floor_number` | `INT` | NO | None | — | — | Level number (0 for Ground, 1, 2, etc.) |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

### 1.4 `room_types`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `room_type_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique room type identifier |
| `name` | `VARCHAR(50)` | NO | None | UK | — | Type name (Single, Double, Triple, Dormitory) |
| `base_capacity` | `INT` | NO | None | — | — | Standard bed capacity for type (CHECK > 0) |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

### 1.5 `rooms`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `room_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique room identifier |
| `floor_id` | `BIGINT` | NO | None | FK | `floors.floor_id` | Floor where room is located |
| `room_type_id` | `BIGINT` | NO | None | FK | `room_types.room_type_id` | Room configuration classification |
| `room_number` | `VARCHAR(20)` | NO | None | — | — | Room identifier number/code |
| `capacity` | `INT` | NO | None | — | — | Max capacity limit for beds (CHECK > 0) |
| `status` | `ENUM(...)` | NO | `'active'` | — | — | Room operational status ('active','under_maintenance','inactive') |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

### 1.6 `beds`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `bed_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique atomic bed identifier |
| `room_id` | `BIGINT` | NO | None | FK | `rooms.room_id` | Room containing bed |
| `bed_code` | `VARCHAR(20)` | NO | None | — | — | Code identifier within room (e.g., 'B1', 'B2') |
| `status` | `ENUM(...)` | NO | `'available'` | — | — | Availability status ('available','occupied','under_maintenance') |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Record creation timestamp |

---

## 2. Academic & Demographics Domain

### 2.1 `departments`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `department_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique department identifier |
| `name` | `VARCHAR(100)` | NO | None | UK | — | Department full name |
| `code` | `VARCHAR(20)` | NO | None | UK | — | Short department code (e.g., 'CSE') |

### 2.2 `courses`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `course_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique degree program identifier |
| `department_id` | `BIGINT` | NO | None | FK | `departments.department_id` | Offering department |
| `name` | `VARCHAR(100)` | NO | None | — | — | Course degree name (e.g., 'B.Tech CSE') |
| `degree_level` | `ENUM(...)` | NO | None | — | — | Level ('UG', 'PG', 'PhD') |

### 2.3 `academic_years`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `academic_year_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Academic cycle identifier |
| `year_label` | `VARCHAR(20)` | NO | None | UK | — | Label (e.g., '2025-2026') |
| `start_date` | `DATE` | NO | None | — | — | Cycle start date |
| `end_date` | `DATE` | NO | None | — | — | Cycle end date (CHECK > start_date) |

### 2.4 `students`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `student_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique student identifier |
| `registration_number` | `VARCHAR(50)` | NO | None | UK | — | Institutional roll/reg number (BR-01) |
| `first_name` | `VARCHAR(50)` | NO | None | — | — | Student first name |
| `last_name` | `VARCHAR(50)` | NO | None | — | — | Student last name |
| `dob` | `DATE` | NO | None | — | — | Date of birth |
| `gender` | `ENUM(...)` | NO | None | — | — | Gender ('M','F','Other') |
| `email` | `VARCHAR(100)` | NO | None | UK | — | Unique contact email |
| `phone` | `VARCHAR(20)` | NO | None | — | — | Primary contact number |
| `department_id` | `BIGINT` | NO | None | FK | `departments.department_id` | Department |
| `course_id` | `BIGINT` | NO | None | FK | `courses.course_id` | Enrolled degree course |
| `academic_year_id` | `BIGINT` | NO | None | FK | `academic_years.academic_year_id` | Academic year context |
| `status` | `ENUM(...)` | NO | `'active'` | — | — | Lifecycle status ('active','inactive','graduated') |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Registration timestamp |

### 2.5 `guardians`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `guardian_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique guardian identifier |
| `student_id` | `BIGINT` | NO | None | FK | `students.student_id` | Associated student |
| `name` | `VARCHAR(100)` | NO | None | — | — | Guardian full name |
| `relationship` | `VARCHAR(50)` | NO | None | — | — | Relationship (Father, Mother, Guardian) |
| `phone` | `VARCHAR(20)` | NO | None | — | — | Primary contact phone |
| `email` | `VARCHAR(100)` | YES | NULL | — | — | Optional contact email |

---

## 3. Allocation & Transition Domain

### 3.1 `allocations`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `allocation_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique stay allocation identifier |
| `student_id` | `BIGINT` | NO | None | FK | `students.student_id` | Allocated student |
| `bed_id` | `BIGINT` | NO | None | FK | `beds.bed_id` | Assigned bed |
| `start_date` | `DATE` | NO | None | — | — | Stay allocation start date |
| `end_date` | `DATE` | YES | NULL | — | — | Allocation end date (CHECK >= start_date) |
| `status` | `ENUM(...)` | NO | `'active'` | — | — | Status ('active','vacated','transferred') |
| `active_bed_key` | `BIGINT` | YES | Derived | UK | — | Generated key: `IF(status='active', bed_id, NULL)` (BR-02) |
| `active_student_key` | `BIGINT` | YES | Derived | UK | — | Generated key: `IF(status='active', student_id, NULL)` (BR-03) |

### 3.2 `transfers`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `transfer_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique transfer event identifier |
| `old_allocation_id` | `BIGINT` | NO | None | FK | `allocations.allocation_id` | Source closed allocation |
| `new_allocation_id` | `BIGINT` | NO | None | FK | `allocations.allocation_id` | Target active allocation |
| `transfer_date` | `DATE` | NO | None | — | — | Date transfer took effect |
| `reason` | `TEXT` | NO | None | — | — | Documented reason for bed transfer (BR-10) |

### 3.3 `vacating_records`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `vacating_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique vacating record identifier |
| `allocation_id` | `BIGINT` | NO | None | UK, FK | `allocations.allocation_id` | Associated closed allocation |
| `vacating_date` | `DATE` | NO | None | — | — | Official checkout date |
| `reason` | `ENUM(...)` | NO | None | — | — | Reason ('graduation','transfer_out','disciplinary','personal','other') |
| `clearance_status` | `ENUM(...)` | NO | None | — | — | Clearance status ('cleared','pending_dues','damage_pending') |
| `deposit_refund_amount` | `DECIMAL(10,2)` | NO | `0.00` | — | — | Refundable deposit amount returned |
| `remarks` | `TEXT` | YES | NULL | — | — | Additional vacating remarks |

---

## 4. Financial Domain

### 4.1 `fee_structures`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `fee_structure_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique fee structure identifier |
| `room_type_id` | `BIGINT` | NO | None | FK | `room_types.room_type_id` | Target room type |
| `academic_year_id` | `BIGINT` | NO | None | FK | `academic_years.academic_year_id` | Valid academic year |
| `amount` | `DECIMAL(10,2)` | NO | None | — | — | Accommodation fee amount (CHECK >= 0) |

### 4.2 `invoices`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `invoice_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique invoice billing identifier |
| `student_id` | `BIGINT` | NO | None | FK | `students.student_id` | Billed student |
| `fee_structure_id` | `BIGINT` | NO | None | FK | `fee_structures.fee_structure_id` | Applicable fee rate structure |
| `total_amount` | `DECIMAL(10,2)` | NO | None | — | — | Total billed invoice amount |
| `outstanding_balance` | `DECIMAL(10,2)` | NO | None | — | — | Remaining unpaid balance (CHECK <= total) |
| `due_date` | `DATE` | NO | None | — | — | Payment due date |
| `status` | `ENUM(...)` | NO | `'unpaid'` | — | — | Payment status ('unpaid','partially_paid','paid') |

### 4.3 `payments`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `payment_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique payment transaction identifier |
| `invoice_id` | `BIGINT` | NO | None | FK | `invoices.invoice_id` | Billed invoice |
| `amount` | `DECIMAL(10,2)` | NO | None | — | — | Payment transaction amount (BR-06) |
| `payment_date` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Transaction timestamp |
| `payment_method` | `ENUM(...)` | NO | None | — | — | Method ('cash','card','bank_transfer','online') |
| `receipt_number` | `VARCHAR(50)` | NO | None | UK | — | Unique transaction receipt code |
| `remarks` | `VARCHAR(255)` | YES | NULL | — | — | Additional payment notes |

---

## 5. Services & Incidents Domain

### 5.1 `visitors`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `visitor_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique visitor entry log ID |
| `student_id` | `BIGINT` | NO | None | FK | `students.student_id` | Student being visited |
| `visitor_name` | `VARCHAR(100)` | NO | None | — | — | External visitor full name |
| `phone` | `VARCHAR(20)` | NO | None | — | — | Visitor phone contact |
| `id_type` | `VARCHAR(50)` | NO | None | — | — | Government ID type (Aadhaar, Passport, etc.) |
| `id_number` | `VARCHAR(50)` | NO | None | — | — | Government ID number |
| `purpose` | `VARCHAR(255)` | NO | None | — | — | Visit purpose |
| `check_in_time` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Gate check-in timestamp |
| `check_out_time` | `TIMESTAMP` | YES | NULL | — | — | Departure timestamp (CHECK >= check_in) (BR-07) |

### 5.2 `complaint_categories`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `category_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Category identifier |
| `name` | `VARCHAR(50)` | NO | None | UK | — | Category name (Noise, Plumbing, Electrical, etc.) |

### 5.3 `complaints`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `complaint_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique complaint identifier |
| `student_id` | `BIGINT` | NO | None | FK | `students.student_id` | Filing student |
| `category_id` | `BIGINT` | NO | None | FK | `complaint_categories.category_id` | Grievance category |
| `subject` | `VARCHAR(150)` | NO | None | — | — | Brief complaint title |
| `description` | `TEXT` | NO | None | — | — | Detailed complaint description |
| `priority` | `ENUM(...)` | NO | `'medium'` | — | — | Priority ('low','medium','high','urgent') |
| `status` | `ENUM(...)` | NO | `'open'` | — | — | Status ('open','in_progress','resolved','closed') |
| `resolution_notes` | `TEXT` | YES | NULL | — | — | Mandatory notes upon resolution (BR-08) |
| `assigned_staff_id` | `BIGINT` | YES | NULL | FK | `maintenance_staff.staff_id` | Assigned staff |
| `filed_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Filing timestamp |
| `resolved_at` | `TIMESTAMP` | YES | NULL | — | — | Resolution timestamp |

### 5.4 `maintenance_staff`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `staff_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Maintenance staff identifier |
| `name` | `VARCHAR(100)` | NO | None | — | — | Staff full name |
| `specialty` | `VARCHAR(50)` | NO | None | — | — | Specialty (Electrician, Plumber, Carpenter, etc.) |
| `phone` | `VARCHAR(20)` | NO | None | — | — | Contact phone number |

### 5.5 `maintenance_requests`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `request_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique maintenance request ID |
| `room_id` | `BIGINT` | NO | None | FK | `rooms.room_id` | Room requiring repair |
| `assigned_staff_id` | `BIGINT` | YES | NULL | FK | `maintenance_staff.staff_id` | Assigned staff member |
| `category` | `VARCHAR(50)` | NO | None | — | — | Category of issue |
| `description` | `TEXT` | NO | None | — | — | Problem description |
| `priority` | `ENUM(...)` | NO | `'medium'` | — | — | Priority ('low','medium','high','urgent') |
| `status` | `ENUM(...)` | NO | `'pending'` | — | — | Status ('pending','assigned','in_progress','completed') |
| `cost` | `DECIMAL(10,2)` | NO | `0.00` | — | — | Repair cost |
| `reported_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Report timestamp |
| `completed_at` | `TIMESTAMP` | YES | NULL | — | — | Completion timestamp |

---

## 6. Security & Audit Domain

### 6.1 `users`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `user_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique system user ID |
| `username` | `VARCHAR(50)` | NO | None | UK | — | Login username |
| `password_hash` | `VARCHAR(255)` | NO | None | — | — | bcrypt hashed password (BR-17) |
| `student_id` | `BIGINT` | YES | NULL | UK, FK | `students.student_id` | Optional link to student |
| `staff_id` | `BIGINT` | YES | NULL | UK, FK | `maintenance_staff.staff_id` | Optional link to staff |
| `is_active` | `BOOLEAN` | NO | `TRUE` | — | — | Account state flag |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | User creation timestamp |

### 6.2 `roles`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `role_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Security role ID |
| `name` | `VARCHAR(50)` | NO | None | UK | — | Role name (Admin, Warden, Security, Maintenance, Student) |
| `description` | `VARCHAR(255)` | YES | NULL | — | — | Role scope description |

### 6.3 `user_roles`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `user_id` | `BIGINT` | NO | None | PK, FK | `users.user_id` | M:N user junction link |
| `role_id` | `BIGINT` | NO | None | PK, FK | `roles.role_id` | M:N role junction link |

### 6.4 `audit_logs`
| Column Name | Data Type | Nullable | Default | Key | References | Business Rule / Description |
|---|---|---|---|---|---|---|
| `log_id` | `BIGINT` | NO | `AUTO_INCREMENT` | PK | — | Unique audit record ID |
| `user_id` | `BIGINT` | YES | NULL | FK | `users.user_id` | Executing user |
| `action` | `VARCHAR(50)` | NO | None | — | — | Action (INSERT, UPDATE, DELETE, ALLOCATE, TRANSFER) |
| `table_name` | `VARCHAR(50)` | NO | None | — | — | Target table name |
| `record_id` | `BIGINT` | NO | None | — | — | Modified record ID |
| `old_values` | `JSON` | YES | NULL | — | — | Pre-update state JSON snapshot |
| `new_values` | `JSON` | YES | NULL | — | — | Post-update state JSON snapshot |
| `timestamp` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | — | — | Log timestamp |
