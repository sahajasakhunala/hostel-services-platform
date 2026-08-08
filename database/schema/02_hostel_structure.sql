-- HostelFlow Schema Layer 2: Physical Infrastructure Hierarchy
-- Document ID: HOSTEL-SQL-002
-- Target Engine: MySQL 9.7.1+

USE hostelflow_db;

-- Table: hostels
CREATE TABLE IF NOT EXISTS hostels (
    hostel_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    gender_type ENUM('M', 'F', 'Co-ed') NOT NULL,
    address VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: blocks
CREATE TABLE IF NOT EXISTS blocks (
    block_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hostel_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_blocks_hostel FOREIGN KEY (hostel_id) REFERENCES hostels (hostel_id) ON DELETE RESTRICT,
    CONSTRAINT uq_blocks_hostel_name UNIQUE (hostel_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: floors
CREATE TABLE IF NOT EXISTS floors (
    floor_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    block_id BIGINT NOT NULL,
    floor_number INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_floors_block FOREIGN KEY (block_id) REFERENCES blocks (block_id) ON DELETE RESTRICT,
    CONSTRAINT uq_floors_block_number UNIQUE (block_id, floor_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: rooms
CREATE TABLE IF NOT EXISTS rooms (
    room_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    floor_id BIGINT NOT NULL,
    room_type_id BIGINT NOT NULL,
    room_number VARCHAR(20) NOT NULL,
    capacity INT NOT NULL,
    status ENUM('active', 'under_maintenance', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rooms_floor FOREIGN KEY (floor_id) REFERENCES floors (floor_id) ON DELETE RESTRICT,
    CONSTRAINT fk_rooms_type FOREIGN KEY (room_type_id) REFERENCES room_types (room_type_id) ON DELETE RESTRICT,
    CONSTRAINT uq_rooms_floor_number UNIQUE (floor_id, room_number),
    CONSTRAINT chk_rooms_capacity CHECK (capacity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: beds
CREATE TABLE IF NOT EXISTS beds (
    bed_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    room_id BIGINT NOT NULL,
    bed_code VARCHAR(20) NOT NULL,
    status ENUM('available', 'occupied', 'under_maintenance') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_beds_room FOREIGN KEY (room_id) REFERENCES rooms (room_id) ON DELETE RESTRICT,
    CONSTRAINT uq_beds_room_code UNIQUE (room_id, bed_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
