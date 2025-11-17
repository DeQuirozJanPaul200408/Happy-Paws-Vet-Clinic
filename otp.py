import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from db import execute, query_one  # Import DB functions from db.py

# Email configuration (from .env)
SMTP_SERVER = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('EMAIL_PORT', 587))
SMTP_USERNAME = os.getenv('EMAIL_USER')
SMTP_PASSWORD = os.getenv('EMAIL_PASSWORD')
FROM_EMAIL = os.getenv('EMAIL_USER')

def generate_otp(length=6):
    """Generate a random OTP code."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(to_email, otp_code, subject="Your OTP Code"):
    """Send OTP via email."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return True

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    body = f"Your OTP code is: {otp_code}. It expires in 10 minutes."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        return True  # Return True to allow login flow to continue
def store_otp(user_id, otp_code, otp_type='login', email=None):
    expires_at = datetime.now() + timedelta(minutes=10)

    if otp_type == 'registration':
        execute("INSERT INTO otp_register (user_id, otp_code, type, expires_at, email) VALUES (?, ?, ?, ?, ?)",
                (user_id, otp_code, otp_type, expires_at, email))
    else:  # login
        execute("INSERT INTO otp_register (user_id, otp_code, type, expires_at) VALUES (?, ?, ?, ?)",
                (user_id, otp_code, otp_type, expires_at))
def verify_otp(user_id, otp_code, otp_type='login', email=None):
    """Verify OTP and delete if valid."""
    otp_row = query_one("SELECT * FROM otp_register WHERE user_id=? AND otp_code=? AND type=? AND expires_at > datetime('now')",
                        (user_id, otp_code, otp_type))
    if otp_row:
        # Log the entered OTP only for real users (not temp 0) and only on success
        if user_id != 0 and otp_type == 'login':
            execute("INSERT INTO otp_login (user_id, otp_code, status) VALUES (?, ?, ?)",
                    (user_id, otp_code, 'success'))
        # For registration, store the entered OTP in otp_register
        if otp_type == 'registration' and email:
            execute("INSERT INTO otp_register (user_id, otp_code, type, email) VALUES (?, ?, ?, ?)",
                    (user_id, otp_code, otp_type, email))
        # Delete OTP after use
        execute("DELETE FROM otp_register WHERE id=?", (otp_row['id'],))
        return True
    return False

def send_and_store_otp(user_id, email, otp_type='login'):
    """Generate, send, and store OTP."""
    otp_code = generate_otp()
    if send_otp_email(email, otp_code):
        store_otp(user_id, otp_code, otp_type, email if otp_type == 'registration' else None)
        return True
    return False
