from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user
from models import User, db


def login_required_redirect(f):
    """Decorator that redirects to login page if user is not authenticated"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def create_user(username, email, password):
    """Create a new user with hashed password"""
    if User.query.filter_by(username=username).first():
        return None, "Username already exists"

    if User.query.filter_by(email=email).first():
        return None, "Email already exists"

    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return user, "User created successfully"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"


def validate_password(password):
    """Basic password validation"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    return True, "Password is valid"


def validate_email(email):
    """Basic email validation"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return True, "Email is valid"
    return False, "Invalid email format"


def validate_username(username):
    """Basic username validation"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 20:
        return False, "Username must be less than 20 characters"

    import re

    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, "Username is valid"
