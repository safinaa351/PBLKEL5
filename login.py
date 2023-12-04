from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'wearekelompok5'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique = True, nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    
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


@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    if request.method == 'POST':
        email = request.form['email']
        nama = request.form["nama"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm-password']
        
        user = User.query.filter_by(email=email, username=username).first()
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
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
