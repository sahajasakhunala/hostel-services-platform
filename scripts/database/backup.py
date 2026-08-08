"""
Phase 7.5 — HostelFlow Database Backup Utility.

Performs a logical backup of the HostelFlow database (tables, data, constraints,
indexes, generated columns, triggers, stored procedures, and views) using mysqldump
or fallback PyMySQL structure dump. Computes SHA-256 checksum and records timing metrics.
"""

import os
import sys
import time
import gzip
import hashlib
import subprocess
import pymysql
import pymysql.cursors

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.config import Config


def compute_sha256(filepath):
    """Computes SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def run_backup(output_dir=None, db_name=None):
    """
    Executes logical database backup.
    Returns dictionary with backup metrics and file metadata.
    """
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'backup', 'dumps'))
    os.makedirs(output_dir, exist_ok=True)

    if db_name is None:
        db_name = Config.DB_NAME

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    sql_filename = f"{db_name}_{timestamp}.sql"
    gz_filename = f"{sql_filename}.gz"
    
    sql_path = os.path.join(output_dir, sql_filename)
    gz_path = os.path.join(output_dir, gz_filename)
    checksum_path = os.path.join(output_dir, f"{gz_filename}.sha256")

    start_time = time.time()
    mysqldump_bin = 'mysqldump'
    
    # Try using mysqldump CLI
    cmd = [
        mysqldump_bin,
        f"-h{Config.DB_HOST}",
        f"-P{Config.DB_PORT}",
        f"-u{Config.DB_USER}",
        f"--routines",
        f"--triggers",
        f"--events",
        f"--single-transaction",
        f"--quick",
        db_name
    ]
    if Config.DB_PASSWORD:
        cmd.insert(4, f"-p{Config.DB_PASSWORD}")

    used_mysqldump = False
    try:
        with open(sql_path, 'wb') as out_file:
            proc = subprocess.run(cmd, stdout=out_file, stderr=subprocess.PIPE, check=True)
        used_mysqldump = True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        # Fallback python mysqldump simulation via PyMySQL metadata query
        _fallback_python_dump(sql_path, db_name)

    duration = time.time() - start_time

    # Compress SQL dump to gzip
    with open(sql_path, 'rb') as f_in:
        with gzip.open(gz_path, 'wb') as f_out:
            f_out.writelines(f_in)

    # Clean up uncompressed SQL file
    if os.path.exists(sql_path):
        os.remove(sql_path)

    gz_size = os.path.getsize(gz_path)
    checksum = compute_sha256(gz_path)

    with open(checksum_path, 'w') as f_cs:
        f_cs.write(f"{checksum}  {gz_filename}\n")

    return {
        'db_name': db_name,
        'gz_path': gz_path,
        'checksum_path': checksum_path,
        'checksum': checksum,
        'size_bytes': gz_size,
        'duration_seconds': duration,
        'used_mysqldump': used_mysqldump
    }


def _fallback_python_dump(sql_path, db_name):
    """Generates structural & data dump via PyMySQL connection context."""
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with open(sql_path, 'w', encoding='utf8') as f:
        f.write(f"-- HostelFlow Logical Fallback Dump for database: {db_name}\n")
        f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
        
        with conn.cursor() as cursor:
            # 1. Show Tables
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            
            for t in tables:
                cursor.execute(f"SHOW CREATE TABLE `{t}`;")
                create_stmt = cursor.fetchone()['Create Table']
                f.write(f"-- Table structure for {t}\nDROP TABLE IF EXISTS `{t}`;\n{create_stmt};\n\n")
                
                cursor.execute(f"SELECT * FROM `{t}`;")
                rows = cursor.fetchall()
                if rows:
                    cols = list(rows[0].keys())
                    cols_str = ", ".join([f"`{c}`" for c in cols])
                    f.write(f"INSERT INTO `{t}` ({cols_str}) VALUES\n")
                    vals_list = []
                    for row in rows:
                        vals = []
                        for c in cols:
                            val = row[c]
                            if val is None:
                                vals.append("NULL")
                            elif isinstance(val, (int, float)):
                                vals.append(str(val))
                            else:
                                escaped = str(val).replace("'", "''").replace("\\", "\\\\")
                                vals.append(f"'{escaped}'")
                        vals_list.append(f"({', '.join(vals)})")
                    f.write(",\n".join(vals_list) + ";\n\n")

            # 2. Show Views
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW';")
            views = [list(row.values())[0] for row in cursor.fetchall()]
            for v in views:
                cursor.execute(f"SHOW CREATE VIEW `{v}`;")
                create_v = cursor.fetchone()['Create View']
                f.write(f"-- View structure for {v}\nDROP VIEW IF EXISTS `{v}`;\n{create_v};\n\n")

            # 3. Show Procedures
            cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s;", (db_name,))
            procs = cursor.fetchall()
            for p in procs:
                p_name = p['Name']
                cursor.execute(f"SHOW CREATE PROCEDURE `{p_name}`;")
                create_p = cursor.fetchone()['Create Procedure']
                f.write(f"-- Procedure structure for {p_name}\nDROP PROCEDURE IF EXISTS `{p_name}`;\nDELIMITER ;;\n{create_p};;\nDELIMITER ;\n\n")

            # 4. Show Triggers
            cursor.execute("SHOW TRIGGERS;")
            triggers = cursor.fetchall()
            for tr in triggers:
                tr_name = tr['Trigger']
                cursor.execute(f"SHOW CREATE TRIGGER `{tr_name}`;")
                create_tr = cursor.fetchone()['SQL Original Statement']
                f.write(f"-- Trigger structure for {tr_name}\nDROP TRIGGER IF EXISTS `{tr_name}`;\nDELIMITER ;;\n{create_tr};;\nDELIMITER ;\n\n")

        f.write("SET FOREIGN_KEY_CHECKS=1;\n")
    conn.close()


if __name__ == '__main__':
    res = run_backup()
    print(f"[BACKUP SUCCESS] File: {res['gz_path']}")
    print(f"  Size: {res['size_bytes']} bytes")
    print(f"  Duration: {res['duration_seconds']:.3f}s")
    print(f"  SHA-256: {res['checksum']}")
