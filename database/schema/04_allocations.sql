-- HostelFlow Schema Layer 4: Allocations, Transfers & Vacating Records
-- Document ID: HOSTEL-SQL-004
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Table: allocations
CREATE TABLE IF NOT EXISTS allocations (
    allocation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    bed_id BIGINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    status ENUM('active', 'vacated', 'transferred') DEFAULT 'active',
    active_bed_key BIGINT GENERATED ALWAYS AS (IF(status = 'active', bed_id, NULL)) STORED,
    active_student_key BIGINT GENERATED ALWAYS AS (IF(status = 'active', student_id, NULL)) STORED,
    CONSTRAINT fk_allocations_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE RESTRICT,
    CONSTRAINT fk_allocations_bed FOREIGN KEY (bed_id) REFERENCES beds (bed_id) ON DELETE RESTRICT,
    CONSTRAINT uq_allocations_active_bed UNIQUE (active_bed_key),
    CONSTRAINT uq_allocations_active_student UNIQUE (active_student_key),
    CONSTRAINT chk_allocations_dates CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: transfers
CREATE TABLE IF NOT EXISTS transfers (
    transfer_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    old_allocation_id BIGINT NOT NULL,
    new_allocation_id BIGINT NOT NULL,
    transfer_date DATE NOT NULL,
    reason TEXT NOT NULL,
    CONSTRAINT fk_transfers_old_alloc FOREIGN KEY (old_allocation_id) REFERENCES allocations (allocation_id) ON DELETE RESTRICT,
    CONSTRAINT fk_transfers_new_alloc FOREIGN KEY (new_allocation_id) REFERENCES allocations (allocation_id) ON DELETE RESTRICT,
    CONSTRAINT chk_transfers_different_alloc CHECK (old_allocation_id != new_allocation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: vacating_records
CREATE TABLE IF NOT EXISTS vacating_records (
    vacating_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    allocation_id BIGINT NOT NULL UNIQUE,
    vacating_date DATE NOT NULL,
    reason ENUM('graduation', 'transfer_out', 'disciplinary', 'personal', 'other') NOT NULL,
    clearance_status ENUM('cleared', 'pending_dues', 'damage_pending') NOT NULL,
    deposit_refund_amount DECIMAL(10,2) DEFAULT 0.00,
    remarks TEXT NULL,
    CONSTRAINT fk_vacating_alloc FOREIGN KEY (allocation_id) REFERENCES allocations (allocation_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
