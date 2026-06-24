# models/attendance_model.py - Attendance record table

from models.user_model import db
import datetime

class Attendance(db.Model):
    """
    Represents one attendance record: a student marking present in a session.
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)

    # Which student marked attendance
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Which session they attended
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)

    # Student's IP at the time of scanning
    ip_address = db.Column(db.String(50), nullable=False)

    # Timestamp of attendance
    marked_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Session:{self.session_id}>'