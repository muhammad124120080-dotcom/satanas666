import hashlib
import pandas as pd
import os

# Test the admin password hashing
password = '12345'
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f"Password: {password}")
print(f"Hashed: {hashed}")

# Check if database exists and show admin data
if os.path.exists('library_db.xlsx'):
    try:
        admin_df = pd.read_excel('library_db.xlsx', sheet_name='admin', engine='openpyxl')
        print("\nAdmin data in database:")
        print(admin_df)
    except Exception as e:
        print(f"Error reading database: {e}")
else:
    print("Database file does not exist")
