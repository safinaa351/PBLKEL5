from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'db_rfid': 'mysql://root:@localhost/db_rfid'
}
app.config['SECRET_KEY'] = 'wearekelompok5'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'locklogic.corp@gmail.com'
app.config['MAIL_PASSWORD'] = 'hygq lkzf whgo ylyl'
app.config['MAIL_DEFAULT_SENDER'] = 'locklogic.corp@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class DatabaseRfid(db.Model):
    __tablename__ = 'log_rfid'
    __bind_key__ = 'db_rfid'
    id = db.Column(db.Integer, primary_key=True)
    no_rfid = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.DateTime, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, no_rfid, waktu):
        self.no_rfid = no_rfid
        self.waktu = waktu

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique = True, nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

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

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/admin')
def admin():
    if 'logged_in' in session:
        if 'login_time' in session and (datetime.now(pytz.utc) - session['login_time']).seconds < 900:
            response = make_response(render_template('adminpage.html'))
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response
        else:
            flash('Session anda telah berakhir, silahkan login kembali', 'danger')
            session.pop('logged_in', None)
            session.pop('username', None)
            session.pop('login_time', None)
    flash('Login terlebih dahulu', 'danger')
    return redirect(url_for('login'))

@app.route('/admin/access_log')
def access_log():
    # Fetch log access data from the DatabaseRfid table
    log_access_data = DatabaseRfid.query.filter(
        DatabaseRfid.timestamp >= (datetime.utcnow() - timedelta(hours=24))
    ).all()

    # Convert the data to a list of dictionaries
    data = [
        {"id": log.id, "no_rfid": log.no_rfid, "waktu": log.waktu.strftime("%Y-%m-%d %H:%M:%S"), "timestamp": log.timestamp}
        for log in log_access_data
    ]

    # Return the data as JSON
    return jsonify(data)

@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    if request.method == 'POST':
        email = request.form['email']
        nama = request.form["nama"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm-password']
        
        user = User.query.filter((User.email==email) | (User.username==username)).first()
        if user is None and password == confirm_password:
            new_user = User(email=email, nama=nama, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash("Registrasi Berhasil, Silahkan Log in", 'success')
            return redirect(url_for('login'))
        elif password != confirm_password:
             flash("Password dan konfirmasi password tidak cocok", 'danger')
             return redirect(url_for('registrasi'))
        else:
            flash("Username atau Email sudah ada", "danger")
    return render_template('registerpage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        user = User.query.filter((User.username==identifier) | (User.email==identifier)).first()

        if user is None:
            flash('Login Gagal, cek username Anda', 'danger')
        elif not check_password_hash(user.password, password):
            flash('Login Gagal, cek password Anda', 'danger')
        else:
            session['logged_in'] = True
            session['username'] = user.username
            session['login_time'] = datetime.now(pytz.utc)
            return redirect(url_for('admin'))
    return render_template('loginpage.html')

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
            flash('Email reset password telah dikirim. Silahkan cek email Anda.', 'success')
            return redirect(url_for('login'))

        flash('Username atau Email tidak ditemukan.', 'danger')

    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if email is None:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('index'))

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)