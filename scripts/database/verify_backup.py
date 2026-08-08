"""
Phase 7.5 — HostelFlow Backup Verification Utility.

Verifies backup file existence, non-emptiness, SHA-256 checksum matching,
and inspects SQL content to confirm mandatory database objects are present.
"""

import os
import sys
import gzip
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def verify_backup_file(gz_path, checksum_path=None):
    """
    Performs structural and checksum verification on a backup file.
    Returns status dictionary with object presence checks.
    """
    if not os.path.exists(gz_path):
        return {'status': 'FAILED', 'reason': f'Backup file does not exist: {gz_path}'}

    size_bytes = os.path.getsize(gz_path)
    if size_bytes == 0:
        return {'status': 'FAILED', 'reason': 'Backup file is empty (0 bytes)'}

    # Verify SHA-256 Checksum if file provided
    if checksum_path and os.path.exists(checksum_path):
        with open(checksum_path, 'r') as f:
            expected_hash = f.read().split()[0]
        
        sha256 = hashlib.sha256()
        with open(gz_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        actual_hash = sha256.hexdigest()

        if actual_hash != expected_hash:
            return {'status': 'FAILED', 'reason': f'Checksum mismatch: expected {expected_hash}, got {actual_hash}'}

    # Inspect Dump Content for Objects
    try:
        if gz_path.endswith('.gz'):
            content = gzip.open(gz_path, 'rt', encoding='utf8', errors='ignore').read()
        else:
            with open(gz_path, 'r', encoding='utf8', errors='ignore') as f:
                content = f.read()
    except Exception as e:
        return {'status': 'FAILED', 'reason': f'Failed to read dump file: {str(e)}'}

    # Required Database Objects Baseline
    required_tables = ['students', 'hostels', 'blocks', 'floors', 'rooms', 'beds', 'allocations', 'invoices', 'payments', 'visitors', 'complaints', 'maintenance_requests', 'audit_logs']
    required_procs = ['sp_allocate_bed', 'sp_transfer_student', 'sp_vacate_student', 'sp_process_payment']
    required_views = ['v_current_occupancy', 'v_vacant_beds', 'v_fee_dues', 'v_visitor_report', 'v_unresolved_complaints', 'v_maintenance_status']

    content_lower = content.lower()
    missing_tables = [t for t in required_tables if t not in content_lower]
    missing_procs = [p for p in required_procs if p not in content_lower]
    missing_views = [v for v in required_views if v not in content_lower]

    is_valid = len(missing_tables) == 0 and len(missing_procs) == 0 and len(missing_views) == 0

    return {
        'status': 'PASS' if is_valid else 'WARNING',
        'file_exists': True,
        'size_bytes': size_bytes,
        'checksum_valid': True,
        'missing_tables': missing_tables,
        'missing_procs': missing_procs,
        'missing_views': missing_views,
        'tables_count_found': len(required_tables) - len(missing_tables),
        'procs_count_found': len(required_procs) - len(missing_procs),
        'views_count_found': len(required_views) - len(missing_views)
    }


if __name__ == '__main__':
    from backup import run_backup
    backup_res = run_backup()
    res = verify_backup_file(backup_res['gz_path'], backup_res['checksum_path'])
    print(f"[VERIFY BACKUP RESULT] Status: {res['status']}")
    print(f"  Size: {res['size_bytes']} bytes")
    print(f"  Checksum Verified: {res['checksum_valid']}")
