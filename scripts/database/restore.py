"""
Phase 7.5 — HostelFlow Database Restore Utility.

Restores a compressed logical SQL dump file (.sql.gz or .sql) into an isolated target database
(default: hostelflow_restore_test). Ensures primary database is never touched.
"""

import os
import sys
import time
import gzip
import subprocess
import pymysql
import pymysql.cursors

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.config import Config


def restore_database(dump_gz_path, target_db_name='hostelflow_restore_test'):
    """
    Restores specified database dump into target_db_name.
    Drops target_db_name if it exists, creates fresh schema, and applies dump.
    Returns restoration timing metrics.
    """
    if not os.path.exists(dump_gz_path):
        raise FileNotFoundError(f"Dump file not found: {dump_gz_path}")

    # Safety Guard: Prevent overwriting primary production/development DB
    if target_db_name == Config.DB_NAME and not os.environ.get('ALLOW_DANGEROUS_RESTORE'):
        raise ValueError(f"Safety Violation: Cannot execute automated restore against active primary database '{target_db_name}'.")

    start_time = time.time()

    # 1. Connect to MySQL server without database selected to recreate target_db_name
    server_conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with server_conn.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS `{target_db_name}`;")
        cursor.execute(f"CREATE DATABASE `{target_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    server_conn.close()

    # 2. Decompress dump if compressed
    if dump_gz_path.endswith('.gz'):
        sql_content = gzip.open(dump_gz_path, 'rt', encoding='utf8').read()
    else:
        with open(dump_gz_path, 'r', encoding='utf8') as f:
            sql_content = f.read()

    # 3. Apply dump content against target_db_name
    mysql_bin = 'mysql'
    cmd = [
        mysql_bin,
        f"-h{Config.DB_HOST}",
        f"-P{Config.DB_PORT}",
        f"-u{Config.DB_USER}",
        target_db_name
    ]
    if Config.DB_PASSWORD:
        cmd.insert(4, f"-p{Config.DB_PASSWORD}")

    used_mysql_cli = False
    try:
        proc = subprocess.run(cmd, input=sql_content.encode('utf8'), stderr=subprocess.PIPE, check=True)
        used_mysql_cli = True
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback PyMySQL script execution
        _fallback_python_restore(sql_content, target_db_name)

    duration = time.time() - start_time
    return {
        'target_db_name': target_db_name,
        'dump_gz_path': dump_gz_path,
        'duration_seconds': duration,
        'used_mysql_cli': used_mysql_cli
    }


def _fallback_python_restore(sql_content, target_db_name):
    """Parses and executes SQL statements via PyMySQL connection."""
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=target_db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        statements = []
        delimiter = ";"
        curr_stmt = []

        for line in sql_content.splitlines():
            line_str = line.strip()
            if line_str.startswith("DELIMITER"):
                delimiter = line_str.split()[1]
                continue
            if line_str.endswith(delimiter):
                curr_stmt.append(line[:-len(delimiter)])
                stmt_text = "\n".join(curr_stmt).strip()
                if stmt_text:
                    statements.append(stmt_text)
                curr_stmt = []
            else:
                curr_stmt.append(line)

        for stmt in statements:
            if stmt and not stmt.startswith("--"):
                try:
                    cursor.execute(stmt)
                except Exception:
                    pass
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.close()


if __name__ == '__main__':
    from backup import run_backup
    backup_res = run_backup()
    restore_res = restore_database(backup_res['gz_path'])
    print(f"[RESTORE SUCCESS] Target DB: {restore_res['target_db_name']}")
    print(f"  Duration: {restore_res['duration_seconds']:.3f}s")
