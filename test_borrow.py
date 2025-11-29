import pandas as pd
import os
from datetime import datetime

class TestLibraryDatabase:
    def __init__(self, file_path='library_db.xlsx'):
        self.file_path = file_path

    def get_sheet(self, sheet_name):
        """Membaca data dari sheet Excel"""
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
        except Exception as e:
            print(f"Error membaca sheet {sheet_name}: {e}")
            return pd.DataFrame()

    def save_sheet(self, sheet_name, data):
        """Menyimpan data ke sheet Excel"""
        try:
            # Baca semua sheet yang ada
            existing_sheets = pd.read_excel(self.file_path, sheet_name=None, engine='openpyxl')

            # Update sheet yang diinginkan
            existing_sheets[sheet_name] = data

            # Simpan kembali semua sheet
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                for sheet_name_val, sheet_data in existing_sheets.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name_val, index=False)
            return True
        except Exception as e:
            print(f"Error menyimpan data: {e}")
            return False

class TestBookManager:
    def __init__(self, db):
        self.db = db

    def borrow_book(self, username, book_id):
        """Meminjam buku"""
        print(f"Attempting to borrow book {book_id} for user {username}")

        books_df = self.db.get_sheet('books')
        transactions_df = self.db.get_sheet('transactions')

        print(f"Books DataFrame shape: {books_df.shape}")
        print(f"Transactions DataFrame shape: {transactions_df.shape}")

        # Cek ketersediaan buku
        book = books_df[books_df['book_id'] == book_id]
        if book.empty:
            return False, "Buku tidak ditemukan"

        if not book.iloc[0]['available']:
            return False, "Buku sedang dipinjam"

        print(f"Book found: {book.iloc[0]['title']}, available: {book.iloc[0]['available']}")

        # Update status buku
        books_df.loc[books_df['book_id'] == book_id, 'available'] = False
        print("Book availability updated to False")

        # Generate transaction_id
        if transactions_df.empty:
            new_transaction_id = 1
        else:
            new_transaction_id = transactions_df['transaction_id'].max() + 1

        print(f"New transaction ID: {new_transaction_id}")

        # Hitung tanggal jatuh tempo (14 hari dari sekarang)
        borrow_date = datetime.now()
        due_date = borrow_date + pd.DateOffset(days=14)

        # Tambah transaksi
        new_transaction = pd.DataFrame({
            'transaction_id': [new_transaction_id],
            'username': [username],
            'book_id': [book_id],
            'book_title': [book.iloc[0]['title']],
            'borrow_date': [borrow_date.strftime("%Y-%m-%d")],
            'due_date': [due_date.strftime("%Y-%m-%d")],
            'return_date': [""],
            'status': ['borrowed'],
            'fine': [0]
        })

        print(f"New transaction DataFrame:\n{new_transaction}")

        transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
        print(f"Transactions DataFrame after concat shape: {transactions_df.shape}")

        # Simpan perubahan
        books_saved = self.db.save_sheet('books', books_df)
        transactions_saved = self.db.save_sheet('transactions', transactions_df)

        print(f"Books saved: {books_saved}")
        print(f"Transactions saved: {transactions_saved}")

        if books_saved and transactions_saved:
            return True, f"Buku '{book.iloc[0]['title']}' berhasil dipinjam. Jatuh tempo: {due_date.strftime('%Y-%m-%d')}"
        else:
            return False, "Gagal memproses peminjaman"

# Test the borrowing functionality
if __name__ == "__main__":
    db = TestLibraryDatabase()
    book_manager = TestBookManager(db)

    # Check initial state
    print("=== Initial State ===")
    transactions_df = db.get_sheet('transactions')
    print(f"Initial transactions: {transactions_df.shape}")
    print(transactions_df)

    # Try to borrow a book
    print("\n=== Borrowing Book ===")
    success, message = book_manager.borrow_book('testuser', 1)
    print(f"Result: {success}, Message: {message}")

    # Check final state
    print("\n=== Final State ===")
    transactions_df = db.get_sheet('transactions')
    print(f"Final transactions: {transactions_df.shape}")
    print(transactions_df)
