import sqlite3
import hashlib
from flask import Flask, jsonify, request, render_template_string, session

app = Flask(__name__)
app.secret_key = 'rafia_secret_key_library_app'

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 1. Books Table
    cursor.execute("PRAGMA table_info(books)")
    columns = [column[1] for column in cursor.fetchall()]
    if not columns or 'status' not in columns or 'category' not in columns:
        cursor.execute('DROP TABLE IF EXISTS books')
        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                status TEXT DEFAULT 'Available'
            )
        ''')
        cursor.execute("INSERT INTO books (title, author, category, status) VALUES ('Clean Code', 'Robert C. Martin', 'Programming', 'Available')")
        cursor.execute("INSERT INTO books (title, author, category, status) VALUES ('The Pragmatic Programmer', 'Andrew Hunt', 'Programming', 'Borrowed')")
        cursor.execute("INSERT INTO books (title, author, category, status) VALUES ('The Hobbit', 'J.R.R. Tolkien', 'Fiction', 'Available')")

    # 2. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Student'
        )
    ''')
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', ?, 'Admin')", (hashed_admin_pass,))

    cursor.execute("SELECT * FROM users WHERE username = 'student'")
    if not cursor.fetchone():
        hashed_student_pass = hashlib.sha256('student123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('student', ?, 'Student')", (hashed_student_pass,))

    conn.commit()
    conn.close()

init_db()

# --- FRONTEND TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rafia Digital Library</title>
    <!-- SweetAlert2 -->
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f0f2f5; color: #333; }
        
        .navbar { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 15px 40px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .navbar h1 { margin: 0; font-size: 24px; letter-spacing: 1px; }
        .nav-links button { background: transparent; border: none; color: white; padding: 10px 18px; font-size: 15px; cursor: pointer; border-radius: 6px; transition: 0.3s; margin-left: 5px; }
        .nav-links button:hover, .nav-links button.active { background: rgba(255,255,255,0.2); font-weight: bold; }
        
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .page { display: none; }
        .page.active { display: block; }
        
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); margin-bottom: 25px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px; }
        .stat-card { background: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 4px solid #2a5298; }
        .stat-card h2 { margin: 10px 0 0 0; font-size: 32px; color: #1e3c72; }
        
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: 600; }
        input, select { width: 100%; padding: 11px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
        
        .filter-row { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; align-items: center; }
        .filter-row input, .filter-row select { flex: 1; min-width: 150px; }
        
        button.btn-primary { background: #28a745; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: bold; width: 100%; transition: 0.3s; }
        button.btn-primary:hover { background: #218838; }
        
        .btn-export { background: #17a2b8; color: white; border: none; padding: 9px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-left: 5px; }
        .btn-export:hover { background: #138496; }
        
        .btn-pdf { background: #6c757d; color: white; border: none; padding: 9px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-left: 5px; }
        .btn-pdf:hover { background: #5a6268; }

        button.delete { background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; }
        button.edit { background: #ffc107; color: #333; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; margin-right: 5px; }
        button.status-btn { background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; margin-right: 5px; }
        
        ul { list-style: none; padding: 0; }
        li { background: #fff; margin: 12px 0; padding: 18px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 6px solid #2a5298; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .badge-cat { font-size: 12px; background: #e2e8f0; color: #475569; padding: 3px 10px; border-radius: 12px; margin-left: 8px; }
        .badge-status { font-size: 11px; padding: 3px 8px; border-radius: 6px; font-weight: bold; margin-left: 5px; }
        .status-Available { background: #d4edda; color: #155724; }
        .status-Borrowed { background: #f8d7da; color: #721c24; }
        .user-info { font-size: 14px; background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; margin-right: 10px; }

        /* Print Style for PDF Generation */
        @media print {
            body { background: white; color: black; }
            .navbar, .filter-row, .btn-export, .btn-pdf, .action-btns { display: none !important; }
            .card { box-shadow: none; border: none; padding: 0; }
            li { border: 1px solid #ccc; margin: 5px 0; }
        }
    </style>
</head>
<body>

    <div class="navbar">
        <h1>📖 Rafia Digital Library</h1>
        <div class="nav-links">
            <span id="user-badge" class="user-info" style="display:none;"></span>
            <button id="nav-home" onclick="showPage('home-page', this)">🏠 Dashboard</button>
            <button id="nav-cat" onclick="showPage('catalogue-page', this)">📚 Catalogue</button>
            <button id="nav-add" style="display:none;" onclick="showPage('add-page', this)">➕ Add Book</button>
            <button id="nav-auth" onclick="showPage('login-page', this)">🔑 Login / Register</button>
            <button id="nav-logout" style="display:none;" onclick="logout()">🚪 Logout</button>
        </div>
    </div>

    <div class="container">

        <!-- AUTH -->
        <div id="login-page" class="page active">
            <div class="card" style="max-width: 450px; margin: 40px auto;">
                <h2 id="auth-title">🔑 Login to Library</h2>
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="auth-username" placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" id="auth-password" placeholder="Enter password">
                </div>
                <div id="role-group" class="form-group" style="display:none;">
                    <label>Role:</label>
                    <select id="auth-role">
                        <option value="Student">Student</option>
                        <option value="Admin">Admin</option>
                    </select>
                </div>
                <button id="auth-btn" class="btn-primary" onclick="handleAuth()">Login</button>
                <p style="text-align: center; margin-top: 15px; font-size: 14px;">
                    <span id="auth-toggle-msg">Don't have an account?</span> 
                    <a href="#" id="auth-toggle-link" onclick="toggleAuthMode(event)">Register Here</a>
                </p>
                <hr>
                <p style="font-size: 12px; color: #666; margin: 0;"><b>Default Accounts:</b><br>Admin: <i>admin / admin123</i><br>Student: <i>student / student123</i></p>
            </div>
        </div>

        <!-- DASHBOARD -->
        <div id="home-page" class="page">
            <div class="stats-grid">
                <div class="stat-card">
                    <span>Total Books</span>
                    <h2 id="stat-total">0</h2>
                </div>
                <div class="stat-card">
                    <span>Available Books</span>
                    <h2 id="stat-available" style="color: #28a745;">0</h2>
                </div>
                <div class="stat-card">
                    <span>Borrowed Books</span>
                    <h2 id="stat-borrowed" style="color: #dc3545;">0</h2>
                </div>
            </div>

            <div class="card">
                <h2>Welcome to Rafia Digital Library 🌟</h2>
                <p>Use search filters, view statistics, and export your library data to Excel/CSV or Print PDF.</p>
            </div>
        </div>

        <!-- CATALOGUE WITH EXPORT & ADVANCED FILTERS -->
        <div id="catalogue-page" class="page">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 15px;">
                    <h2>📖 Library Catalogue</h2>
                    <div>
                        <button class="btn-export" onclick="exportToCSV()">📥 Export Excel/CSV</button>
                        <button class="btn-pdf" onclick="exportToPDF()">🖨️ Print / PDF</button>
                    </div>
                </div>

                <!-- ADVANCED FILTER ROW -->
                <div class="filter-row">
                    <input type="text" id="search" placeholder="🔍 Search title or author..." onkeyup="filterBooks()">
                    <select id="category-filter" onchange="filterBooks()">
                        <option value="All">All Categories</option>
                        <option value="Programming">Programming</option>
                        <option value="Fiction">Fiction</option>
                        <option value="Science">Science</option>
                        <option value="History">History</option>
                        <option value="General">General</option>
                    </select>
                    <select id="status-filter" onchange="filterBooks()">
                        <option value="All">All Statuses</option>
                        <option value="Available">Available Only</option>
                        <option value="Borrowed">Borrowed Only</option>
                    </select>
                </div>

                <ul id="book-list"></ul>
            </div>
        </div>

        <!-- ADD / EDIT BOOK -->
        <div id="add-page" class="page">
            <div class="card">
                <h2 id="form-heading">➕ Add New Book</h2>
                <input type="hidden" id="book-id">
                
                <div class="form-group">
                    <label>Book Title:</label>
                    <input type="text" id="title" placeholder="e.g. Clean Code">
                </div>

                <div class="form-group">
                    <label>Author Name:</label>
                    <input type="text" id="author" placeholder="e.g. Robert C. Martin">
                </div>

                <div class="form-group">
                    <label>Category / Genre:</label>
                    <select id="category">
                        <option value="Programming">Programming</option>
                        <option value="Fiction">Fiction</option>
                        <option value="Science">Science</option>
                        <option value="History">History</option>
                        <option value="General">General</option>
                    </select>
                </div>

                <button id="submit-btn" class="btn-primary" onclick="saveBook()">Save Book to Library</button>
            </div>
        </div>

    </div>

    <script>
        let currentUser = null;
        let isRegisterMode = false;
        let allBooks = [];

        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });

        function showPage(pageId, btn) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-links button').forEach(b => b.classList.remove('active'));
            
            document.getElementById(pageId).classList.add('active');
            if(btn) btn.classList.add('active');
        }

        function toggleAuthMode(e) {
            e.preventDefault();
            isRegisterMode = !isRegisterMode;
            document.getElementById('auth-title').innerText = isRegisterMode ? '📝 Register New Account' : '🔑 Login to Library';
            document.getElementById('auth-btn').innerText = isRegisterMode ? 'Register' : 'Login';
            document.getElementById('role-group').style.display = isRegisterMode ? 'block' : 'none';
            document.getElementById('auth-toggle-msg').innerText = isRegisterMode ? 'Already have an account?' : "Don't have an account?";
            document.getElementById('auth-toggle-link').innerText = isRegisterMode ? 'Login Here' : 'Register Here';
        }

        async function handleAuth() {
            const username = document.getElementById('auth-username').value.trim();
            const password = document.getElementById('auth-password').value.trim();
            const role = document.getElementById('auth-role').value;

            if (!username || !password) {
                Swal.fire('Validation Error', 'Please enter both username and password!', 'warning');
                return;
            }

            const endpoint = isRegisterMode ? '/api/v1/auth/register' : '/api/v1/auth/login';
            const body = isRegisterMode ? { username, password, role } : { username, password };

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const data = await res.json();
            if (data.success) {
                if (isRegisterMode) {
                    Toast.fire({ icon: 'success', title: 'Account created! Please login.' });
                    toggleAuthMode({ preventDefault: () => {} });
                } else {
                    currentUser = data.user;
                    updateUIForUser();
                    Toast.fire({ icon: 'success', title: `Welcome back, ${currentUser.username}!` });
                    showPage('home-page', document.getElementById('nav-home'));
                    fetchBooks();
                }
            } else {
                Swal.fire('Authentication Error', data.message, 'error');
            }
        }

        function updateUIForUser() {
            if (currentUser) {
                document.getElementById('user-badge').innerText = `👤 ${currentUser.username} (${currentUser.role})`;
                document.getElementById('user-badge').style.display = 'inline-block';
                document.getElementById('nav-auth').style.display = 'none';
                document.getElementById('nav-logout').style.display = 'inline-block';
                
                if (currentUser.role === 'Admin') {
                    document.getElementById('nav-add').style.display = 'inline-block';
                } else {
                    document.getElementById('nav-add').style.display = 'none';
                }
            } else {
                document.getElementById('user-badge').style.display = 'none';
                document.getElementById('nav-auth').style.display = 'inline-block';
                document.getElementById('nav-logout').style.display = 'none';
                document.getElementById('nav-add').style.display = 'none';
            }
        }

        async function logout() {
            await fetch('/api/v1/auth/logout', { method: 'POST' });
            currentUser = null;
            updateUIForUser();
            Toast.fire({ icon: 'info', title: 'Logged out successfully' });
            showPage('login-page', document.getElementById('nav-auth'));
        }

        async function fetchBooks() {
            const res = await fetch('/api/v1/books');
            const data = await res.json();
            allBooks = data.data;
            updateStats();
            filterBooks();
        }

        function updateStats() {
            document.getElementById('stat-total').innerText = allBooks.length;
            const available = allBooks.filter(b => b.status === 'Available').length;
            const borrowed = allBooks.filter(b => b.status === 'Borrowed').length;
            document.getElementById('stat-available').innerText = available;
            document.getElementById('stat-borrowed').innerText = borrowed;
        }

        function renderBooks(books) {
            const list = document.getElementById('book-list');
            list.innerHTML = '';
            if(books.length === 0) {
                list.innerHTML = '<p style="color: #777;">No matching books found.</p>';
                return;
            }
            books.forEach(book => {
                let actionButtons = '';
                
                if (currentUser) {
                    actionButtons += `<button class="status-btn" onclick="toggleStatus(${book.id}, '${book.status}')">${book.status === 'Available' ? 'Borrow' : 'Return'}</button>`;
                    
                    if (currentUser.role === 'Admin') {
                        actionButtons += `
                            <button class="edit" onclick="editBook(${book.id}, '${book.title}', '${book.author}', '${book.category}')">Edit</button>
                            <button class="delete" onclick="deleteBook(${book.id})">Delete</button>
                        `;
                    }
                }

                list.innerHTML += `
                    <li>
                        <span>
                            <b>${book.title}</b> by <i>${book.author}</i>
                            <span class="badge-cat">${book.category || 'General'}</span>
                            <span class="badge-status status-${book.status}">${book.status}</span>
                        </span>
                        <div class="action-btns">${actionButtons}</div>
                    </li>
                `;
            });
        }

        // MULTI-CRITERIA FILTER (Search + Category + Status)
        function filterBooks() {
            const query = document.getElementById('search').value.toLowerCase();
            const selectedCat = document.getElementById('category-filter').value;
            const selectedStatus = document.getElementById('status-filter').value;

            const filtered = allBooks.filter(b => {
                const matchesSearch = b.title.toLowerCase().includes(query) || b.author.toLowerCase().includes(query);
                const matchesCat = selectedCat === 'All' || b.category === selectedCat;
                const matchesStatus = selectedStatus === 'All' || b.status === selectedStatus;
                return matchesSearch && matchesCat && matchesStatus;
            });
            renderBooks(filtered);
        }

        // EXPORT TO EXCEL / CSV
        function exportToCSV() {
            if (allBooks.length === 0) {
                Swal.fire('No Data', 'No books available to export!', 'info');
                return;
            }

            let csvContent = "data:text/csv;charset=utf-8,ID,Title,Author,Category,Status\\n";
            allBooks.forEach(b => {
                csvContent += `"${b.id}","${b.title}","${b.author}","${b.category}","${b.status}"\\n`;
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "library_books_export.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            Toast.fire({ icon: 'success', title: 'CSV Downloaded!' });
        }

        // PRINT / EXPORT TO PDF
        function exportToPDF() {
            window.print();
        }

        async function saveBook() {
            const id = document.getElementById('book-id').value;
            const title = document.getElementById('title').value.trim();
            const author = document.getElementById('author').value.trim();
            const category = document.getElementById('category').value;
            
            if (!title || !author) {
                Swal.fire('Input Error', 'Book Title and Author Name cannot be empty!', 'warning');
                return;
            }

            const bodyData = JSON.stringify({ title, author, category });

            if (id) {
                await fetch(`/api/v1/books/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: bodyData
                });
                Toast.fire({ icon: 'success', title: 'Book updated successfully!' });
            } else {
                await fetch('/api/v1/books', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: bodyData
                });
                Toast.fire({ icon: 'success', title: 'New book added to library!' });
            }

            resetForm();
            fetchBooks();
            showPage('catalogue-page', document.getElementById('nav-cat'));
        }

        async function toggleStatus(id, currentStatus) {
            const newStatus = currentStatus === 'Available' ? 'Borrowed' : 'Available';
            await fetch(`/api/v1/books/${id}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            Toast.fire({ icon: 'info', title: `Book marked as ${newStatus}` });
            fetchBooks();
        }

        function editBook(id, title, author, category) {
            document.getElementById('book-id').value = id;
            document.getElementById('title').value = title;
            document.getElementById('author').value = author;
            document.getElementById('category').value = category || 'General';
            
            document.getElementById('form-heading').innerText = '✏️ Edit Book Details';
            document.getElementById('submit-btn').innerText = 'Update Book Details';
            showPage('add-page', document.getElementById('nav-add'));
        }

        function resetForm() {
            document.getElementById('book-id').value = '';
            document.getElementById('title').value = '';
            document.getElementById('author').value = '';
            document.getElementById('form-heading').innerText = '➕ Add New Book';
            document.getElementById('submit-btn').innerText = 'Save Book to Library';
        }

        async function deleteBook(id) {
            const result = await Swal.fire({
                title: 'Are you sure?',
                text: "This book will be permanently deleted from the database!",
                icon: 'warning',
                showCancelButton: true,
                confirmColor: '#dc3545',
                confirmButtonText: 'Yes, delete it!'
            });

            if (result.isConfirmed) {
                await fetch(`/api/v1/books/${id}`, { method: 'DELETE' });
                Toast.fire({ icon: 'success', title: 'Book deleted successfully' });
                fetchBooks();
            }
        }
    </script>
</body>
</html>
"""

# --- AUTH ROUTES ---

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Student')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pass, role))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Username already exists"}), 400

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, hashed_pass))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user'] = {"id": user[0], "username": user[1], "role": user[2]}
        return jsonify({"success": True, "user": session['user']}), 200
    
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/v1/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True}), 200

# --- BOOK ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/books', methods=['GET'])
def get_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author, category, status FROM books')
    rows = cursor.fetchall()
    conn.close()
    books_list = [{"id": row[0], "title": row[1], "author": row[2], "category": row[3], "status": row[4]} for row in rows]
    return jsonify({"success": True, "data": books_list}), 200

@app.route('/api/v1/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"success": False, "message": "Title & Author required"}), 400
    
    category = data.get('category', 'General')
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (title, author, category, status) VALUES (?, ?, ?, ?)', (data['title'], data['author'], category, 'Available'))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 201

@app.route('/api/v1/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"success": False, "message": "Title & Author required"}), 400
    
    category = data.get('category', 'General')
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE books SET title = ?, author = ?, category = ? WHERE id = ?', (data['title'], data['author'], category, book_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200

@app.route('/api/v1/books/<int:book_id>/status', methods=['PATCH'])
def toggle_status(book_id):
    data = request.get_json()
    new_status = data.get('status', 'Available')
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE books SET status = ? WHERE id = ?', (new_status, book_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200

@app.route('/api/v1/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)