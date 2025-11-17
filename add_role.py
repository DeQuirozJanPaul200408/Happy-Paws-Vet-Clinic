from db import execute

# Add role column to user table
execute("ALTER TABLE user ADD COLUMN role TEXT DEFAULT 'user';")
print("Role column added to user table.")
