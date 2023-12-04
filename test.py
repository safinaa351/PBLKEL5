from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'db_rfid': 'mysql://root:@localhost/db_rfid'
}
app.secret_key = 'wearekelompok5'

db = SQLAlchemy(app)

class DatabaseRfid(db.Model):
    __bind_key__ = 'db_rfid'
    id = db.Column(db.Integer, primary_key=True)
    no_rfid = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, no_rfid, waktu):
        self.no_rfid = no_rfid
        self.waktu = waktu

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/admin')
def admin():
    if 'logged_in' in session:
        rfid_data = DatabaseRfid.query.all()
        response = make_response(render_template('view.php',rfid_data=rfid_data))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
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
        
        user = User.query.filter_by(username=username).first()
        if user is None and password == confirm_password:
            new_user = User(email=email, nama=nama, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash("Registrasi Berhasil, Silahkan Log in", 'success')
            return redirect(url_for('login'))
        elif password != confirm_password:
             flash("Password dan konfirmasi password tidak cocok", 'error')
             return redirect(url_for('registrasi'))
        else:
            flash("Username sudah ada", "danger")
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
            return redirect(url_for('admin'))
    return render_template('loginpage.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all(bind=db.get_engine(app, 'db_rfid'))  # Create tables in 'db_rfid'
    app.run(debug=True)
