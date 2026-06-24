# routes/student_routes.py

from flask import Blueprint, render_template
from flask_login import current_user
from utils.auth_utils import student_required
from services.attendance_service import get_student_attendance
from models.session_model import AttendanceSession

student = Blueprint('student', __name__, url_prefix='/student')


@student.route('/dashboard')
@student_required
def dashboard():
    records = get_student_attendance(current_user.id)
    history = [{
        'session':   AttendanceSession.query.get(r.session_id),
        'marked_at': r.marked_at,
        'ip':        r.ip_address,
    } for r in records]
    return render_template('dashboard_student.html', history=history)