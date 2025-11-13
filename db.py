import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DATABASE CONNECTION
def get_db():
    try:
        # Convert port to int if provided
        db_port = os.getenv("DB_PORT")
        if db_port:
            try:
                db_port = int(db_port)
            except ValueError:
                # keep as string and let connector decide
                pass

        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=db_port,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            autocommit=False  # control commits explicitly
        )
        return conn
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        raise


# DATABASE HELPERS
def query_all(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        data = cur.fetchall()
        return data
    finally:
        cur.close()
        conn.close()


def query_one(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
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
        print("Database execute error:", e)
        raise
    finally:
        cur.close()
        conn.close()
