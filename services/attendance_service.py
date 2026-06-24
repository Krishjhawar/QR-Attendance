# services/attendance_service.py

from models.user_model import db
from models.attendance_model import Attendance
from models.session_model import AttendanceSession


def mark_attendance(student_id, session_id, ip_address):
    r = Attendance(student_id=student_id, session_id=session_id, ip_address=ip_address)
    db.session.add(r)
    db.session.commit()
    return r


def get_session_attendance(session_id):
    return Attendance.query.filter_by(session_id=session_id).all()


def get_student_attendance(student_id):
    return Attendance.query.filter_by(student_id=student_id).all()


def create_session(teacher_id, teacher_ip, subject='General'):
    s = AttendanceSession(teacher_id=teacher_id, teacher_ip=teacher_ip, subject=subject)
    db.session.add(s)
    db.session.commit()
    return s