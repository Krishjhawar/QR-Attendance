# models/user_model.py - User table definition

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# db instance imported from app in __init__ or passed in
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    Represents a user (teacher or student).
    Roles: 'teacher' or 'student'
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # plain text for demo simplicity
    role = db.Column(db.String(20), nullable=False)       # 'teacher' or 'student'

    # Track if this user is currently logged in (single session enforcement)
    is_active_session = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'