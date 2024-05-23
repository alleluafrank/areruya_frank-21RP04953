from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure random key in production

# Function to connect to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='infocus_studio'
    )

# Decorator for routes that require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Register user route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstName']
        lastname = request.form['lastName']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO users (Firstname, Lastname, phone, Username, Password) VALUES (%s, %s, %s, %s, %s)',
                        (firstname, lastname, phone, username, hashed_password)
                    )
                    conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute('SELECT * FROM users WHERE Username = %s', (username,))
                    user = cursor.fetchone()
            if user and check_password_hash(user['Password'], password):
                session['user_id'] = user['user_id']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
                user = cursor.fetchone()
        if user:
            return render_template('dashboard.html', username=user['Username'])
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return redirect(url_for('login'))

@app.route('/order_service', methods=['GET', 'POST'])
@login_required
def order_service():
    services = fetch_services_from_database()

    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        phone = request.form['phone']
        service_name = request.form['service_name']
        service_price = request.form['service_price']
        date = request.form['date']

        user = fetch_user_from_session()
        if user:
            try:
                insert_order_into_database(firstName, lastName, phone, service_name, service_price, date)
                flash('Order sent successfully!', 'success')
                return redirect(url_for('order_service'))
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
        else:
            return redirect(url_for('login'))

    user = fetch_user_from_session()
    return render_template('order_service.html', services=services, user=user)

def fetch_user_from_session():
    user_id = session.get('user_id')
    if user_id:
        try:
            with get_db_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT Firstname, Lastname, phone FROM users WHERE user_id = %s", (user_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
    return None

def fetch_services_from_database():
    try:
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT service_id, service_name, price FROM services")
                return cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return []

def get_service_price_from_database(service_id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT price FROM services WHERE service_id = %s", (service_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return None

def insert_order_into_database(firstName, lastName, phone, service_name, service_price, date):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO orders (Firstname, Lastname, phone, service_name, price, date) VALUES (%s, %s, %s, %s, %s, %s)",
                               (firstName, lastName, phone, service_name, service_price, date))
                connection.commit()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
