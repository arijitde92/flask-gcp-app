from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from gcp_mysql_connect import connect_with_connector_auto_iam_authn
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection setup using gcp_mysql_connect.py
instance_conn_name = "inbound-byway-457408-c9:asia-south1:synerjix-mysql-practice"
user_name = "synerjix-sql"
db_name = "synerjix"

# Create the SQLAlchemy engine
engine = connect_with_connector_auto_iam_authn(instance_conn_name, user_name, db_name)
if engine:
    print("Connected to Cloud SQL MySQL instance successfully!")
else:
    print("Failed to connect to Cloud SQL MySQL instance.")
@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Debug: Print form data
        print(f"Form data: username={username}, email={email}, password={hashed_password}")

        # Insert user into the database
        insert_query = text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)")
        try:
            with engine.connect() as connection:
                connection.execute(insert_query, {
                    'username': username,
                    'email': email,
                    'password_hash': hashed_password
                })
                connection.commit()  # Commit the transaction
            print(f"User {username} signed up successfully.")
            flash('Sign up successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error signing up user {username}: {e}")
            if "Duplicate entry" in str(e):
                flash('Username or email already exists.', 'danger')
            else:
                flash(f'Error: {e}', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user from the database
        select_query = text("SELECT * FROM users WHERE email = :email")
        try:
            with engine.connect() as connection:
                user = connection.execute(select_query, {'email': email}).fetchone()
                print(user)  # Debug: Print fetched user data
            if user and check_password_hash(user[-2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]  # Store username in session
                # flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Add logic to handle password reset (e.g., send email with reset link)
        flash('Password reset instructions have been sent to your email.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear session variables
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# @app.teardown_appcontext
# def close_connection(exception=None):
#     """Close the database connection when the app context is torn down."""
#     engine.dispose()
#     print("Database connection closed.")

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        engine.dispose()  # Ensure connections are closed on app shutdown
