from db import execute

# Insert admin user if not exists
execute("""
INSERT IGNORE INTO user (name, email, password, role)
VALUES (%s, %s, %s, %s)
""", ('Admin', 'vetclinicadmin@gmail.com', 'admin123', 'admin'))

print("Admin user 'vetclinicadmin@gmail.com' with password 'admin123' has been inserted into the database.")
