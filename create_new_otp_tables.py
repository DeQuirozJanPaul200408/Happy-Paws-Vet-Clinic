from db import execute

# Create otp_register table for registration OTPs
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

# Create otp_login table for login OTPs
execute("""
CREATE TABLE IF NOT EXISTS otp_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL
);
""")

print("New OTP tables created: otp_register and otp_login")
