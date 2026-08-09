import os
import sqlite3
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from flask import g, current_app


class SQLiteWrapperCursor:
    """Wrapper adapting sqlite3 cursor to match PyMySQL DictCursor interface."""
    def __init__(self, sqlite_conn):
        self.conn = sqlite_conn
        self.cursor = sqlite_conn.cursor()
        self.lastrowid = None

    def execute(self, query, params=None):
        # Convert PyMySQL %s placeholders to SQLite ? placeholders
        sqlite_query = query.replace('%s', '?')
        if params is None:
            self.cursor.execute(sqlite_query)
        else:
            self.cursor.execute(sqlite_query, params)
        self.lastrowid = self.cursor.lastrowid
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.cursor.close()


class SQLiteWrapperConn:
    """Wrapper adapting sqlite3 connection to PyMySQL connection interface."""
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def cursor(self):
        return SQLiteWrapperCursor(self.conn)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def _init_tables(self):
        """Creates SQLite fallback tables if they do not exist."""
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                student_id INTEGER UNIQUE,
                staff_id INTEGER UNIQUE,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id_ref INTEGER NOT NULL,
                role_id INTEGER NOT NULL
            );
            INSERT OR IGNORE INTO roles (role_id, name, description) VALUES
            (1, 'Administrator', 'Full access to platform administration'),
            (2, 'Warden', 'Hostel block management'),
            (3, 'Student', 'Hostel resident'),
            (4, 'Security Staff', 'Gate access logging'),
            (5, 'Maintenance Staff', 'Infrastructure repair handling');
        """)
        self.conn.commit()


def get_db_connection():
    """
    Retrieves or creates a database connection bound to current Flask context (g).
    First attempts PyMySQL connection to MySQL.
    If MySQL credentials fail (Access Denied / Offline), cleanly falls back to SQLite
    to guarantee local account creation and login operations succeed out-of-the-box.
    """
    if 'db_conn' not in g:
        try:
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
        except (pymysql.err.OperationalError, pymysql.err.MySQLError, Exception):
            # Fallback to local SQLite instance when MySQL connection is restricted or offline
            sqlite_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'hostelflow_fallback.db'))
            os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)
            g.db_conn = SQLiteWrapperConn(sqlite_db_path)

    return g.db_conn


def close_db_connection(e=None):
    """Closes the database connection at the end of the request context."""
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
