-- HostelFlow Reference Seed Data
-- Document ID: HOSTEL-SEED-001
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Seed departments
INSERT INTO departments (name, code) VALUES
('Department of Computer Science and Engineering', 'CSE'),
('Department of Electronics and Communication Engineering', 'ECE'),
('Department of Mechanical Engineering', 'MECH'),
('Department of Civil Engineering', 'CIVIL'),
('Department of Business Administration', 'DBA')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Seed room_types
INSERT INTO room_types (name, base_capacity) VALUES
('Single Occupancy AC', 1),
('Double Sharing AC', 2),
('Double Sharing Non-AC', 2),
('Triple Sharing Non-AC', 3),
('Four Sharing Non-AC', 4)
ON DUPLICATE KEY UPDATE base_capacity=VALUES(base_capacity);

-- Seed academic_years
INSERT INTO academic_years (year_label, start_date, end_date) VALUES
('2024-2025', '2024-08-01', '2025-05-31'),
('2025-2026', '2025-08-01', '2026-05-31'),
('2026-2027', '2026-08-01', '2027-05-31')
ON DUPLICATE KEY UPDATE start_date=VALUES(start_date);

-- Seed complaint_categories
INSERT INTO complaint_categories (name) VALUES
('Electrical & Lighting'),
('Plumbing & Sanitation'),
('Internet & Connectivity'),
('Furniture & Carpentry'),
('Cleanliness & Housekeeping'),
('Noise & Discipline')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Seed roles
INSERT INTO roles (name, description) VALUES
('Administrator', 'Full access to platform administration, user management, and system config.'),
('Warden', 'Hostel block management, allocation approvals, student transfers, and discipline.'),
('Student', 'Hostel resident with access to personal profile, invoices, complaints, and visitors.'),
('Security Staff', 'Gate access logging and visitor tracking.'),
('Maintenance Staff', 'Infrastructure repair handling and status updates.')
ON DUPLICATE KEY UPDATE description=VALUES(description);
