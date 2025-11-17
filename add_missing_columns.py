from db import execute

# Add payment_method column to appointment table
execute("ALTER TABLE appointment ADD COLUMN payment_method TEXT;")

# Add payment_status column to appointment table
execute("ALTER TABLE appointment ADD COLUMN payment_status TEXT DEFAULT 'Pending';")

print("Columns added successfully.")
