from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_migrate import Migrate
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from functools import wraps
import pytz
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class DatabaseRfid(db.Model):
    __tablename__ = 'log_rfid'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.DateTime,nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique = True, nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(10))
    password = db.Column(db.String(256), nullable=False)

class Uid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_reset_token(email):
    return serializer.dumps(email, salt='reset-password-salt')

def verify_reset_token(token, expiration=300):
    try:
        email = serializer.loads(token, salt='reset-password-salt', max_age=expiration)
    except:
        return None
    return email

def send_reset_email(email, token):
    reset_link = url_for('reset_password', token=token, _external=True)
    msg = Message('Reset Your Password', recipients=[email])
    msg.body = f'Click the following link to reset your password: {reset_link}'
    mail.send(msg)

def check_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            if 'login_time' in session and (datetime.now(pytz.utc) - session['login_time']).seconds < 900:
                response = make_response(f(*args, **kwargs))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                return response
            else:
                flash('Your session has ended, please log in again.', 'danger')
                session.pop('logged_in', None)
                session.pop('username', None)
                session.pop('login_time', None)
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return decorated_function

database = {'last_uid': 'Scan your card...'}

@app.route('/dashboard/room-info/')
@check_session
def room_info():
    return render_template('room_info.html')

# Route untuk schedule
@app.route('/dashboard/room-schedule/')
@check_session
def schedule():
    return render_template('schedule.html')

# Route untuk contact admin
@app.route('/dashboard/contact-admin/')
@check_session
def contact_admin():
    return render_template('contact_admin.html')

@app.route('/dashboard')
@check_session
def home():
    return render_template('homepage.html')

@app.route('/admin')
@check_session
def admin():
    return render_template('adminpage.html')

@app.route('/admin/access_log')
def access_log():
    # Fetch log access data from the DatabaseRfid table
    log_access_data = DatabaseRfid.query.filter(
        DatabaseRfid.waktu >= (datetime.utcnow() - timedelta(hours=24))
    ).all()

    # Convert the data to a list of dictionaries
    data = [
        {
            "id": log.id,
            "uid": log.uid,
            "waktu": log.waktu.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": log.waktu,
            "status": "Available" if log.id % 2 == 0 else "Not Available"
        }
        for log in log_access_data
    ]
    # Return the data as JSON
    return jsonify(data)

@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    if request.method == 'POST':
        email = request.form['email']
        nama = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm_password']
        
        if (
            len(password) < 8
            or not any(c.islower() for c in password)
            or not any(c.isupper() for c in password)
            or not any(c.isdigit() for c in password)
        ):
            flash('Your password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, and one digit.')
            return redirect(url_for('registrasi'))

        user = User.query.filter((User.email==email) | (User.username==username)).first()
        if user is None and password == confirm_password:
            new_user = User(email=email, nama=nama, username=username, password=generate_password_hash(password), role='user')
            db.session.add(new_user)
            db.session.commit()
            flash("Registration succesful, please log in.", 'success')
            return redirect(url_for('login'))
        elif password != confirm_password:
             flash("Passwords do not match", 'danger')
             return redirect(url_for('registrasi'))
        else:
            flash("The username or email already exist", "danger")
    return render_template('registerpage.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        user = User.query.filter((User.username==identifier) | (User.email==identifier)).first()

        if user is None:
            flash("User Didn't Find", 'danger')
        elif not check_password_hash(user.password, password):
            flash('Login failed. Please double-check your username/email and password', 'danger')
        else:  # User found and password matches
            session['logged_in'] = True 
            session['username'] = user.username
            session['role'] = user.role
            session['login_time'] = datetime.now(pytz.utc)
            if user.role == 'user':
                return redirect(url_for('home'))
            elif user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                flash('Role undefined', 'danger')
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        identifier = request.form['identifier']
        user = User.query.filter((User.username==identifier) | (User.email==identifier)).first()

        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            flash('The password reset email has been sent. Please check your email', 'success')
            return redirect(url_for('login'))

        flash("Can't find userneme or password", 'danger')

    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if email is None:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Ambil kata sandi baru dari formulir
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validasi kata sandi
        if not new_password or not confirm_password:
            flash('Password cannot be empty', 'danger')
            return redirect(url_for('reset_password', token=token))

        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('reset_password', token=token))

        # Enkripsi kata sandi
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Simpan kata sandi yang diubah ke database (sesuai dengan model pengguna Anda)
        user = User.query.filter_by(email=email).first()
        user.password = hashed_password
        db.session.commit()

        flash('Password has been reset successfully', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/api/catch_uid', methods=['POST'])
def nfc_scan():
    try:
        data = request.get_json()
        uid = data['uid']

        # Update UID terakhir di database
        database['last_uid'] = uid

        response = {'status': 'success', 'message': f'UID {uid} diterima'}
        return jsonify(response)

    except Exception as e:
        error_message = f'Error: {str(e)}'
        response = {'status': 'error', 'message': error_message}
        return jsonify(response)

@app.route('/regis_uid', methods=['GET', 'POST'])
@check_session
def regis_uid():
    if request.method == 'POST':
        uid= database['last_uid']
        nama = request.form['nama']
        uid = Uid.query.filter_by(uid=uid)
        if uid:
            flash('The UID already exist', 'warning')
            return redirect(url_for('regis_uid'))
        else:
            new_uid = Uid(uid=uid, nama=nama)
            db.session.add(new_uid)
            db.session.commit()
            flash('Your card succesfully registered!')
            return redirect(url_for('regis_uid'))
    return render_template('registrasi_uid.html', last_uid=database['last_uid'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)