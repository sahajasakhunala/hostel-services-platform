-- HostelFlow Schema Layer 6: Visitors, Complaints & Maintenance
-- Document ID: HOSTEL-SQL-006
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Table: visitors
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    visitor_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    id_type VARCHAR(50) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    check_in_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP NULL,
    CONSTRAINT fk_visitors_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE RESTRICT,
    CONSTRAINT chk_visitors_time CHECK (check_out_time IS NULL OR check_out_time >= check_in_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: maintenance_staff
CREATE TABLE IF NOT EXISTS maintenance_staff (
    staff_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: complaints
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    subject VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    resolution_notes TEXT NULL,
    assigned_staff_id BIGINT NULL,
    filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    CONSTRAINT fk_complaints_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE RESTRICT,
    CONSTRAINT fk_complaints_category FOREIGN KEY (category_id) REFERENCES complaint_categories (category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_complaints_staff FOREIGN KEY (assigned_staff_id) REFERENCES maintenance_staff (staff_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: maintenance_requests
CREATE TABLE IF NOT EXISTS maintenance_requests (
    request_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    room_id BIGINT NOT NULL,
    assigned_staff_id BIGINT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('pending', 'assigned', 'in_progress', 'completed') DEFAULT 'pending',
    cost DECIMAL(10,2) DEFAULT 0.00,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    CONSTRAINT fk_maint_room FOREIGN KEY (room_id) REFERENCES rooms (room_id) ON DELETE RESTRICT,
    CONSTRAINT fk_maint_staff FOREIGN KEY (assigned_staff_id) REFERENCES maintenance_staff (staff_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
