# HostelFlow Environment Configuration Guide

## 1. Environments Hierarchy

HostelFlow supports three execution environments:

* **Development** (`FLASK_ENV=development`): Enable debugging, local default secrets, and relaxed cookie checks for simple local workflows.
* **Testing** (`FLASK_ENV=testing`): Set test parameters, isolate data targets, and execute test assertion blocks.
* **Production** (`FLASK_ENV=production`): Enforce strict security settings (rejection of dev secret placeholders, mandatory `DEBUG=False`, and `SESSION_COOKIE_SECURE=True`).

---

## 2. Fail-Fast Start Validation

Upon calling `create_app()`, config validator functions (`validate_config()`) execute checks to ensure environment settings are valid:
1. Verifies that the current environment name is in `{'development', 'testing', 'production'}`.
2. Validates that the database port is a numeric value in range `1 <= DB_PORT <= 65535`.
3. In **Production**:
   - `SECRET_KEY` must be defined.
   - `SECRET_KEY` must not match dev placeholders (`dev-secret-key-hostelflow-local-only`, etc.) or contain `dev-secret`.
   - `DEBUG` must be `False`.
   - `SESSION_COOKIE_SECURE` must be `True`.

If validation fails, application startup terminates immediately with a descriptive `ValueError`.

---

## 3. Diagnostics Fingerprinting

To assist in debugging database connection configurations without exposing credentials, you can retrieve a safe configuration metadata fingerprint:
```python
from app.utils.config_validation import get_config_fingerprint
from flask import current_app

# Safe non-sensitive metadata only
print(get_config_fingerprint(current_app.config))
```
*Credentials, passwords, and secret keys are automatically excluded from the fingerprint.*
