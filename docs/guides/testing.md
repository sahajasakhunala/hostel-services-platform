# HostelFlow Testing & Verification Reference

HostelFlow implements a comprehensive verification model spanning database triggers, API validations, concurrency stress tests, logging audits, and configuration safety checks.

## 1. Test Suite Commands

Run pytest from the repository root:
```bash
# 1. API Validation & Schema Constraints
.\venv\Scripts\python -m pytest tests/test_validation.py -v

# 2. Concurrency Stress Suite (Locks, Double-Booking, Race Conditions)
.\venv\Scripts\python -m pytest tests/test_concurrency.py -v

# 3. Database Recovery & Restore Verification
.\venv\Scripts\python -m pytest tests/test_backup_restore.py -v

# 4. Structured JSON Logging & Security Event Audits
.\venv\Scripts\python -m pytest tests/test_logging.py -v

# 5. Configuration & Environment Hardening Controls
.\venv\Scripts\python -m pytest tests/test_configuration.py -v
```

---

## 2. Full Platform Regression Suite

To execute the master regression tests verifying routes, health status, and cross-domain reporting APIs:
```bash
.\venv\Scripts\python tests/run_full_verification.py
```
Ensure all verification indicators show `[PASS]` before release tagging.
