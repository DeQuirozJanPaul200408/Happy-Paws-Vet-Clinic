import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DATABASE CONNECTION
def get_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'vetclinic.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as err:
        raise


# DATABASE HELPERS
def query_all(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        data = cur.fetchall()
        return data
    finally:
        cur.close()
        conn.close()


def query_one(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return row
    finally:
        cur.close()
        conn.close()


def execute(query, params=()):
    """Execute a write query and return lastrowid (if available)."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        lastrowid = getattr(cur, 'lastrowid', None)
        return lastrowid
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
