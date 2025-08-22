from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def role_required(*roles):
    """Usage: @role_required('absolute_admin', 'country_admin')"""
    allowed = set(roles)

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # current_user.is_authenticated is guaranteed by @login_required
            if not current_user.is_authenticated or current_user.role not in allowed:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function

    return decorator
