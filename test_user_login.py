import hashlib
import pandas as pd
import os

class TestUserLogin:
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

    def login_user(self, username, password):
        """Login user biasa"""
        users_df = self.get_sheet('users')

        print(f"Input username: {username}")
        print(f"Input password: {password}")
        print(f"Hashed password: {self._hash_password(password)}")
        print(f"Users DataFrame:\n{users_df}")

        if users_df.empty:
            print("Users DataFrame is empty")
            return False, "Belum ada user terdaftar"

        hashed_password = self._hash_password(password)

        user = users_df[(users_df['username'] == username) &
                       (users_df['password'] == hashed_password)]

        print(f"Matching user found: {not user.empty}")

        if not user.empty:
            return True, "Login berhasil!"
        return False, "Username atau password salah"

# Test the user login
if __name__ == "__main__":
    db = TestUserLogin()
    # Assuming the password is 'n' or something, but we need to guess or ask
    # From the hashed password in the database, let's see if it's 'n'
    # The hashed password is 96cae35ce8a9b0244178bf28e4966c2ce1b8385723a96a6a7ae9e5a14f096e82
    # Let's check if it's 'n'
    test_password = 'n'
    hashed = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"Testing password '{test_password}': {hashed}")
    success, message = db.login_user('n', test_password)
    print(f"Login result: {success}, Message: {message}")
