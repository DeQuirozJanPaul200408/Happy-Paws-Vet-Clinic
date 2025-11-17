from db import execute

# Add reference_number column to appointment table
execute("ALTER TABLE appointment ADD COLUMN reference_number VARCHAR(255);")

print("Reference number column added successfully.")
