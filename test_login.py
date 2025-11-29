import hashlib
import pandas as pd
import os

class TestLibraryDatabase:
    def __init__(self, file_path='library_db.xlsx'):
        self.file_path = file_path

    def _hash_password(self, password):
        """Hash password menggunakan SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_sheet(self, sheet_name):
        """Membaca data dari sheet Excel"""
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
        except Exception as e:
            print(f"Error membaca sheet {sheet_name}: {e}")
            return pd.DataFrame()

    def login_admin(self, username, password):
        """Login admin"""
        admin_df = self.get_sheet('admin')
        hashed_password = self._hash_password(password)

        print(f"Input username: {username}")
        print(f"Input password: {password}")
        print(f"Hashed password: {hashed_password}")
        print(f"Admin DataFrame:\n{admin_df}")

        admin = admin_df[(admin_df['username'] == username) &
                        (admin_df['password'] == hashed_password)]

        print(f"Matching admin found: {not admin.empty}")

        if not admin.empty:
            return True, "Login admin berhasil!"
        return False, "Username atau password admin salah"

# Test the login
if __name__ == "__main__":
    db = TestLibraryDatabase()
    success, message = db.login_admin('admin', '12345')
    print(f"Login result: {success}, Message: {message}")
