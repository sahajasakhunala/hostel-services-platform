-- HostelFlow Schema Layer 3: Courses, Students & Guardians
-- Document ID: HOSTEL-SQL-003
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Table: courses
CREATE TABLE IF NOT EXISTS courses (
    course_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    department_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    degree_level ENUM('UG', 'PG', 'PhD') NOT NULL,
    CONSTRAINT fk_courses_department FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE RESTRICT,
    CONSTRAINT uq_courses_dept_name UNIQUE (department_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: students
CREATE TABLE IF NOT EXISTS students (
    student_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('M', 'F', 'Other') NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    department_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    academic_year_id BIGINT NOT NULL,
    status ENUM('active', 'inactive', 'graduated') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_students_department FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE RESTRICT,
    CONSTRAINT fk_students_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE RESTRICT,
    CONSTRAINT fk_students_academic_year FOREIGN KEY (academic_year_id) REFERENCES academic_years (academic_year_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: guardians
CREATE TABLE IF NOT EXISTS guardians (
    guardian_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NULL,
    CONSTRAINT fk_guardians_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
