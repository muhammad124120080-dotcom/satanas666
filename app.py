import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import hashlib
import os
from datetime import datetime

# ===============================
# CLASS: LIBRARY DATABASE MANAGER
# ===============================
class LibraryDatabase:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'library_db.xlsx')
        self.file_path = file_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Membuat database Excel otomatis jika belum ada"""
        if not os.path.exists(self.file_path):
            # 1. DATA ADMIN (default)
            admin_data = pd.DataFrame({
                'username': ['admin'],
                'password': [self._hash_password('12345')],
                'created_at': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })

            # 2. DATA USER (struktur kosong)
            user_data = pd.DataFrame(columns=[
                'username', 'password', 'email', 'created_at'
            ])

            # 3. DATA BUKU (sample data)
            book_data = pd.DataFrame({
                'book_id': [1, 2, 3, 4, 5],
                'title': [
                    'Python Programming for Beginners',
                    'Data Science Handbook',
                    'Machine Learning Basics',
                    'Web Development with Streamlit',
                    'Database System Concepts'
                ],
                'author': [
                    'John Smith',
                    'Jane Doe',
                    'Robert Johnson',
                    'Sarah Wilson',
                    'Michael Brown'
                ],
                'year': [2023, 2022, 2023, 2024, 2021],
                'category': [
                    'Programming',
                    'Data Science',
                    'Artificial Intelligence',
                    'Web Development',
                    'Database'
                ],
                'isbn': [
                    '978-1234567890',
                    '978-0987654321',
                    '978-1122334455',
                    '978-5566778899',
                    '978-9988776655'
                ],
                'available': [True, True, True, True, True],
                'added_date': [
                    '2024-01-15', '2024-01-10', '2024-01-20',
                    '2024-01-25', '2024-01-05'
                ]
            })

            # 4. DATA TRANSAKSI (struktur kosong)
            transaction_data = pd.DataFrame(columns=[
                'transaction_id', 'username', 'book_id', 'book_title',
                'borrow_date', 'due_date', 'return_date', 'status', 'fine'
            ])

            # Simpan semua sheet ke Excel
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                admin_data.to_excel(writer, sheet_name='admin', index=False)
                user_data.to_excel(writer, sheet_name='users', index=False)
                book_data.to_excel(writer, sheet_name='books', index=False)
                transaction_data.to_excel(writer, sheet_name='transactions', index=False)
    
    def _hash_password(self, password):
        """Hash password menggunakan SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_sheet(self, sheet_name):
        """Membaca data dari sheet Excel"""
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
        except Exception as e:
            st.error(f"Error membaca sheet {sheet_name}: {e}")
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
            st.error(f"Error menyimpan data: {e}")
            return False

