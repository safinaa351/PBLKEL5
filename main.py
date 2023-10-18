from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # Ganti dengan kunci yang lebih aman
app.secret_key = "123" 

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Data pengguna statis (contoh)
users = {'user1': 'password1', 'user2': 'password2'}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Daftar nama siswa yang akan diabsen
daftar_siswa = ["Siswa 1", "Siswa 2", "Siswa 3"]

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            user = User(username)
            login_user(user)
            flash('Login berhasil', 'success')
            return redirect(url_for('index'))  # Pengalihan ke rute /index

        else:
            flash('Login gagal. Periksa kembali username dan password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar', 'success')
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    if 'absen' not in session:
        session['absen'] = []
    return render_template('index.html', daftar_siswa=daftar_siswa, absen=session['absen'])

@app.route('/absen', methods=['POST'])
@login_required
def absen():
    if 'siswa' in request.form:
        siswa = request.form['siswa']
        if siswa not in session['absen']:
            session['absen'].append(siswa)
            flash(f'Siswa {siswa} berhasil diabsen.', 'success')
        else:
            flash(f'Siswa {siswa} sudah diabsen sebelumnya.', 'warning')
    return redirect(url_for('index'))

@app.route('/reset')
@login_required
def reset():
    session.pop('absen', None)
    flash('Reset absensi berhasil.', 'success')
    return redirect(url_for('index'))

@app.template_filter('message_color')
def message_color(message):
    if 'success' in message:
        return 'green'
    elif 'warning' in message:
        return 'orange'
    else:
        return 'red'

if __name__ == '__main__':
    app.run(debug=True)
