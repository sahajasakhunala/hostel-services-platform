-- HostelFlow Schema Layer 5: Fee Structures, Invoices & Payments
-- Document ID: HOSTEL-SQL-005
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Table: fee_structures
CREATE TABLE IF NOT EXISTS fee_structures (
    fee_structure_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    room_type_id BIGINT NOT NULL,
    academic_year_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_fee_struct_room_type FOREIGN KEY (room_type_id) REFERENCES room_types (room_type_id) ON DELETE RESTRICT,
    CONSTRAINT fk_fee_struct_academic_year FOREIGN KEY (academic_year_id) REFERENCES academic_years (academic_year_id) ON DELETE RESTRICT,
    CONSTRAINT uq_fee_struct_type_year UNIQUE (room_type_id, academic_year_id),
    CONSTRAINT chk_fee_struct_amount CHECK (amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: invoices
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    fee_structure_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    outstanding_balance DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('unpaid', 'partially_paid', 'paid') DEFAULT 'unpaid',
    CONSTRAINT fk_invoices_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE RESTRICT,
    CONSTRAINT fk_invoices_fee_struct FOREIGN KEY (fee_structure_id) REFERENCES fee_structures (fee_structure_id) ON DELETE RESTRICT,
    CONSTRAINT chk_invoices_total_amount CHECK (total_amount >= 0.00),
    CONSTRAINT chk_invoices_balance CHECK (outstanding_balance >= 0.00 AND outstanding_balance <= total_amount)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('cash', 'card', 'bank_transfer', 'online') NOT NULL,
    receipt_number VARCHAR(50) NOT NULL UNIQUE,
    remarks VARCHAR(255) NULL,
    CONSTRAINT fk_payments_invoice FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id) ON DELETE RESTRICT,
    CONSTRAINT chk_payments_amount CHECK (amount > 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
