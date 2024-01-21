from flask import flash, redirect, url_for, make_response, session
from datetime import datetime, timedelta
from app import app, mail, serializer
from flask_mail import Message
import pytz
from functools import wraps

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

def check_session(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' in session:
                # Jika sesi telah berakhir (lebih dari 15 menit), arahkan ke halaman login
                if 'login_time' in session:
                    elapsed_time = (datetime.now(pytz.utc) - session['login_time']).seconds
                    if elapsed_time >= 900:
                        # ... (kode lain untuk menghandle sesi yang telah berakhir)
                        flash('Your session has ended, please log in again.', 'danger')
                        session.pop('logged_in', None)
                        session.pop('role', None)
                        session.pop('username', None)
                        session.pop('login_time', None)
                        return redirect(url_for('login'))
                    else:
                        # Perbarui waktu login hanya jika sisa waktu kurang dari 900 detik
                        if elapsed_time < 900:
                            session['login_time'] = datetime.now(pytz.utc)
                            session.permanent = True
                            app.permanent_session_lifetime = timedelta(seconds=900 - elapsed_time)

                # Pengecekan peran pengguna
                if 'role' in session:
                    user_role = session['role']
                    if user_role not in allowed_roles:
                        flash('You do not have permission to access the page', 'danger')
                        if user_role == 'admin':
                            return redirect(url_for('admin'))
                        elif user_role == 'user':
                            return redirect(url_for('home'))

                response = make_response(f(*args, **kwargs))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                return response
            flash('Please login first', 'danger')
            return redirect(url_for('login'))
        return decorated_function
    return decorator

def total_access_granted(log_access_data):
    # Calculate the total access granted in the log access data
    return sum(1 for log in log_access_data if log.access == 'GRANTED')