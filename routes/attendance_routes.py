# routes/attendance_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from utils.ip_utils import get_client_ip
from services.validation_service import validate_attendance
from services.attendance_service import mark_attendance
from models.session_model import AttendanceSession

attendance = Blueprint('attendance', __name__, url_prefix='/attendance')


# ── PRIMARY: auto-mark when QR is scanned ──────────────────────────────────
@attendance.route('/mark', methods=['GET'])
@login_required
def mark():
    """
    Called automatically when student's browser opens the QR URL.
    No form input required. Fully automatic attendance marking.

    If student isn't logged in → Flask-Login → /login?next=this_url
    After login → redirected back here → marked ✓
    """
    if current_user.role != 'student':
        flash('Only students can mark attendance.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    session_id = request.args.get('session_id', type=int)
    if not session_id:
        return _render_result('error', 'Invalid QR — session ID missing.', None, None)

    student_ip = get_client_ip()
    ok, err    = validate_attendance(session_id, current_user.id, student_ip)

    if not ok:
        if err == 'already_marked':
            return _render_result('duplicate', 'Attendance already recorded.', session_id, None)
        return _render_result('error', err, session_id, None)

    mark_attendance(current_user.id, session_id, student_ip)
    sess = AttendanceSession.query.get(session_id)
    return _render_result('success', 'Attendance recorded successfully!', session_id, sess)


# ── OPTION 2: browser camera scanner (JS / html5-qrcode) ───────────────────
@attendance.route('/scan-camera', methods=['GET'])
@login_required
def scan_camera():
    if current_user.role != 'student':
        flash('Students only.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    return render_template('scan_camera.html')


# ── OPTION 3: manual fallback ────────────────────────────────────────────────
@attendance.route('/scan', methods=['GET', 'POST'])
@login_required
def scan_qr():
    if current_user.role != 'student':
        flash('Students only.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        raw        = request.form.get('qr_text', '').strip()
        session_id = _parse_id(raw)

        if session_id is None:
            flash('Could not parse. Paste the full URL or just the session number.', 'danger')
            return render_template('scan_qr.html')

        student_ip = get_client_ip()
        ok, err    = validate_attendance(session_id, current_user.id, student_ip)

        if not ok:
            flash('Attendance already recorded.' if err == 'already_marked' else err,
                  'warning' if err == 'already_marked' else 'danger')
            return render_template('scan_qr.html')

        mark_attendance(current_user.id, session_id, student_ip)
        flash(f'✅ Attendance marked for Session #{session_id}!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('scan_qr.html')


# ── Helpers ──────────────────────────────────────────────────────────────────
def _parse_id(raw: str):
    try:
        if 'session_id=' in raw:
            return int(raw.split('session_id=')[-1].split('&')[0].strip())
        return int(raw.strip())
    except (ValueError, IndexError):
        return None


def _render_result(status, message, session_id, session_obj):
    return render_template(
        'attendance_result.html',
        status     = status,
        message    = message,
        session_id = session_id,
        session_obj= session_obj,
    )