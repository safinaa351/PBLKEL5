from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config['MYSQL_HOST'] = 'localhost'
        self.config['MYSQL_USER'] = 'root'
        self.config['MYSQL_PASSWORD'] = ''
        self.config['MYSQL_DB'] = 'flask_login'
        self.config['MYSQL_CURSORCLASS'] = 'DictCursor'

        self.mysql = MySQL(self)

        self.secret_key = 'pblkelompok5'

        self.add_routes()

    def add_routes(self):
        self.add_route('/', 'home', view_func=self.home)
        self.add_route('/addusr', 'add', view_func=self.add)
        self.add_route('/login', 'login', methods=['GET', 'POST'], view_func=self.login)
        self.add_route('/logout', 'logout', view_func=self.logout)

    def add_route(self, rule, endpoint=None, view_func=None, **options):
        if endpoint is None:
            endpoint = view_func.__name__
        self.route(rule, endpoint=endpoint, **options)(view_func)

    def home(self):
        return render_template('Tampilan_web.html')

    def add(self):
        pass

    #def comment(self):
     #   pass

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['pass']
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()
            if user:
                session['username'] = user['username']
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
        return render_template('index.html')

    def logout(self):
        session.pop('username', None)
        return redirect(url_for('home'))

app = MyApp(__name__)

if __name__ == '__main__':
    app.run(debug=True)