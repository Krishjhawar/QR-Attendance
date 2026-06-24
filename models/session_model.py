# models/session_model.py - Attendance session table

from models.user_model import db
import datetime

class AttendanceSession(db.Model):
    """
    Represents a QR attendance session created by a teacher.
    Each session has a unique ID embedded in the QR code.
    """
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)

    # Teacher who created this session
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # When the session was created (used for expiry check)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Teacher's IP address when session was created
    teacher_ip = db.Column(db.String(50), nullable=False)

    # Subject/label for the session (optional but useful)
    subject = db.Column(db.String(100), default='General')

    def __repr__(self):
        return f'<Session {self.id} by Teacher {self.teacher_id}>'