# ===============================
# CLASS: USER MANAGEMENT
# ===============================
class UserManager:
    def __init__(self, db):
        self.db = db
    
    def register_user(self, username, password, email):
        """Registrasi user baru"""
        users_df = self.db.get_sheet('users')
        
        # Validasi input
        if not username or not password or not email:
            return False, "Semua field harus diisi"
        
        # Cek jika username sudah ada
        if not users_df.empty and username in users_df['username'].values:
            return False, "Username sudah terdaftar"
        
        # Tambah user baru
        new_user = pd.DataFrame({
            'username': [username],
            'password': [self.db._hash_password(password)],
            'email': [email],
            'created_at': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        
        if self.db.save_sheet('users', users_df):
            return True, "Registrasi berhasil! Silakan login."
        else:
            return False, "Gagal menyimpan data user"
    
    def login_user(self, username, password):
        """Login user biasa"""
        users_df = self.db.get_sheet('users')
        
        if users_df.empty:
            return False, "Belum ada user terdaftar"
        
        hashed_password = self.db._hash_password(password)
        
        user = users_df[(users_df['username'] == username) & 
                       (users_df['password'] == hashed_password)]
        
        if not user.empty:
            return True, "Login berhasil!"
        return False, "Username atau password salah"
    
    def login_admin(self, username, password):
        """Login admin"""
        admin_df = self.db.get_sheet('admin')
        hashed_password = self.db._hash_password(password)

        admin = admin_df[(admin_df['username'] == username) &
                        (admin_df['password'] == hashed_password)]

        if not admin.empty:
            return True, "Login admin berhasil!"
        return False, "Username atau password admin salah"

# ===============================
# CLASS: BOOK MANAGEMENT
# ===============================
class BookManager:
    def __init__(self, db):
        self.db = db
    
    def get_all_books(self):
        """Mendapatkan semua buku"""
        return self.db.get_sheet('books')
    
    def get_available_books(self):
        """Mendapatkan buku yang tersedia"""
        books_df = self.db.get_sheet('books')
        if books_df.empty:
            return books_df
        return books_df[books_df['available'] == True]
    
    def add_book(self, book_data):
        """Menambah buku baru"""
        books_df = self.db.get_sheet('books')
        
        # Generate book_id
        if books_df.empty:
            new_id = 1
        else:
            new_id = books_df['book_id'].max() + 1
        
        book_data['book_id'] = new_id
        book_data['available'] = True
        book_data['added_date'] = datetime.now().strftime("%Y-%m-%d")
        
        new_book = pd.DataFrame([book_data])
        books_df = pd.concat([books_df, new_book], ignore_index=True)
        
        if self.db.save_sheet('books', books_df):
            return True, f"Buku berhasil ditambahkan dengan ID: {new_id}"
        else:
            return False, "Gagal menambahkan buku"
    
    def borrow_book(self, username, book_id):
        """Meminjam buku"""
        books_df = self.db.get_sheet('books')
        transactions_df = self.db.get_sheet('transactions')

        # Cek ketersediaan buku
        book = books_df[books_df['book_id'] == book_id]
        if book.empty:
            return False, "Buku tidak ditemukan"

        if not book.iloc[0]['available']:
            return False, "Buku sedang dipinjam"

        # Update status buku
        books_df.loc[books_df['book_id'] == book_id, 'available'] = False

        # Generate transaction_id
        if transactions_df.empty:
            new_transaction_id = 1
        else:
            new_transaction_id = transactions_df['transaction_id'].max() + 1

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

        transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)

        # Simpan perubahan
        if (self.db.save_sheet('books', books_df) and
            self.db.save_sheet('transactions', transactions_df)):
            return True, f"Buku '{book.iloc[0]['title']}' berhasil dipinjam. Jatuh tempo: {due_date.strftime('%Y-%m-%d')}"
        else:
            return False, "Gagal memproses peminjaman"
    
    def return_book(self, transaction_id):
        """Mengembalikan buku"""
        print(f"DEBUG: return_book called with transaction_id={transaction_id}")

        transactions_df = self.db.get_sheet('transactions')
        books_df = self.db.get_sheet('books')

        print(f"DEBUG: Transactions DataFrame shape: {transactions_df.shape}")
        print(f"DEBUG: Books DataFrame shape: {books_df.shape}")

        # Cek transaksi
        transaction = transactions_df[transactions_df['transaction_id'] == transaction_id]
        if transaction.empty:
            print("DEBUG: Transaction not found")
            return False, "Transaksi tidak ditemukan"

        if transaction.iloc[0]['status'] == 'returned':
            print("DEBUG: Book already returned")
            return False, "Buku sudah dikembalikan"

        book_id = transaction.iloc[0]['book_id']
        print(f"DEBUG: Book ID to return: {book_id}")

        # Update status buku
        books_df.loc[books_df['book_id'] == book_id, 'available'] = True
        print("DEBUG: Book availability updated to True")

        # Update transaksi
        return_date = datetime.now()
        transactions_df.loc[transactions_df['transaction_id'] == transaction_id, 'return_date'] = return_date.strftime("%Y-%m-%d")
        transactions_df.loc[transactions_df['transaction_id'] == transaction_id, 'status'] = 'returned'
        print(f"DEBUG: Transaction updated with return_date: {return_date.strftime('%Y-%m-%d')}")

        # Hitung denda jika terlambat
        due_date = pd.to_datetime(transaction.iloc[0]['due_date'])
        if return_date > due_date:
            days_late = (return_date - due_date).days
            fine = days_late * 5000  # Denda Rp 5000/hari
            transactions_df.loc[transactions_df['transaction_id'] == transaction_id, 'fine'] = fine
            print(f"DEBUG: Fine calculated: {fine}")
        else:
            print("DEBUG: No fine")

        # Simpan perubahan
        books_saved = self.db.save_sheet('books', books_df)
        transactions_saved = self.db.save_sheet('transactions', transactions_df)

        print(f"DEBUG: Books saved: {books_saved}")
        print(f"DEBUG: Transactions saved: {transactions_saved}")

        if books_saved and transactions_saved:
            print(f"DEBUG: Return successful for transaction {transaction_id}")
            return True, "Buku berhasil dikembalikan"
        else:
            print(f"DEBUG: Return failed for transaction {transaction_id}")
            return False, "Gagal memproses pengembalian"

# ===============================
# CLASS: LIBRARY ANALYTICS
# ===============================
class LibraryAnalytics:
    def __init__(self, db):
        self.db = db
    
    def get_borrowing_stats(self):
        """Analisis statistik peminjaman"""
        transactions_df = self.db.get_sheet('transactions')
        books_df = self.db.get_sheet('books')
        
        if transactions_df.empty:
            return None
        
        # Analisis menggunakan numpy
        borrow_counts = transactions_df['book_id'].value_counts()
        
        stats_result = {
            'total_transactions': len(transactions_df),
            'active_borrows': len(transactions_df[transactions_df['status'] == 'borrowed']),
            'most_borrowed_book': borrow_counts.idxmax() if not borrow_counts.empty else None,
            'borrow_frequency': dict(borrow_counts),
            'mean_borrows': np.mean(list(borrow_counts)) if not borrow_counts.empty else 0,
            'std_borrows': np.std(list(borrow_counts)) if not borrow_counts.empty else 0
        }
        
        return stats_result
    
    def plot_borrowing_trend(self):
        """Visualisasi trend peminjaman"""
        transactions_df = self.db.get_sheet('transactions')
        
        if transactions_df.empty:
            st.warning("Tidak ada data transaksi untuk dianalisis")
            return
        
        # Konversi tanggal dan analisis
        transactions_df['borrow_date'] = pd.to_datetime(transactions_df['borrow_date'])
        monthly_borrows = transactions_df.groupby(transactions_df['borrow_date'].dt.to_period('M')).size()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        monthly_borrows.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Trend Peminjaman Bulanan')
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Jumlah Peminjaman')
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    def plot_category_distribution(self):
        """Visualisasi distribusi kategori buku"""
        books_df = self.db.get_sheet('books')
        
        if books_df.empty:
            st.warning("Tidak ada data buku untuk dianalisis")
            return
        
        category_counts = books_df['category'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        category_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title('Distribusi Kategori Buku')
        ax.set_ylabel('')
        st.pyplot(fig)

# ===============================
# INISIALISASI SISTEM
# ===============================
db = LibraryDatabase()
user_manager = UserManager(db)
book_manager = BookManager(db)
analytics = LibraryAnalytics(db)

# ===============================
# FUNGSI STREAMLIT - AUTH PAGES
# ===============================
def show_login_page():
    """Halaman login user"""
    st.header("🔐 Login User")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            success, message = user_manager.login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = False
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def show_register_page():
    """Halaman registrasi user"""
    st.header("📝 Register User")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Password tidak cocok")
            elif len(password) < 6:
                st.error("Password minimal 6 karakter")
            else:
                success, message = user_manager.register_user(username, password, email)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def show_admin_login_page():
    """Halaman login admin"""
    st.header("👑 Login Admin")
    
    with st.form("admin_login_form"):
        username = st.text_input("Username Admin")
        password = st.text_input("Password Admin", type="password")
        submit = st.form_submit_button("Login sebagai Admin")
        
        if submit:
            success, message = user_manager.login_admin(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = True
                st.success(message)
                st.rerun()
            else:
                st.error(message)

# ===============================
# FUNGSI STREAMLIT - USER DASHBOARD
# ===============================
def show_user_dashboard():
    """Dashboard untuk user biasa"""
    st.header(f"📚 Selamat datang, {st.session_state.username}!")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 Semua Buku",
        "🔍 Buku Tersedia",
        "📚 Pinjam Buku",
        "🔄 Kembalikan Buku",
        "📋 Riwayat Saya"
    ])
    
    with tab1:
        st.subheader("📖 Katalog Semua Buku")
        books_df = book_manager.get_all_books()
        if not books_df.empty:
            # Tampilkan dengan format yang lebih rapi
            for _, book in books_df.iterrows():
                status = "✅ Tersedia" if book['available'] else "❌ Dipinjam"
                st.write(f"**{book['title']}**")
                st.write(f"Penulis: {book['author']} | Tahun: {book['year']} | Kategori: {book['category']} | Status: {status}")
                st.divider()
        else:
            st.info("Belum ada buku dalam sistem")
    
    with tab2:
        st.subheader("🔍 Buku yang Tersedia")
        available_books = book_manager.get_available_books()
        if not available_books.empty:
            st.dataframe(
                available_books[['title', 'author', 'year', 'category']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tidak ada buku yang tersedia saat ini")
    
    with tab3:
        st.subheader("📚 Pinjam Buku")
        available_books = book_manager.get_available_books()
        
        if not available_books.empty:
            # Buat pilihan buku dengan format yang informatif
            book_options = {
                f"{row['title']} oleh {row['author']} (ID: {row['book_id']})": row['book_id'] 
                for _, row in available_books.iterrows()
            }
            
            selected_book = st.selectbox(
                "Pilih buku untuk dipinjam:", 
                list(book_options.keys())
            )
            
            if st.button("📥 Pinjam Buku", type="primary"):
                book_id = book_options[selected_book]
                success, message = book_manager.borrow_book(
                    st.session_state.username, 
                    book_id
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("Tidak ada buku yang tersedia untuk dipinjam")
    
    with tab4:
        st.subheader("🔄 Kembalikan Buku")
        transactions_df = db.get_sheet('transactions')

        if not transactions_df.empty:
            # Get user's active loans (borrowed but not returned)
            user_active_loans = transactions_df[
                (transactions_df['username'] == st.session_state.username) &
                (transactions_df['status'] == 'borrowed')
            ]

            if not user_active_loans.empty:
                st.info("Berikut adalah buku yang sedang Anda pinjam:")

                # Create options for books to return
                return_options = {}
                for _, loan in user_active_loans.iterrows():
                    due_date = pd.to_datetime(loan['due_date'])
                    today = pd.Timestamp.now()
                    days_overdue = (today - due_date).days if today > due_date else 0

                    status_text = f"{'⚠️ TERLAMBAT' if days_overdue > 0 else '✅ Masih dalam batas waktu'}"
                    if days_overdue > 0:
                        status_text += f" ({days_overdue} hari)"

                    option_text = f"{loan['book_title']} - Dipinjam: {loan['borrow_date']} - Jatuh tempo: {loan['due_date']} - {status_text}"
                    return_options[option_text] = loan['transaction_id']

                selected_return = st.selectbox(
                    "Pilih buku yang ingin dikembalikan:",
                    list(return_options.keys())
                )

                if st.button("🔄 Kembalikan Buku", type="primary"):
                    print("DEBUG: Return button clicked!")
                    print(f"DEBUG: Current user: {st.session_state.username}")
                    print(f"DEBUG: selected_return: {selected_return}")
                    print(f"DEBUG: return_options: {return_options}")

                    if selected_return in return_options:
                        transaction_id = return_options[selected_return]
                        print(f"DEBUG: Calling return_book with transaction_id: {transaction_id}")
                        success, message = book_manager.return_book(transaction_id)
                        print(f"DEBUG: return_book result - success: {success}, message: {message}")
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        print("DEBUG: selected_return not in return_options")
                        st.error("Pilihan tidak valid")

                # Show potential fine calculation
                if selected_return:
                    transaction_id = return_options[selected_return]
                    loan = user_active_loans[user_active_loans['transaction_id'] == transaction_id].iloc[0]
                    due_date = pd.to_datetime(loan['due_date'])
                    today = pd.Timestamp.now()

                    if today > due_date:
                        days_late = (today - due_date).days
                        fine = days_late * 5000
                        st.warning(f"⚠️ Buku ini terlambat {days_late} hari. Denda yang harus dibayar: Rp {fine:,}")
                    else:
                        st.success("✅ Buku dapat dikembalikan tanpa denda")

            else:
                st.info("Anda tidak memiliki buku yang sedang dipinjam")
        else:
            st.info("Belum ada transaksi peminjaman")

    with tab5:
        st.subheader("📋 Riwayat Peminjaman Saya")
        transactions_df = db.get_sheet('transactions')
        if not transactions_df.empty:
            user_transactions = transactions_df[
                transactions_df['username'] == st.session_state.username
            ]
            if not user_transactions.empty:
                st.dataframe(
                    user_transactions[[
                        'transaction_id', 'book_title', 'borrow_date',
                        'due_date', 'return_date', 'status', 'fine'
                    ]],
                    use_container_width=True
                )
            else:
                st.info("Anda belum meminjam buku apapun")
        else:
            st.info("Belum ada transaksi peminjaman")

# ===============================
# FUNGSI STREAMLIT - ADMIN DASHBOARD
# ===============================
def show_admin_dashboard():
    """Dashboard untuk admin"""
    st.header(f"👑 Dashboard Admin - {st.session_state.username}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Kelola Buku", 
        "👥 Buku Terpinjam", 
        "📊 Analisis",
        "➕ Tambah Buku",
        "⚙️ Admin Tools"
    ])
    
    with tab1:
        st.subheader("📚 Semua Buku dalam Sistem")
        books_df = book_manager.get_all_books()
        if not books_df.empty:
            st.dataframe(books_df, use_container_width=True)
            
            # Statistik cepat
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Buku", len(books_df))
            with col2:
                st.metric("Buku Tersedia", len(books_df[books_df['available'] == True]))
            with col3:
                st.metric("Buku Dipinjam", len(books_df[books_df['available'] == False]))
        else:
            st.info("Belum ada buku dalam sistem")
    
    with tab2:
        st.subheader("👥 Buku yang Sedang Dipinjam")
        transactions_df = db.get_sheet('transactions')
        books_df = db.get_sheet('books')
        
        if not transactions_df.empty:
            active_loans = transactions_df[transactions_df['status'] == 'borrowed']
            if not active_loans.empty:
                # Gabungkan dengan data buku untuk info lengkap
                loan_details = pd.merge(
                    active_loans, 
                    books_df, 
                    on='book_id', 
                    how='left'
                )
                
                st.dataframe(
                    loan_details[[
                        'transaction_id', 'username', 'title', 'author', 
                        'borrow_date', 'due_date'
                    ]],
                    use_container_width=True
                )
                
                # Fitur pengembalian buku
                st.subheader("🔄 Proses Pengembalian Buku")
                transaction_id = st.number_input(
                    "Masukkan ID Transaksi untuk pengembalian:",
                    min_value=1,
                    step=1
                )
                
                if st.button("Proses Pengembalian"):
                    success, message = book_manager.return_book(transaction_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("Tidak ada buku yang sedang dipinjam")
        else:
            st.info("Belum ada transaksi peminjaman")
    
    with tab3:
        st.subheader("📊 Analisis dan Statistik")
        
        stats = analytics.get_borrowing_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transaksi", stats['total_transactions'])
            with col2:
                st.metric("Sedang Dipinjam", stats['active_borrows'])
            with col3:
                st.metric("Rata-rata Peminjaman", f"{stats['mean_borrows']:.2f}")
            
            # Visualisasi
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Trend Peminjaman Bulanan")
                analytics.plot_borrowing_trend()
            with col2:
                st.subheader("Distribusi Kategori Buku")
                analytics.plot_category_distribution()
        else:
            st.info("Belum ada data untuk dianalisis")
    
    with tab4:
        st.subheader("➕ Tambah Buku Baru")
        
        with st.form("add_book_form"):
            title = st.text_input("Judul Buku *")
            author = st.text_input("Penulis *")
            year = st.number_input(
                "Tahun Terbit *", 
                min_value=1000, 
                max_value=2100, 
                value=2024
            )
            category = st.selectbox(
                "Kategori *",
                ["Programming", "Data Science", "Artificial Intelligence", 
                 "Web Development", "Database", "Fiction", "Non-Fiction", "Lainnya"]
            )
            isbn = st.text_input("ISBN (opsional)")
            
            submit = st.form_submit_button("Tambah Buku", type="primary")
            
            if submit:
                if not title or not author:
                    st.error("Judul dan Penulis wajib diisi!")
                else:
                    book_data = {
                        'title': title,
                        'author': author,
                        'year': int(year),
                        'category': category,
                        'isbn': isbn
                    }
                    
                    success, message = book_manager.add_book(book_data)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab5:
        st.subheader("⚙️ Admin Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📊 Data Users")
            users_df = db.get_sheet('users')
            if not users_df.empty:
                st.dataframe(
                    users_df[['username', 'email', 'created_at']],
                    use_container_width=True
                )
            else:
                st.info("Belum ada user terdaftar")
        
        with col2:
            st.info("🔄 System Info")
            st.write(f"Total Buku: {len(book_manager.get_all_books())}")
            st.write(f"Total Users: {len(users_df) if not users_df.empty else 0}")
            st.write(f"Database File: library_db.xlsx")
            
            if st.button("🔄 Refresh Database"):
                st.rerun()

# ===============================
# MAIN APPLICATION
# ===============================
def main():
    """Aplikasi utama Streamlit"""
    st.set_page_config(
        page_title="E-Library System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📚 E-Library System</h1>', unsafe_allow_html=True)
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # Sidebar untuk navigasi
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
        st.title("Navigasi")
        
        if not st.session_state.logged_in:
            menu = st.radio(
                "Pilih Menu:",
                ["🔐 Login User", "📝 Register", "👑 Login Admin"],
                index=0
            )
        else:
            st.success(f"Login sebagai: **{st.session_state.username}**")
            if st.session_state.is_admin:
                st.info("👑 Role: Administrator")
            else:
                st.info("👤 Role: User")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.is_admin = False
                st.rerun()
            
            st.divider()
            st.info("ℹ️ Sistem E-Library")
            st.caption("Project UAS - Basic Python OOP")
    
    # Routing halaman berdasarkan status login
    if not st.session_state.logged_in:
        if menu == "🔐 Login User":
            show_login_page()
        elif menu == "📝 Register":
            show_register_page()
        elif menu == "👑 Login Admin":
            show_admin_login_page()
    else:
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            show_user_dashboard()
    
    # Footer
    st.divider()
    st.caption("🎓 Project UAS - E-Library System | Kelompok 4")

if __name__ == "__main__":
    main()