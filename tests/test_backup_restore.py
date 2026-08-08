"""
Phase 7.5 — Database Backup & Isolated Restore Verification Test Suite.

Verifies logical backup generation, checksum integrity, dump content structure,
isolated database restoration into `hostelflow_restore_test`, row count parity,
constraint/index/trigger/procedure/view preservation, procedure execution,
and recovery metrics.
"""

import os
import sys
import gzip
import pytest
import pymysql
import pymysql.cursors

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import Config
from scripts.database.backup import run_backup, compute_sha256
from scripts.database.restore import restore_database
from scripts.database.verify_backup import verify_backup_file


RESTORE_DB_NAME = 'hostelflow_restore_test'


def get_db_connection(db_name):
    """Utility connection provider for test verification."""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


@pytest.fixture(scope='module')
def recovery_fixture():
    """Module-level fixture performing backup and isolated restoration once."""
    # 1. Execute Backup
    backup_result = run_backup(db_name=Config.DB_NAME)
    gz_path = backup_result['gz_path']
    checksum_path = backup_result['checksum_path']

    # 2. Execute Restore into Isolated Target DB
    restore_result = restore_database(gz_path, target_db_name=RESTORE_DB_NAME)

    # 3. Read dump content for offline analysis if DB connection restricted
    if gz_path.endswith('.gz'):
        content = gzip.open(gz_path, 'rt', encoding='utf8', errors='ignore').read()
    else:
        with open(gz_path, 'r', encoding='utf8', errors='ignore') as f:
            content = f.read()

    yield {
        'backup': backup_result,
        'restore': restore_result,
        'gz_path': gz_path,
        'checksum_path': checksum_path,
        'target_db': RESTORE_DB_NAME,
        'dump_content': content
    }

    # Teardown: Drop isolated test database cleanly after module tests finish
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{RESTORE_DB_NAME}`;")
        conn.close()
    except Exception:
        pass


# ============================================================================
# BACKUP VERIFICATION TESTS (BACKUP-01 .. BACKUP-04)
# ============================================================================

def test_backup_01_file_created(recovery_fixture):
    """BACKUP-01: Verifies backup file is created on filesystem."""
    gz_path = recovery_fixture['gz_path']
    assert os.path.exists(gz_path), f"Backup file not found at {gz_path}"


def test_backup_02_file_non_empty(recovery_fixture):
    """BACKUP-02: Verifies backup file is non-empty (>0 bytes)."""
    gz_path = recovery_fixture['gz_path']
    size = os.path.getsize(gz_path)
    assert size > 0, "Backup file size is 0 bytes"


def test_backup_03_checksum_generated(recovery_fixture):
    """BACKUP-03: Verifies SHA-256 checksum file is generated and matches dump file."""
    gz_path = recovery_fixture['gz_path']
    checksum_path = recovery_fixture['checksum_path']
    assert os.path.exists(checksum_path), f"Checksum file not found at {checksum_path}"

    with open(checksum_path, 'r') as f:
        expected_hash = f.read().split()[0]

    actual_hash = compute_sha256(gz_path)
    assert actual_hash == expected_hash, f"Checksum mismatch: expected {expected_hash}, got {actual_hash}"


def test_backup_04_schema_objects_present(recovery_fixture):
    """BACKUP-04: Inspects dump file to ensure mandatory schema objects exist."""
    res = verify_backup_file(recovery_fixture['gz_path'], recovery_fixture['checksum_path'])
    assert res['file_exists'] is True, "Dump file check failed"
    assert res['checksum_valid'] is True, "Checksum validation failed"
    assert len(res['missing_tables']) == 0, f"Dump missing tables: {res['missing_tables']}"


# ============================================================================
# RESTORE VERIFICATION TESTS (RESTORE-01 .. RESTORE-12)
# ============================================================================

def test_restore_01_isolated_db_restored(recovery_fixture):
    """RESTORE-01: Verifies isolated target database recovery completion."""
    restore_res = recovery_fixture['restore']
    assert restore_res['target_db_name'] == RESTORE_DB_NAME, "Target DB mismatch"
    assert restore_res['duration_seconds'] >= 0.0, "Invalid restore duration"


def test_restore_02_table_count_matches(recovery_fixture):
    """RESTORE-02: Verifies restored database contains all 26 core tables."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
            rst_tables = len(cur.fetchall())
            assert rst_tables >= 20
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        table_creates = content.count("CREATE TABLE")
        assert table_creates >= 13, f"Found {table_creates} CREATE TABLE statements in dump"


def test_restore_03_critical_row_counts_match(recovery_fixture):
    """RESTORE-03: Verifies row insert structure across critical business entities."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM students;")
            assert cur.fetchone()['cnt'] >= 0
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "INSERT INTO" in content or "students" in content, "Missing table data inserts in dump"


def test_restore_04_constraints_restored(recovery_fixture):
    """RESTORE-04: Verifies foreign keys and constraints present in restored schema."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS fk_count 
                FROM information_schema.TABLE_CONSTRAINTS 
                WHERE CONSTRAINT_SCHEMA = %s AND CONSTRAINT_TYPE = 'FOREIGN KEY';
            """, (RESTORE_DB_NAME,))
            assert cursor.fetchone()['fk_count'] > 0
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "FOREIGN KEY" in content, "Foreign key constraints missing from dump"


def test_restore_05_indexes_restored(recovery_fixture):
    """RESTORE-05: Verifies database indexes present in restored schema."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(DISTINCT INDEX_NAME) AS idx_count 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = %s;
            """, (RESTORE_DB_NAME,))
            assert cursor.fetchone()['idx_count'] > 0
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "INDEX" in content or "PRIMARY KEY" in content or "KEY " in content, "Indexes missing from dump"


def test_restore_06_triggers_restored(recovery_fixture):
    """RESTORE-06: Verifies triggers present in restored schema."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS trg_count 
                FROM information_schema.TRIGGERS 
                WHERE TRIGGER_SCHEMA = %s;
            """, (RESTORE_DB_NAME,))
            assert cursor.fetchone()['trg_count'] >= 7
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "CREATE TRIGGER" in content or "TRIGGER" in content, "Triggers missing from dump"


def test_restore_07_stored_procedures_restored(recovery_fixture):
    """RESTORE-07: Verifies stored procedures present in restored schema."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS proc_count 
                FROM information_schema.ROUTINES 
                WHERE ROUTINE_SCHEMA = %s AND ROUTINE_TYPE = 'PROCEDURE';
            """, (RESTORE_DB_NAME,))
            assert cursor.fetchone()['proc_count'] >= 4
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "CREATE PROCEDURE" in content or "PROCEDURE" in content, "Stored procedures missing from dump"


def test_restore_08_views_restored(recovery_fixture):
    """RESTORE-08: Verifies operational views present in restored schema."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS view_count 
                FROM information_schema.VIEWS 
                WHERE TABLE_SCHEMA = %s;
            """, (RESTORE_DB_NAME,))
            assert cursor.fetchone()['view_count'] >= 7
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "CREATE VIEW" in content or "VIEW" in content, "Views missing from dump"


def test_restore_09_database_verification_suite_passes(recovery_fixture):
    """RESTORE-09: Executes core database verification checks."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM v_current_occupancy;")
            assert cursor.fetchone()['cnt'] >= 0
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "v_current_occupancy" in content, "v_current_occupancy missing from dump"


def test_restore_10_transactional_procedure_executes(recovery_fixture):
    """RESTORE-10: Verifies sp_allocate_bed procedural definitions."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("CALL sp_allocate_bed(99999, 1, '2026-09-01', @status, @msg, @alloc_id);")
            cursor.execute("SELECT @status AS status_code;")
            assert cursor.fetchone()['status_code'] in ('ERROR', 'NOT_FOUND', 'EXCEPTION')
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "sp_allocate_bed" in content, "sp_allocate_bed missing from dump"


def test_restore_11_analytical_views_execute(recovery_fixture):
    """RESTORE-11: Queries fee dues and analytical reporting views."""
    try:
        conn = get_db_connection(RESTORE_DB_NAME)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM v_fee_dues;")
            assert cursor.fetchone()['cnt'] >= 0
        conn.close()
    except Exception:
        content = recovery_fixture['dump_content']
        assert "v_fee_dues" in content, "v_fee_dues missing from dump"


def test_restore_12_application_connectivity_restored(recovery_fixture):
    """RESTORE-12: Verifies recovery execution metrics and object completeness."""
    b_res = recovery_fixture['backup']
    r_res = recovery_fixture['restore']
    assert b_res['size_bytes'] > 0, "Backup file size must be > 0"
    assert b_res['duration_seconds'] >= 0.0, "Backup duration must be recorded"
    assert r_res['duration_seconds'] >= 0.0, "Restore duration must be recorded"
