from db import execute

# Add status column to otp_entries table
execute("ALTER TABLE otp_entries ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'success'")
print("Status column added to otp_entries table")
