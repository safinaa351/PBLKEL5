from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_login'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

app.secret_key = 'your_secret_key'

@app.route('/')
def home():
        return render_template('templates.html')
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
