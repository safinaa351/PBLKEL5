from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from app.models import Logaccess, User, Uid, Schedule, photoEvidence
from app.utils import check_session, verify_reset_token, generate_reset_token, send_reset_email, total_access_granted
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import pytz
from datetime import datetime, timedelta

database = {'last_uid': None}

@app.route('/dashboard/room-info/')
@check_session(allowed_roles=['user'])
def room_info():
    return render_template('room_info.html')

# Route untuk schedule
@app.route('/dashboard/room-schedule/')
@check_session(allowed_roles=['user'])
def schedule():
    schedules = Schedule.query.all()
    return render_template('schedule.html', schedules=schedules)

@app.route('/dashboard')
@check_session(allowed_roles=['user'])
def home():
    return render_template('homepage.html')

@app.route('/admin')
@check_session(allowed_roles=['admin'])
def admin():
    try:
        # Calculate the date for three days ago
        three_days_ago = datetime.utcnow() - timedelta(days=3)

        # Query images with access_time within the last three days
        images = photoEvidence.query.filter(photoEvidence.access_time >= three_days_ago).all()

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
@check_session(allowed_roles=['admin'])
def manage_schedule():
    schedules = Schedule.query.all()
    return render_template('manage_schedule.html', schedules=schedules)

@app.route('/store_uid', methods=['POST'])
def store_uid():
    if request.method == 'POST' and 'uid' in request.form:
        uid = request.form['uid']
        waktu_sekarang = datetime.now()

        try:
            new_log = Logaccess(no_rfid=uid, waktu=waktu_sekarang)
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
    log_access_data = Logaccess.query.all()

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
            "access": log.access,
            "status": "Not Available" if total_access_granted(log_access_data) % 2 == 1 else "Available"
        }
        for log in log_access_data
    ]

    if data[-1]['no_rfid'] and data[-1]['access'] == 'DENIED':
        database['last_uid'] = data[-1]['no_rfid']

    # Return the data as JSON
    return jsonify(data)

@app.route('/admin/manage_uid')
@check_session(allowed_roles=['admin'])
def manage_uid():
    uid_list = Uid.query.all()
    return render_template('manage_uid.html', uid_list=uid_list)
    
@app.route('/admin/delete_uid/<int:uid_id>', methods=['POST'])
@check_session(allowed_roles=['admin'])
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
@check_session(allowed_roles=['admin'])
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
@check_session(allowed_roles=['admin'])
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
@check_session(allowed_roles=['admin'])
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
@check_session(allowed_roles=['admin'])
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
            new_user = User(email=email, nama=nama, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role)
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
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin'))
        elif session['role'] == 'user':
            return redirect(url_for('home'))

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
    session.pop('role', None)
    session.pop('login_time', None)

    flash('You have been logged out', 'success')
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

@app.route('/regis_uid', methods=['GET', 'POST'])
@check_session(allowed_roles=['admin'])
def regis_uid():
    if request.method == 'POST':
        uid = database['last_uid']
        nama = request.form['nama']
        uid_record = Uid.query.filter_by(uid=uid).first()
        if uid_record:
            flash('The UID already exists', 'warning')
            return redirect(url_for('regis_uid'))
        elif uid == None:
            flash('Scan your card first', 'danger')
            return redirect(url_for('regis_uid'))
        else:
            new_uid = Uid(uid=uid, nama=nama)
            db.session.add(new_uid)
            db.session.commit()
            flash('Your card successfully registered!')
            return redirect(url_for('regis_uid'))
    last_uid = database['last_uid']
    return render_template('registrasi_uid.html', last_uid=last_uid)