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
    print(f"Sending OTP to {to_email}: {otp_code}")
    if not SMTP_USERNAME or not SMTP_PASSWORD:

        print(f"Development mode: OTP for {to_email} is {otp_code}. Use this to verify.")
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
        print(f"OTP email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(f"Development mode: OTP for {to_email} is {otp_code}. Use this to verify.")
        return True  # Return True to allow login flow to continue
def store_otp(user_id, otp_code, otp_type='login', email=None):
    expires_at = datetime.now() + timedelta(minutes=10)
    print(f"Storing OTP for user {user_id}: {otp_code} type: {otp_type} email: {email}")

    if otp_type == 'registration':
        execute("INSERT INTO otp_register (user_id, otp_code, type, expires_at, email) VALUES (%s, %s, %s, %s, %s)",
                (user_id, otp_code, otp_type, expires_at, email))
    else:  # login
        execute("INSERT INTO otp_register (user_id, otp_code, type, expires_at) VALUES (%s, %s, %s, %s)",
                (user_id, otp_code, otp_type, expires_at))
def verify_otp(user_id, otp_code, otp_type='login', email=None):
    """Verify OTP and delete if valid."""
    print(f"Verifying OTP for user {user_id}: {otp_code} type: {otp_type}")
    otp_row = query_one("SELECT * FROM otp_register WHERE user_id=%s AND otp_code=%s AND type=%s AND expires_at > NOW()",
                        (user_id, otp_code, otp_type))
    if otp_row:
        print(f"OTP verified successfully for user {user_id}")
        # Log the entered OTP only for real users (not temp 0) and only on success
        if user_id != 0 and otp_type == 'login':
            execute("INSERT INTO otp_login (user_id, otp_code, status) VALUES (%s, %s, %s)",
                    (user_id, otp_code, 'success'))
        # For registration, store the entered OTP in otp_register
        if otp_type == 'registration' and email:
            execute("INSERT INTO otp_register (user_id, otp_code, type, email) VALUES (%s, %s, %s, %s)",
                    (user_id, otp_code, otp_type, email))
        # Delete OTP after use
        execute("DELETE FROM otp_register WHERE id=%s", (otp_row['id'],))
        return True
    print(f"OTP verification failed for user {user_id}")
    # Do not log failed OTP attempts to prevent duplication
    return False

def send_and_store_otp(user_id, email, otp_type='login'):
    """Generate, send, and store OTP."""
    otp_code = generate_otp()
    print(f"Generated OTP: {otp_code} for user {user_id} type {otp_type}")
    if send_otp_email(email, otp_code):
        store_otp(user_id, otp_code, otp_type, email if otp_type == 'registration' else None)
        return True
    return False
