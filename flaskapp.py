from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  #  random secure key

# Set up database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "users.db")

# Create users table if it doesn't exist
def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            firstname TEXT NOT NULL,
                            lastname TEXT NOT NULL,
                            email TEXT NOT NULL,
                            address TEXT NOT NULL)''')
        conn.commit()

create_database()

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)", 
                               (username, password, firstname, lastname, email, address))
                conn.commit()
                session['username'] = username  # Store in session
                return redirect(url_for('display'))
            except sqlite3.IntegrityError:
                return "Error: Username already exists. <a href='/register'>Try Again</a>"

    return render_template('register.html')

# Display User Information After Registration
@app.route('/display')
def display():
    if 'username' in session:
        username = session['username']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT firstname, lastname, email, address FROM users WHERE username=?", (username,))
            user_data = cursor.fetchone()
            if user_data:
                return render_template('display.html', user=user_data)
    return redirect(url_for('register'))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT firstname, lastname, email, address FROM users WHERE username=? AND password=?", (username, password))
            user_data = cursor.fetchone()
            if user_data:
                return render_template('display.html', user=user_data)
            else:
                return "Invalid login. <a href='/login'>Try Again</a>"

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
