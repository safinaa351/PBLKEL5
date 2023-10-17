from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # Ganti dengan kunci yang lebih aman

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

@app.route('/')
def home():
    return redirect(url_for('login')) ("selamat datang")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            user = User(username)
            login_user(user)
            flash('Login berhasil', 'success')
            # Menjalankan main.py sebagai aplikasi terpisah
            subprocess.run(["python", "C:\\Users\\ACER\\Desktop\\flask\\myenv\\main.py"])

        else:
            flash('Login gagal. Periksa kembali username dan password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
