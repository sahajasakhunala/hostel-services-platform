"""
Phase 7.4 — Concurrency & Transaction Stress Testing Suite for HostelFlow.

Verifies that MySQL FOR UPDATE row locks, transactional stored procedures, and state-derived
generated column uniqueness constraints (active_bed_key, active_student_key) hold strict state
invariants under multi-threaded concurrent execution workloads.

Architectural Rule:
- Each worker thread MUST instantiate its own independent PyMySQL database connection.
"""

import os
import sys
import time
import pytest
import pymysql
import pymysql.cursors
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import Config


def get_standalone_connection():
    """Returns an independent PyMySQL connection for a worker thread."""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=Config.DB_CONNECT_TIMEOUT,
        autocommit=False
    )


class TestConcurrencyFixtures:
    """Fixture manager creating and destroying isolated test data for concurrency testing."""

    @staticmethod
    def setup(conn):
        """Creates deterministic CONC-% test data."""
        with conn.cursor() as cursor:
            # 1. Clean up any leftover CONC- records from prior aborted runs
            TestConcurrencyFixtures.teardown(conn)

            # 2. Insert Test Campus/Hostel/Block/Floor/Room/Beds
            cursor.execute("SELECT campus_id FROM campuses LIMIT 1;")
            campus = cursor.fetchone()
            campus_id = campus['campus_id'] if campus else 1

            cursor.execute(
                "INSERT INTO hostels (name, campus_id, gender_policy, total_capacity) VALUES (%s, %s, %s, %s);",
                ('CONC-HOSTEL', campus_id, 'coed', 20)
            )
            hostel_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO blocks (hostel_id, name, block_code) VALUES (%s, %s, %s);",
                (hostel_id, 'CONC-BLOCK', 'CONC-B1')
            )
            block_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO floors (block_id, floor_number) VALUES (%s, %s);",
                (block_id, 1)
            )
            floor_id = cursor.lastrowid

            cursor.execute("SELECT room_type_id FROM room_types LIMIT 1;")
            room_type = cursor.fetchone()
            room_type_id = room_type['room_type_id'] if room_type else 1

            cursor.execute(
                "INSERT INTO rooms (floor_id, room_type_id, room_number, capacity, monthly_rent) VALUES (%s, %s, %s, %s, %s);",
                (floor_id, room_type_id, 'CONC-101', 10, 5000.00)
            )
            room_id = cursor.lastrowid

            bed_ids = []
            for i in range(1, 11):
                bed_code = f"CONC-BED-{i:02d}"
                cursor.execute(
                    "INSERT INTO beds (room_id, bed_code, bed_letter, is_occupied) VALUES (%s, %s, %s, %s);",
                    (room_id, bed_code, chr(64 + i), 0)
                )
                bed_ids.append(cursor.lastrowid)

            # 3. Insert 10 Test Students
            student_ids = []
            for i in range(1, 11):
                reg_no = f"CONC-REG-{i:02d}"
                email = f"conc_stu_{i:02d}@hostelflow.test"
                cursor.execute(
                    """INSERT INTO students 
                       (first_name, last_name, registration_number, email, phone, gender, dob, emergency_contact, status, is_resident)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    (f"ConcStu{i}", "Test", reg_no, email, f"90000000{i:02d}", "male", "2000-01-01", "9000000000", "active", 0)
                )
                student_ids.append(cursor.lastrowid)

            # 4. Insert Test Academic Year & Fee Structure & Invoice
            cursor.execute("SELECT academic_year_id FROM academic_years LIMIT 1;")
            ay = cursor.fetchone()
            ay_id = ay['academic_year_id'] if ay else 1

            cursor.execute(
                "INSERT INTO fee_structures (academic_year_id, room_type_id, total_amount, due_date) VALUES (%s, %s, %s, %s);",
                (ay_id, room_type_id, 100.00, '2026-12-31')
            )
            fee_struct_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO invoices (student_id, fee_structure_id, total_amount, outstanding_balance, due_date, status) VALUES (%s, %s, %s, %s, %s, %s);",
                (student_ids[0], fee_struct_id, 100.00, 100.00, '2026-12-31', 'unpaid')
            )
            invoice_id = cursor.lastrowid

            conn.commit()
            return {
                'hostel_id': hostel_id,
                'block_id': block_id,
                'floor_id': floor_id,
                'room_id': room_id,
                'bed_ids': bed_ids,
                'student_ids': student_ids,
                'invoice_id': invoice_id
            }

    @staticmethod
    def teardown(conn):
        """Removes all CONC-% test data completely."""
        with conn.cursor() as cursor:
            # Delete payments on test invoices
            cursor.execute("""
                DELETE FROM payments WHERE invoice_id IN (
                    SELECT i.invoice_id FROM invoices i 
                    JOIN students s ON i.student_id = s.student_id 
                    WHERE s.registration_number LIKE 'CONC-REG-%'
                );
            """)
            # Delete invoices
            cursor.execute("""
                DELETE FROM invoices WHERE student_id IN (
                    SELECT student_id FROM students WHERE registration_number LIKE 'CONC-REG-%'
                );
            """)
            # Delete bed allocations
            cursor.execute("""
                DELETE FROM bed_allocations WHERE student_id IN (
                    SELECT student_id FROM students WHERE registration_number LIKE 'CONC-REG-%'
                );
            """)
            # Delete audit logs
            cursor.execute("DELETE FROM audit_logs WHERE entity_type IN ('ALLOCATION', 'PAYMENT', 'BED', 'STUDENT') AND remarks LIKE '%CONC%';")
            # Delete beds
            cursor.execute("DELETE FROM beds WHERE bed_code LIKE 'CONC-BED-%';")
            # Delete rooms
            cursor.execute("DELETE FROM rooms WHERE room_number = 'CONC-101';")
            # Delete floors
            cursor.execute("DELETE FROM floors WHERE block_id IN (SELECT block_id FROM blocks WHERE name = 'CONC-BLOCK');")
            # Delete blocks
            cursor.execute("DELETE FROM blocks WHERE name = 'CONC-BLOCK';")
            # Delete hostels
            cursor.execute("DELETE FROM hostels WHERE name = 'CONC-HOSTEL';")
            # Delete students
            cursor.execute("DELETE FROM students WHERE registration_number LIKE 'CONC-REG-%';")
            conn.commit()


# ============================================================================
# PHASE 7.4.2 — COMPETING BED ALLOCATION (10 STUDENTS -> 1 BED)
# ============================================================================

def _worker_allocate_bed(student_id, bed_id, start_date='2026-09-01'):
    """Worker function executing sp_allocate_bed on an independent PyMySQL connection."""
    conn = get_standalone_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_allocate_bed(%s, %s, %s, @status_code, @message, @alloc_id);",
                (student_id, bed_id, start_date)
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @alloc_id AS allocation_id;")
            res = cursor.fetchone()
            conn.commit()
            return {'student_id': student_id, 'bed_id': bed_id, 'status_code': res['status_code'], 'message': res['message'], 'alloc_id': res['allocation_id']}
    except Exception as e:
        conn.rollback()
        return {'student_id': student_id, 'bed_id': bed_id, 'status_code': 'EXCEPTION', 'message': str(e), 'alloc_id': None}
    finally:
        conn.close()


def test_7_4_2_competing_bed_allocation():
    """
    7.4.2: 10 distinct students concurrently attempt to allocate the exact same vacant bed (CONC-BED-01).
    Invariant: Exactly 1 allocation succeeds; 9 fail with CONFLICT/ERROR. State invariants verified in DB.
    """
    main_conn = get_standalone_connection()
    try:
        fixtures = TestConcurrencyFixtures.setup(main_conn)
        target_bed_id = fixtures['bed_ids'][0]
        student_ids = fixtures['student_ids']

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(_worker_allocate_bed, stu_id, target_bed_id) for stu_id in student_ids]
            for f in as_completed(futures):
                results.append(f.result())

        successes = [r for r in results if r['status_code'] == 'SUCCESS']
        conflicts = [r for r in results if r['status_code'] in ('ERROR', 'EXCEPTION', 'CONFLICT')]

        # Semantic Assertions
        assert len(successes) == 1, f"Expected exactly 1 successful allocation, got {len(successes)}"
        assert len(conflicts) == 9, f"Expected exactly 9 rejected allocations, got {len(conflicts)}"

        winning_student_id = successes[0]['student_id']

        # Deep Database Invariant Verification
        with main_conn.cursor() as cursor:
            # 1. Exactly 1 active allocation record for target_bed_id
            cursor.execute("SELECT COUNT(*) AS cnt FROM bed_allocations WHERE bed_id = %s AND status = 'active';", (target_bed_id,))
            alloc_cnt = cursor.fetchone()['cnt']
            assert alloc_cnt == 1, f"Database has {alloc_cnt} active allocations for bed {target_bed_id}, expected 1"

            # 2. Bed status updated to is_occupied = 1
            cursor.execute("SELECT is_occupied FROM beds WHERE bed_id = %s;", (target_bed_id,))
            is_occ = cursor.fetchone()['is_occupied']
            assert is_occ == 1, "Bed is_occupied flag was not set to 1"

            # 3. Winning student marked is_resident = 1
            cursor.execute("SELECT is_resident FROM students WHERE student_id = %s;", (winning_student_id,))
            is_res = cursor.fetchone()['is_resident']
            assert is_res == 1, "Winning student is_resident flag was not set to 1"

            # 4. Non-winning 9 students remain is_resident = 0
            cursor.execute("SELECT COUNT(*) AS cnt FROM students WHERE student_id IN %s AND is_resident = 0;", (tuple(student_ids),))
            non_res_cnt = cursor.fetchone()['cnt']
            assert non_res_cnt == 9, f"Expected 9 non-resident students, found {non_res_cnt}"

    finally:
        TestConcurrencyFixtures.teardown(main_conn)
        main_conn.close()


# ============================================================================
# PHASE 7.4.3 — COMPETING STUDENT ALLOCATION (1 STUDENT -> 10 BEDS)
# ============================================================================

def test_7_4_3_competing_student_allocation():
    """
    7.4.3: 10 distinct vacant beds concurrently offered to the exact same student (CONC-STU-02).
    Invariant: MySQL active_student_key unique constraint guarantees exactly 1 allocation succeeds.
    """
    main_conn = get_standalone_connection()
    try:
        fixtures = TestConcurrencyFixtures.setup(main_conn)
        target_student_id = fixtures['student_ids'][1]  # CONC-STU-02
        bed_ids = fixtures['bed_ids']

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(_worker_allocate_bed, target_student_id, b_id) for b_id in bed_ids]
            for f in as_completed(futures):
                results.append(f.result())

        successes = [r for r in results if r['status_code'] == 'SUCCESS']
        conflicts = [r for r in results if r['status_code'] in ('ERROR', 'EXCEPTION', 'CONFLICT')]

        assert len(successes) == 1, f"Expected exactly 1 successful allocation for student, got {len(successes)}"
        assert len(conflicts) == 9, f"Expected 9 rejections due to active_student_key, got {len(conflicts)}"

        with main_conn.cursor() as cursor:
            # Verify active_student_key generated constraint enforcement
            cursor.execute("SELECT COUNT(*) AS cnt FROM bed_allocations WHERE student_id = %s AND status = 'active';", (target_student_id,))
            active_cnt = cursor.fetchone()['cnt']
            assert active_cnt == 1, f"Student holds {active_cnt} active allocations, expected exactly 1"
    finally:
        TestConcurrencyFixtures.teardown(main_conn)
        main_conn.close()


# ============================================================================
# PHASE 7.4.4 — CONCURRENT INVOICE PAYMENTS (RACE FOR $100 BALANCE)
# ============================================================================

def _worker_process_payment(invoice_id, amount, payment_method, receipt_number):
    """Worker function executing sp_process_payment on an independent PyMySQL connection."""
    conn = get_standalone_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_process_payment(%s, %s, %s, %s, %s, @status_code, @message, @pay_id);",
                (invoice_id, amount, payment_method, receipt_number, "CONC Payment Test")
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @pay_id AS payment_id;")
            res = cursor.fetchone()
            conn.commit()
            return {'invoice_id': invoice_id, 'receipt_number': receipt_number, 'status_code': res['status_code'], 'message': res['message'], 'payment_id': res['payment_id']}
    except Exception as e:
        conn.rollback()
        return {'invoice_id': invoice_id, 'receipt_number': receipt_number, 'status_code': 'EXCEPTION', 'message': str(e), 'payment_id': None}
    finally:
        conn.close()


def test_7_4_4_concurrent_invoice_payments():
    """
    7.4.4: 5 threads concurrently attempt $100 payment on invoice CONC-INVOICE-01 (outstanding balance = $100).
    Invariant: FOR UPDATE row lock guarantees exactly 1 payment succeeds; outstanding_balance == 0.00; no negative balances.
    """
    main_conn = get_standalone_connection()
    try:
        fixtures = TestConcurrencyFixtures.setup(main_conn)
        invoice_id = fixtures['invoice_id']

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(_worker_process_payment, invoice_id, 100.00, 'UPI', f"CONC-RC-{idx}")
                for idx in range(1, 6)
            ]
            for f in as_completed(futures):
                results.append(f.result())

        successes = [r for r in results if r['status_code'] == 'SUCCESS']
        conflicts = [r for r in results if r['status_code'] in ('ERROR', 'EXCEPTION', 'CONFLICT')]

        assert len(successes) == 1, f"Expected 1 successful payment, got {len(successes)}"
        assert len(conflicts) == 4, f"Expected 4 payment rejections due to zero balance, got {len(conflicts)}"

        with main_conn.cursor() as cursor:
            # Check final invoice outstanding balance
            cursor.execute("SELECT outstanding_balance, status FROM invoices WHERE invoice_id = %s;", (invoice_id,))
            inv = cursor.fetchone()
            assert float(inv['outstanding_balance']) == 0.00, f"Outstanding balance is {inv['outstanding_balance']}, expected 0.00"
            assert inv['status'] == 'paid', f"Invoice status is {inv['status']}, expected 'paid'"

            # Verify total recorded payments sum to exactly $100.00
            cursor.execute("SELECT SUM(amount) AS total_paid FROM payments WHERE invoice_id = %s;", (invoice_id,))
            total_paid = float(cursor.fetchone()['total_paid'])
            assert total_paid == 100.00, f"Total payments sum to {total_paid}, expected 100.00"

            # Invariant: outstanding_balance >= 0
            cursor.execute("SELECT COUNT(*) AS cnt FROM invoices WHERE invoice_id = %s AND outstanding_balance < 0;", (invoice_id,))
            neg_cnt = cursor.fetchone()['cnt']
            assert neg_cnt == 0, "Discovered negative outstanding balance violation!"
    finally:
        TestConcurrencyFixtures.teardown(main_conn)
        main_conn.close()


# ============================================================================
# PHASE 7.4.5 — VACATE VS REALLOCATION RACE CONDITION
# ============================================================================

def _worker_vacate_student(student_id, vacating_date='2026-10-01'):
    """Worker function executing sp_vacate_student."""
    conn = get_standalone_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_vacate_student(%s, %s, %s, %s, %s, %s, @status_code, @message, @vac_id);",
                (student_id, vacating_date, 'End of Term', 'cleared', 0.00, 'CONC Vacate')
            )
            cursor.execute("SELECT @status_code AS status_code, @message AS message, @vac_id AS vacating_id;")
            res = cursor.fetchone()
            conn.commit()
            return {'action': 'vacate', 'status_code': res['status_code'], 'message': res['message']}
    except Exception as e:
        conn.rollback()
        return {'action': 'vacate', 'status_code': 'EXCEPTION', 'message': str(e)}
    finally:
        conn.close()


def test_7_4_5_vacate_reallocate_race():
    """
    7.4.5: Concurrently execute vacating an active resident (CONC-STU-01 on CONC-BED-01) and allocating CONC-BED-01 to CONC-STU-02.
    Invariant: Database must finish in a valid consistent state regardless of transaction execution order.
    """
    main_conn = get_standalone_connection()
    try:
        fixtures = TestConcurrencyFixtures.setup(main_conn)
        target_bed_id = fixtures['bed_ids'][0]
        stu1_id = fixtures['student_ids'][0]
        stu2_id = fixtures['student_ids'][1]

        # Initial Setup: Allocate CONC-BED-01 to STU-01 sequentially
        alloc_res = _worker_allocate_bed(stu1_id, target_bed_id)
        assert alloc_res['status_code'] == 'SUCCESS'

        # Concurrent Execution: Thread A vacates STU-01, Thread B allocates bed to STU-02
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            f_vac = executor.submit(_worker_vacate_student, stu1_id)
            f_alloc = executor.submit(_worker_allocate_bed, stu2_id, target_bed_id)
            results.append(f_vac.result())
            results.append(f_alloc.result())

        # Database State Invariant Assertions (Valid Outcomes)
        with main_conn.cursor() as cursor:
            # 1. No double active allocations on CONC-BED-01
            cursor.execute("SELECT COUNT(*) AS cnt FROM bed_allocations WHERE bed_id = %s AND status = 'active';", (target_bed_id,))
            active_allocs = cursor.fetchone()['cnt']
            assert active_allocs in (0, 1), f"Corrupted active allocation count: {active_allocs}"

            # 2. Bed occupancy flag matches active allocations count exactly
            cursor.execute("SELECT is_occupied FROM beds WHERE bed_id = %s;", (target_bed_id,))
            is_occ = cursor.fetchone()['is_occupied']
            assert is_occ == active_allocs, f"Bed is_occupied ({is_occ}) does not match active allocations count ({active_allocs})"

            # 3. Vacated student STU-01 must not have active allocation
            cursor.execute("SELECT COUNT(*) AS cnt FROM bed_allocations WHERE student_id = %s AND status = 'active';", (stu1_id,))
            stu1_active = cursor.fetchone()['cnt']
            assert stu1_active == 0, "STU-01 still holds active allocation after vacate race!"
    finally:
        TestConcurrencyFixtures.teardown(main_conn)
        main_conn.close()


# ============================================================================
# PHASE 7.4.6 — TRANSACTION ATOMICITY & ROLLBACK INTEGRITY
# ============================================================================

def test_7_4_6_transaction_rollback_integrity():
    """
    7.4.6: Validates that multi-step transactions roll back completely when an intentional exception is triggered.
    """
    conn = get_standalone_connection()
    try:
        fixtures = TestConcurrencyFixtures.setup(conn)
        target_student_id = fixtures['student_ids'][2]
        invalid_bed_id = 9999999  # Non-existent bed ID

        res = _worker_allocate_bed(target_student_id, invalid_bed_id)
        assert res['status_code'] in ('ERROR', 'EXCEPTION')

        # Verify no orphan allocations created
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM bed_allocations WHERE student_id = %s;", (target_student_id,))
            cnt = cursor.fetchone()['cnt']
            assert cnt == 0, f"Discovered {cnt} orphaned allocations after transaction failure!"
    finally:
        TestConcurrencyFixtures.teardown(conn)
        conn.close()


# ============================================================================
# PHASE 7.4.7 — DEADLOCK & LOCK BEHAVIOR ANALYSIS (REPEATED CONTENTION)
# ============================================================================

def test_7_4_7_deadlock_and_lock_behavior():
    """
    7.4.7: Executes repeated contention rounds (5 rounds x 10 threads) to detect deadlocks or lock wait timeouts.
    """
    main_conn = get_standalone_connection()
    total_ops = 0
    success_cnt = 0
    expected_conflicts = 0
    unexpected_failures = 0
    deadlocks = 0

    try:
        fixtures = TestConcurrencyFixtures.setup(main_conn)
        target_bed_id = fixtures['bed_ids'][4]
        student_ids = fixtures['student_ids']

        for round_num in range(1, 6):
            # Clean allocations for target_bed_id before round
            with main_conn.cursor() as cursor:
                cursor.execute("UPDATE beds SET is_occupied = 0 WHERE bed_id = %s;", (target_bed_id,))
                cursor.execute("UPDATE students SET is_resident = 0 WHERE student_id IN %s;", (tuple(student_ids),))
                cursor.execute("DELETE FROM bed_allocations WHERE bed_id = %s;", (target_bed_id,))
                main_conn.commit()

            results = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(_worker_allocate_bed, s_id, target_bed_id) for s_id in student_ids]
                for f in as_completed(futures):
                    results.append(f.result())

            total_ops += len(results)
            for r in results:
                if r['status_code'] == 'SUCCESS':
                    success_cnt += 1
                elif r['status_code'] in ('ERROR', 'CONFLICT'):
                    expected_conflicts += 1
                elif 'Deadlock' in r.get('message', ''):
                    deadlocks += 1
                    unexpected_failures += 1
                else:
                    unexpected_failures += 1

        assert total_ops == 50, f"Expected 50 total operations, got {total_ops}"
        assert success_cnt == 5, f"Expected 5 total successes (1 per round), got {success_cnt}"
        assert expected_conflicts == 45, f"Expected 45 expected conflicts, got {expected_conflicts}"
        assert deadlocks == 0, f"Detected {deadlocks} deadlock errors!"
        assert unexpected_failures == 0, f"Detected {unexpected_failures} unexpected failures!"
    finally:
        TestConcurrencyFixtures.teardown(main_conn)
        main_conn.close()
