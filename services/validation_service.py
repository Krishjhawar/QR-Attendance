# services/validation_service.py

import datetime
from models.session_model import AttendanceSession
from models.attendance_model import Attendance
from utils.ip_utils import compare_network
from config import Config


def validate_attendance(session_id: int, student_id: int, student_ip: str):
    """
    Full validation pipeline.

    Checks:
      1. Session exists
      2. QR not expired
      3. No duplicate (returns sentinel 'already_marked')
      4. Same /24 network (hotspot-safe)

    Returns:
      (True,  None)            — all checks passed
      (False, error_string)    — first failure reason
      (False, 'already_marked')— duplicate sentinel for UI
    """
    session = AttendanceSession.query.get(session_id)
    if not session:
        return False, 'Session not found. QR code may be invalid or deleted.'

    elapsed = (datetime.datetime.utcnow() - session.created_at).total_seconds()
    if elapsed > Config.QR_EXPIRY_SECONDS:
        mins = Config.QR_EXPIRY_SECONDS // 60
        return False, f'QR code expired ({mins}-minute limit). Ask teacher to generate a new one.'

    if Attendance.query.filter_by(student_id=student_id, session_id=session_id).first():
        return False, 'already_marked'

    if not compare_network(session.teacher_ip, student_ip):
        teacher_subnet  = '.'.join(session.teacher_ip.split('.')[:3]) + '.x'
        return False, (
            f'Network mismatch. You must be on the same WiFi/hotspot as your teacher. '
            f'Teacher subnet: {teacher_subnet} | Your IP: {student_ip}'
        )

    return True, None