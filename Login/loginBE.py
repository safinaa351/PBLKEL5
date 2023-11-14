from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

##hhhhhhhhh
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_login'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']  # Ganti 'password' dengan 'pass' sesuai dengan nama yang didefinisikan di form HTML
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['username'] = user['username']
            flash('Login successful', 'success')  # Menambahkan pesan sukses
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')  # Mengubah pesan logout
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/delete')
def delete():
    pass

@app.route('/add')
def add():
    pass

@app.route('/edit')
def edit():
    pass