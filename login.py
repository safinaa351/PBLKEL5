from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "flask_login"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

app.secret_key = "your_secret_key"


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authentication(self, username, password):
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM user WHERE username = %s AND password = %s",
            (username, password),
        )
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            return User(username=user_data["username"], password=user_data["password"])
        return None


@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/admin")
def admin():
    return render_template('adminpage.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username, password)
        found_user = user.authentication(username, password)
        if found_user:
            session["username"] = found_user.username
            return redirect(url_for("admin"))
        else:
            flash("Username or Password is incorrect", "error")
            return redirect(url_for("login"))
    return render_template("loginpage.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/update")
def update():
    pass

if __name__ == "__main__":
    app.run(debug=True)

#test
