# utils/auth_utils.py - Authentication helper decorators

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def teacher_required(f):
    """Decorator: only allow teachers to access this route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'teacher':
            flash('Access denied. Teachers only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    """Decorator: only allow students to access this route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'student':
            flash('Access denied. Students only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated