"""
Phase 7.6 — HostelFlow Structured Application Logging & Security Audit Utility.

Provides standard-library based logging infrastructure with strict log separation:
- Application events -> logs/application.log
- Security/RBAC events -> logs/security.log
- Server-side error tracebacks -> logs/error.log

Enforces recursive sensitive data scrubbing, request correlation IDs (X-Request-ID),
and structured JSON log formatting.
"""

import os
import sys
import json
import uuid
import logging
import datetime
from flask import g, request, session, has_request_context


LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
os.makedirs(LOGS_DIR, exist_ok=True)

APP_LOG_PATH = os.path.join(LOGS_DIR, 'application.log')
SEC_LOG_PATH = os.path.join(LOGS_DIR, 'security.log')
ERR_LOG_PATH = os.path.join(LOGS_DIR, 'error.log')


SENSITIVE_KEYS = {
    'password', 'passwd', 'secret', 'secret_key', 'session', 'session_cookie',
    'token', 'access_token', 'refresh_token', 'authorization', 'db_password',
    'credit_card', 'card_number', 'cvv'
}


def scrub_sensitive_data(data):
    """
    Recursively scrubs sensitive keys from dictionary and list structures,
    replacing secrets with '[REDACTED]'.
    """
    if isinstance(data, dict):
        scrubbed = {}
        for key, value in data.items():
            if str(key).lower() in SENSITIVE_KEYS:
                scrubbed[key] = '[REDACTED]'
            else:
                scrubbed[key] = scrub_sensitive_data(value)
        return scrubbed
    elif isinstance(data, list):
        return [scrub_sensitive_data(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(scrub_sensitive_data(item) for item in data)
    return data


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects with standard fields."""

    def format(self, record):
        log_payload = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'level': record.levelname,
            'event': getattr(record, 'event', record.getMessage()),
        }

        # Request Correlation Context
        if has_request_context():
            log_payload['request_id'] = getattr(g, 'request_id', None)
            log_payload['route'] = request.path
            log_payload['method'] = request.method
            log_payload['ip'] = request.remote_addr

            if 'user_id' in session:
                log_payload['user_id'] = session.get('user_id')
                roles = session.get('roles', [])
                log_payload['role'] = roles[0] if roles else None

        # Add custom extra context attributes
        if hasattr(record, 'extra_data') and isinstance(record.extra_data, dict):
            clean_extra = scrub_sensitive_data(record.extra_data)
            log_payload.update(clean_extra)

        if record.exc_info:
            log_payload['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def _setup_logger(name, log_file, level=logging.INFO):
    """Factory creating an isolated logger writing to a specific log file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate bubbling to root logger

    # Clear existing handlers if re-initialized
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = StructuredJsonFormatter()

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Initialize Isolated Loggers
app_logger = _setup_logger('hostelflow.app', APP_LOG_PATH, logging.INFO)
sec_logger = _setup_logger('hostelflow.security', SEC_LOG_PATH, logging.WARNING)
err_logger = _setup_logger('hostelflow.error', ERR_LOG_PATH, logging.ERROR)


def get_request_id():
    """Returns the current request correlation ID from Flask g, or generates a new one."""
    if has_request_context():
        if not hasattr(g, 'request_id') or g.request_id is None:
            g.request_id = uuid.uuid4().hex[:12]
        return g.request_id
    return uuid.uuid4().hex[:12]


def log_app_event(event_name, extra=None, level=logging.INFO):
    """Logs an application lifecycle event to application.log."""
    extra_scrubbed = scrub_sensitive_data(extra) if extra else {}
    app_logger.log(level, event_name, extra={'event': event_name, 'extra_data': extra_scrubbed})


def log_security_event(event_name, extra=None, level=logging.WARNING):
    """Logs an authentication or authorization security event to security.log."""
    extra_scrubbed = scrub_sensitive_data(extra) if extra else {}
    sec_logger.log(level, event_name, extra={'event': event_name, 'extra_data': extra_scrubbed})


def log_exception(event_name, exc_info=True, extra=None):
    """Logs a server-side exception traceback to error.log."""
    extra_scrubbed = scrub_sensitive_data(extra) if extra else {}
    err_logger.error(event_name, exc_info=exc_info, extra={'event': event_name, 'extra_data': extra_scrubbed})
