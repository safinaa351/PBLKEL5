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


@app.route("/")
def home():
    return render_template("Tampilan_web.html")
    
@app.route("/admin")
def admin():
    if 'username' in session:  # Check if user is logged in
        username = session['username']
        # Here, you can check if the logged-in user is an admin in your database
        # For example, if there's a field 'is_admin' in the user table
        cur = mysql.connection.cursor()
        cur.execute("SELECT is_admin FROM user WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and user['is_admin']:
            # If the user is an admin, render the admin page
            return render_template("admin.html", username=username)
        else:
            # If not an admin, redirect to a different page or display an error
            flash("You do not have admin privileges", "error")
            return redirect(url_for("home"))  # Redirect to home or login page
    else:
        # If user is not logged in, redirect to the login page
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["pass"]
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT is_admin FROM user WHERE username = %s AND password = %s",
            (username, password),
        )
        is_admin = cur.fetchone()  # Fetch only the is_admin value
        cur.close()
        if is_admin:
            session["username"] = username
            if is_admin['is_admin']:
                return redirect(url_for("admin"))  # Redirect to admin page
            else:
                return redirect(url_for("home"))  # Redirect to home page for non-admins
        else:
            flash("Username or Password is incorrect", "error")
            return redirect(url_for("login"))
    return render_template("login.html")




@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

##test