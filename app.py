from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_migrate import Migrate
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from functools import wraps
import base64
import pytz
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.urandom(24)
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
    no_rfid = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.DateTime,nullable=False)
    
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

class Schedule(db.Model):
    __tablename__ = 'tb_roomschedules'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(15), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_name = db.Column(db.String(30), nullable=False)

class Images(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    file_name =  db.Column(db.String(255), nullable=False)
    image_data = db.Column(MEDIUMBLOB)

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
            # Jika sesi telah berakhir (lebih dari 15 menit), arahkan ke halaman login
            if 'login_time' in session:
                elapsed_time = (datetime.now(pytz.utc) - session['login_time']).seconds
                if elapsed_time >= 900:
                    # ... (kode lain untuk menghandle sesi yang telah berakhir)
                    flash('Your session has ended, please log in again.', 'danger')
                    session.pop('logged_in', None)
                    session.pop('username', None)
                    session.pop('login_time', None)
                    return redirect(url_for('login'))
                else:
                    # Perbarui waktu login hanya jika sisa waktu kurang dari 900 detik
                    if elapsed_time < 900:
                        session['login_time'] = datetime.now(pytz.utc)
                        session.permanent = True
                        app.permanent_session_lifetime = timedelta(seconds=900 - elapsed_time)
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return decorated_function

database = {'last_uid': None}

@app.route('/dashboard/room-info/')
@check_session
def room_info():
    return render_template('room_info.html')

# Route untuk schedule
@app.route('/dashboard/room-schedule/')
@check_session
def schedule():
    schedules = Schedule.query.all()
    return render_template('schedule.html', schedules=schedules)

@app.route('/dashboard')
@check_session
def home():
    return render_template('homepage.html')

@app.route('/admin')
@check_session
def admin():
    try:
        images = Images.query.all()

        # Check if images are found in the database
        if images:
            for image in images:
                # Encode the binary data to base64
                image.image_data = base64.b64encode(image.image_data).decode('utf-8')

            return render_template('adminpage.html', images=images)
        else:
            return render_template('adminpage.html', images=[])
    except Exception as e:
        # Handle the exception (e.g., log it)
        error_message = f"Error: {str(e)}"
        return render_template('adminpage.html', images=[], error_message=error_message)

@app.route('/admin/manage-room-schedule')
@check_session
def manage_schedule():
    schedules = Schedule.query.all()
    return render_template('manage_schedule.html', schedules=schedules)

@app.route('/store_uid', methods=['POST'])
def store_uid():
    if request.method == 'POST' and 'uid' in request.form:
        uid = request.form['uid']
        waktu_sekarang = datetime.now()

        try:
            new_log = DatabaseRfid(no_rfid=uid, waktu=waktu_sekarang)
            db.session.add(new_log)
            db.session.commit()
            return "Data UID berhasil disimpan ke database.\n" \
                   "=================================================="
        except Exception as e:
            return f"Gagal menyimpan data UID ke database: {str(e)}"
    return "Invalid Request"

@app.route('/admin/access_log')
def access_log():
    # Fetch log access data from the DatabaseRfid table
    log_access_data = DatabaseRfid.query.all()

    # Check if log_access_data is empty
    if not log_access_data:
        # If no data is found, set a default entry with status 'Available'
        default_entry = {
            "id": 0,
            "no_rfid": "N/A",
            "waktu": "N/A",
            "timestamp": "N/A",
            "status": "Available"
        }
        return jsonify([default_entry])

    # Convert the data to a list of dictionaries
    data = [
        {
            "id": log.id,
            "no_rfid": log.no_rfid,
            "waktu": log.waktu.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": log.waktu,
            "status": "Available" if log.id % 2 == 0 else "Not Available"
        }
        for log in log_access_data
    ]
    # Return the data as JSON
    return jsonify(data)

@app.route('/admin/manage_uid')
@check_session
def manage_uid():
    uid_list = Uid.query.all()
    return render_template('manage_uid.html', uid_list=uid_list)
    
@app.route('/admin/delete_uid/<int:uid_id>', methods=['POST'])
@check_session
def delete_uid(uid_id):
    uid_to_delete = Uid.query.get(uid_id)
    if uid_to_delete:
        db.session.delete(uid_to_delete)
        db.session.commit()
        flash('UID has been deleted successfully.', 'success')
    else:
        flash('UID not found.', 'danger')
    return redirect(url_for('manage_uid'))

@app.route('/admin/edit_uid/<int:uid_id>', methods=['GET', 'POST'])
@check_session
def edit_uid(uid_id):
    if request.method == 'GET':
        uid_to_edit = Uid.query.get(uid_id)
        if uid_to_edit:
            return render_template('edit_uid.html', uid_to_edit=uid_to_edit)
        else:
            flash('UID not found.', 'danger')
            return redirect(url_for('manage_uid'))
    elif request.method == 'POST':
        nama_baru = request.form.get('nama')
        uid_to_update = Uid.query.get(uid_id)
        if uid_to_update:
            uid_to_update.nama = nama_baru
            db.session.commit()
            flash('UID has been updated successfully.', 'success')
            return redirect(url_for('manage_uid'))
        else:
            flash('UID not found.', 'danger')
            return redirect(url_for('manage_uid'))

@app.route('/add_room_schedule', methods=['POST'])
def add_room_schedule():
    if request.method == 'POST':
        day = request.form.get('day')
        time = request.form.get('time')
        subject = request.form.get('subject')
        class_name = request.form.get('class_name')

        new_schedule = Schedule(day=day, time=time, subject=subject, class_name=class_name)
        db.session.add(new_schedule)
        db.session.commit()
        flash("Room schedule added.", "success")
    return redirect(url_for('manage_schedule'))

@app.route('/admin/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
@check_session
def edit_schedule(schedule_id):
    if request.method == 'GET':
        schedule_to_edit = Schedule.query.get(schedule_id)
        if schedule_to_edit:
            return render_template('edit_schedule.html', schedule_to_edit=schedule_to_edit)
        else:
            flash('Schedule not found.', 'danger')
            return redirect(url_for('manage_schedule'))
    elif request.method == 'POST':
        new_day = request.form.get('day')
        new_time = request.form.get('time')
        new_subject = request.form.get('subject')
        new_class_name = request.form.get('class_name')
        schedule_to_update = Schedule.query.get(schedule_id)
        if schedule_to_update:
            schedule_to_update.day = new_day
            schedule_to_update.time = new_time
            schedule_to_update.subject = new_subject
            schedule_to_update.class_name = new_class_name
            db.session.commit()
            flash('Schedule has been updated successfully.', 'success')
            return redirect(url_for('manage_schedule'))
        else:
            flash('Schedule not found.', 'danger')
            return redirect(url_for('manage_schedule'))

@app.route('/admin/delete_schedule/<int:schedule_id>', methods=['POST'])
@check_session
def delete_schedule(schedule_id):
    schedule_to_delete = Schedule.query.get(schedule_id)
    if schedule_to_delete:
        db.session.delete(schedule_to_delete)
        db.session.commit()
        flash('Schedule has been deleted successfully.', 'success')
    else:
        flash('Schedule not found.', 'danger')
    return redirect(url_for('manage_schedule'))

@app.route('/admin/account-registration', methods=['GET', 'POST'])
@check_session
def registrasi():
    if request.method == 'POST':
        email = request.form['email']
        nama = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
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
            new_user = User(email=email, nama=nama, username=username, password=generate_password_hash(password), role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Account successfully registered", 'success')
            return redirect(url_for('admin'))
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
            return redirect(url_for('admin'))
        elif not check_password_hash(user.password, password):
            flash('Login failed. Incorrect username or password', 'danger')
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

        if (
            len(new_password) < 8
            or not any(c.islower() for c in new_password)   
            or not any(c.isupper() for c in new_password)
            or not any(c.isdigit() for c in new_password)
        ):
            flash('Your password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, and one digit.')
            return redirect(url_for('reset_password', token=token))

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
        uid = database['last_uid']
        nama = request.form['nama']
        uid_record = Uid.query.filter_by(uid=uid).first()
        if uid_record:
            flash('The UID already exists', 'warning')
            return redirect(url_for('regis_uid'))
        else:
            new_uid = Uid(uid=uid, nama=nama)
            db.session.add(new_uid)
            db.session.commit()
            flash('Your card successfully registered!')
            return redirect(url_for('regis_uid'))

    # Mendapatkan nilai last_uid dari database atau sesuai kebutuhan aplikasi
    last_uid = database['last_uid']
    return render_template('registrasi_uid.html', last_uid=last_uid)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)