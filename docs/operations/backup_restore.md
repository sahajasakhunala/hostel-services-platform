# HostelFlow Database Recovery Runbook

## 1. Logical Database Backup
Run the backup script to generate a compressed SQL dump:
```bash
# Using Python runner:
.\venv\Scripts\python scripts/database/backup.py

# Using Bash script:
./database/backup/backup_database.sh
```
This utility creates:
1. A compressed SQL dump: `database/backup/dumps/hostelflow_db_YYYYMMDD_HHMMSS.sql.gz`.
2. A SHA-256 signature file: `database/backup/dumps/hostelflow_db_YYYYMMDD_HHMMSS.sql.gz.sha256`.

---

## 2. Checksum Verification
Validate the integrity of your backup file:
```bash
# Python:
.\venv\Scripts\python scripts/database/verify_backup.py

# Bash:
./database/backup/verify_backup.sh database/backup/dumps/your_dump.sql.gz
```
The script confirms that the checksum matches and verifies that mandatory tables, views, stored procedures, and triggers are present.

---

## 3. Isolated Database Restore
To prevent accidental data loss, **never** restore directly over your active database. Restore into an isolated database:
```bash
# Python:
.\venv\Scripts\python scripts/database/restore.py

# Bash:
./database/backup/restore_database.sh database/backup/dumps/your_dump.sql.gz hostelflow_restore_test
```
Verify the restored schema counts (26 tables, 7 views, 4 stored procedures, 7 triggers) before completing recovery.
