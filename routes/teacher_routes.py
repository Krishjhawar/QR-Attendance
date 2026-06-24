# routes/teacher_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import current_user
from utils.auth_utils import teacher_required
from utils.ip_utils import get_client_ip
from services.attendance_service import create_session, get_session_attendance
from services.qr_service import generate_qr_code, get_or_create_qr
from models.session_model import AttendanceSession
from models.user_model import User
from config import Config
import datetime
import csv
import io

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')


@teacher.route('/dashboard')
@teacher_required
def dashboard():
    sessions = AttendanceSession.query.filter_by(
        teacher_id=current_user.id
    ).order_by(AttendanceSession.created_at.desc()).all()

    now = datetime.datetime.utcnow()
    session_data = []
    for s in sessions:
        elapsed   = (now - s.created_at).total_seconds()
        remaining = max(0, Config.QR_EXPIRY_SECONDS - elapsed)
        session_data.append({
            'session':   s,
            'count':     len(get_session_attendance(s.id)),
            'is_active': remaining > 0,
            'remaining': int(remaining),
        })

    return render_template('dashboard_teacher.html', session_data=session_data)


@teacher.route('/generate_qr', methods=['GET', 'POST'])
@teacher_required
def generate_qr():
    if request.method == 'POST':
        subject    = request.form.get('subject', 'General').strip() or 'General'
        teacher_ip = get_client_ip()

        new_session = create_session(current_user.id, teacher_ip, subject)
        generate_qr_code(
            session_id  = new_session.id,
            server_ip   = Config.SERVER_IP,
            server_port = Config.SERVER_PORT,
        )

        flash(f'Session #{new_session.id} created!', 'success')
        return redirect(url_for('teacher.session_detail', session_id=new_session.id))

    return render_template('generate_qr.html')


@teacher.route('/session/<int:session_id>')
@teacher_required
def session_detail(session_id):
    sess = AttendanceSession.query.get_or_404(session_id)

    if sess.teacher_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    qr_image, qr_url = get_or_create_qr(
        session_id  = session_id,
        server_ip   = Config.SERVER_IP,
        server_port = Config.SERVER_PORT,
    )

    elapsed   = (datetime.datetime.utcnow() - sess.created_at).total_seconds()
    remaining = max(0, Config.QR_EXPIRY_SECONDS - elapsed)

    records = get_session_attendance(session_id)
    attendance_data = [{
        'student': User.query.get(r.student_id),
        'ip':      r.ip_address,
        'time':    r.marked_at,
    } for r in records]

    return render_template(
        'session_detail.html',
        sess            = sess,
        qr_image        = qr_image,
        qr_url          = qr_url,
        remaining_secs  = int(remaining),
        is_active       = remaining > 0,
        attendance_data = attendance_data,
        expiry_secs     = Config.QR_EXPIRY_SECONDS,
    )


@teacher.route('/session/<int:session_id>/attendance')
@teacher_required
def view_attendance(session_id):
    return redirect(url_for('teacher.session_detail', session_id=session_id))


# ─────────────────────────────────────────────────────────────
# NEW: Export attendance for ONE session as CSV
# ─────────────────────────────────────────────────────────────
@teacher.route('/session/<int:session_id>/export')
@teacher_required
def export_session_csv(session_id):
    """
    Download attendance for a single session as a CSV file.
    Columns: S.No, Student Username, Marked At, IP Address, Status
    """
    sess = AttendanceSession.query.get_or_404(session_id)

    # Security: only the teacher who owns this session can export
    if sess.teacher_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    records = get_session_attendance(session_id)

    # Build CSV in memory using StringIO (no file saved to disk)
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Header rows with session info ──
    writer.writerow(['AcadScan – Attendance Export'])
    writer.writerow(['Subject',    sess.subject])
    writer.writerow(['Session ID', f'#{sess.id}'])
    writer.writerow(['Teacher',    current_user.username])
    writer.writerow(['Date',       sess.created_at.strftime('%d %B %Y, %I:%M %p')])
    writer.writerow(['Teacher IP', sess.teacher_ip])
    writer.writerow(['Total Present', len(records)])
    writer.writerow([])  # blank separator row

    # ── Column headers ──
    writer.writerow(['S.No', 'Student Username', 'Marked At (UTC)', 'IP Address', 'Status'])

    # ── Data rows ──
    for i, record in enumerate(records, start=1):
        student = User.query.get(record.student_id)
        writer.writerow([
            i,
            student.username if student else 'Unknown',
            record.marked_at.strftime('%d-%m-%Y %H:%M:%S'),
            record.ip_address,
            'Present',
        ])

    # If no records, write a note
    if not records:
        writer.writerow(['—', 'No students marked attendance', '—', '—', '—'])

    # ── Build the Flask response as a file download ──
    output.seek(0)

    # Filename: AcadScan_DBMS_Session3.csv
    safe_subject = sess.subject.replace(' ', '_').replace('/', '-')
    filename = f'AcadScan_{safe_subject}_Session{sess.id}.csv'

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )


# ─────────────────────────────────────────────────────────────
# NEW: Export ALL sessions for this teacher as one CSV
# ─────────────────────────────────────────────────────────────
@teacher.route('/export/all')
@teacher_required
def export_all_csv():
    """
    Download ALL sessions created by this teacher as one combined CSV.
    Each session has its own section in the file.
    """
    sessions = AttendanceSession.query.filter_by(
        teacher_id=current_user.id
    ).order_by(AttendanceSession.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # ── File header ──
    writer.writerow(['AcadScan – Full Attendance Report'])
    writer.writerow(['Teacher',        current_user.username])
    writer.writerow(['Exported At',    datetime.datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')])
    writer.writerow(['Total Sessions', len(sessions)])
    writer.writerow([])

    for sess in sessions:
        records = get_session_attendance(sess.id)

        # Section header for each session
        writer.writerow([f'── Session #{sess.id} ──'])
        writer.writerow(['Subject',       sess.subject])
        writer.writerow(['Date',          sess.created_at.strftime('%d %B %Y, %I:%M %p')])
        writer.writerow(['Total Present', len(records)])
        writer.writerow([])

        # Column headers
        writer.writerow(['S.No', 'Student Username', 'Marked At (UTC)', 'IP Address', 'Status'])

        if records:
            for i, record in enumerate(records, start=1):
                student = User.query.get(record.student_id)
                writer.writerow([
                    i,
                    student.username if student else 'Unknown',
                    record.marked_at.strftime('%d-%m-%Y %H:%M:%S'),
                    record.ip_address,
                    'Present',
                ])
        else:
            writer.writerow(['—', 'No attendance recorded', '—', '—', '—'])

        writer.writerow([])  # blank line between sessions

    output.seek(0)

    filename = f'AcadScan_{current_user.username}_FullReport.csv'

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )