# HostelFlow Troubleshooting & Support Runbook

## 1. Database Connection Failures
* **Symptom**: Application fails to start or requests return 500 with connection timeout errors.
* **Troubleshooting Steps**:
  1. Verify the MySQL service is active.
     - On Windows (PowerShell): `Get-Service MySQL97`
     - On Linux: `systemctl status mysql`
  2. Inspect the `.env` settings: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`.
  3. Run the configuration validation script to verify parameters:
     ```bash
     .\venv\Scripts\python -c "from app.config import Config; from app.utils.config_validation import validate_config; validate_config(Config)"
     ```

---

## 2. Lock Wait Timeout / Concurrency Issues
* **Symptom**: Stored procedures fail with lock wait timeout exceeded exceptions under heavy load.
* **Troubleshooting Steps**:
  1. Inspect active InnoDB transaction locks:
     ```sql
     SELECT * FROM information_schema.INNODB_TRX;
     ```
  2. Locate blocked transactions and run:
     ```sql
     KILL <thread_id>;
     ```
  3. Ensure that PyMySQL operations do not share connection contexts across concurrent threads.

---

## 3. Investigating Security Exceptions via Correlation IDs
* **Symptom**: Users report 403 Forbidden or 500 error responses without diagnostic messages.
* **Troubleshooting Steps**:
  1. Extract the `X-Request-ID` correlation ID from the client's HTTP response header (e.g. `8f3a8b92d1c5`).
  2. Search for the correlation ID in the log files to trace the exact events leading to the error:
     ```bash
     # Search security logs
     Select-String -Path logs/security.log -Pattern "8f3a8b92d1c5"

     # Search error tracebacks
     Select-String -Path logs/error.log -Pattern "8f3a8b92d1c5"
     ```
