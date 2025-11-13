from db import execute

# Drop old tables if they exist
try:
    execute("DROP TABLE IF EXISTS otps")
    print("Dropped old otps table")
except Exception as e:
    print(f"Error dropping otps table: {e}")

try:
    execute("DROP TABLE IF EXISTS otp_entries")
    print("Dropped old otp_entries table")
except Exception as e:
    print(f"Error dropping otp_entries table: {e}")

# Create new tables
try:
    execute("""
    CREATE TABLE IF NOT EXISTS otp_register (
        id INT NOT NULL AUTO_INCREMENT,
        user_id INT DEFAULT NULL,
        otp_code VARCHAR(10) DEFAULT NULL,
        type VARCHAR(20) DEFAULT NULL,
        expires_at DATETIME DEFAULT NULL,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """)
    print("Created otp_register table")
except Exception as e:
    print(f"Error creating otp_register table: {e}")

try:
    execute("""
    CREATE TABLE IF NOT EXISTS otp_login (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        otp_code VARCHAR(10) NOT NULL,
        entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) NOT NULL
    );
    """)
    print("Created otp_login table")
except Exception as e:
    print(f"Error creating otp_login table: {e}")

print("Migration completed")
