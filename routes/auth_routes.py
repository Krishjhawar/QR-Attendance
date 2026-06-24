# routes/auth_routes.py
#
# KEY: 'next' param carries the QR attendance URL through the login flow.
# When student scans QR without being logged in:
#   /attendance/mark?session_id=4
#   → Flask-Login → /login?next=%2Fattendance%2Fmark%3Fsession_id%3D4
#   → After login  → redirected back → attendance auto-marked ✓

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from models.user_model import User
from utils.session_utils import mark_user_logged_in, mark_user_logged_out, is_user_already_logged_in

auth = Blueprint('auth', __name__)


@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(_dash(current_user))

    next_url = request.args.get('next', '') or request.form.get('next', '')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user     = User.query.filter_by(username=username).first()

        if not user or user.password != password:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', next_url=next_url)

        if is_user_already_logged_in(user):
            flash('Previous session overridden.', 'info')

        login_user(user)
        mark_user_logged_in(user)
        flash(f'Welcome, {user.username}!', 'success')

        # Return to QR attendance URL if that triggered login
        if next_url and next_url.startswith('/'):
            return redirect(next_url)

        return redirect(_dash(user))

    return render_template('login.html', next_url=next_url)


def _dash(user):
    return url_for('teacher.dashboard') if user.role == 'teacher' \
           else url_for('student.dashboard')


@auth.route('/logout')
@login_required
def logout():
    mark_user_logged_out(current_user)
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))