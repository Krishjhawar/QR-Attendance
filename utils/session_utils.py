# utils/session_utils.py - Single session enforcement utilities

from models.user_model import db, User

def mark_user_logged_in(user):
    """Mark a user as having an active session in the database."""
    user.is_active_session = True
    db.session.commit()

def mark_user_logged_out(user):
    """Mark a user's session as ended."""
    user.is_active_session = False
    db.session.commit()

def is_user_already_logged_in(user):
    """
    Check if this user already has an active session.
    Used to enforce single-session login.
    Returns True if another session is active.
    """
    return user.is_active_session