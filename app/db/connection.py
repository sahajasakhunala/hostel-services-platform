import pymysql
import pymysql.cursors
from contextlib import contextmanager
from flask import g, current_app


def get_db_connection():
    """
    Retrieves or creates a PyMySQL connection bound to the current Flask application context (g).
    Returns dictionary-based cursor records for clean service-layer consumption.
    """
    if 'db_conn' not in g:
        g.db_conn = pymysql.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=current_app.config['DB_CONNECT_TIMEOUT'],
            autocommit=False
        )
    return g.db_conn


def close_db_connection(e=None):
    """Closes the PyMySQL database connection at the end of the request context."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database cursor operations.
    Handles automatic commit on success and rollback on exception.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
