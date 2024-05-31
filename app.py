from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure random key
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure MySQL connection pooling
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "infocus_studio"
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

# Function to get a connection from the pool
def get_db_connection():
    return connection_pool.get_connection()

# Registration form with validation
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Length(min=10, max=15)])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])
    submit = SubmitField('Register')

    # Custom validator to check for unique username
    def validate_username(self, field):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE Username = %s', (field.data,))
        if cursor.fetchone():
            raise ValidationError('Username already taken.')
        cursor.close()
        conn.close()

# Register user route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        username = form.username.data
        password = generate_password_hash(form.password.data)  # Hash the password

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (Firstname, Lastname, phone, Username, Password) VALUES (%s, %s, %s, %s, %s)',
                           (firstname, lastname, phone, username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE Username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['Password'], password):
            session['user_id'] = user['user_id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = fetch_user_from_session()
        if user:
            return render_template('dashboard.html', username=user['Username'])
    flash('Please log in to access the dashboard', 'warning')
    return redirect(url_for('login'))

@app.route('/order_service', methods=['GET', 'POST'])
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
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
            return redirect(url_for('order_service'))
        else:
            flash('Please log in to place an order', 'warning')
            return redirect(url_for('login'))

    user = fetch_user_from_session()
    return render_template('order_service.html', services=services, user=user)

def fetch_user_from_session():
    user_id = session.get('user_id')
    if user_id:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT Firstname, Lastname, phone, Username FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    return None

def fetch_services_from_database():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT service_id, service_name, price FROM services")
    services = cursor.fetchall()
    cursor.close()
    connection.close()
    return services

def insert_order_into_database(firstName, lastName, phone, service_name, service_price, date):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO orders (Firstname, Lastname, phone, service_name, price, date) VALUES (%s, %s, %s, %s, %s, %s)",
                   (firstName, lastName, phone, service_name, service_price, date))
    connection.commit()
    cursor.close()
    connection.close()

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
