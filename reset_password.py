import pandas as pd
import hashlib
import os

def reset_user_password(username, new_password):
    file_path = os.path.join(os.path.dirname(__file__), 'library_db.xlsx')
    try:
        # Read the users sheet
        users_df = pd.read_excel(file_path, sheet_name='users', engine='openpyxl')

        if users_df.empty:
            print("No users found in database")
            return False

        # Find the user
        user_index = users_df[users_df['username'] == username].index
        if user_index.empty:
            print(f"User '{username}' not found")
            return False

        # Hash the new password
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        # Update the password
        users_df.loc[user_index, 'password'] = hashed_password

        # Save back to Excel
        existing_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        existing_sheets['users'] = users_df

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in existing_sheets.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Password for user '{username}' has been reset to '{new_password}'")
        return True

    except Exception as e:
        print(f"Error resetting password: {e}")
        return False

if __name__ == "__main__":
    # Reset password for user 'n' to 'n'
    reset_user_password('n', 'n')
