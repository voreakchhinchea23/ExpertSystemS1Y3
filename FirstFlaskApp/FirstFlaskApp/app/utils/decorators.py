from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user

def permission_required(*required_permissions):
    """
    Decorator to protect routes that require at least ONE of the specified permissions.
    Usage:
        @permission_required('user.read')
        @permission_required('user.create') 
        @permission_required('user.create', 'user.update')  # user needs at least one
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            # Check if user has at least one of the required permissions
            if not any(current_user.has_permission(perm) for perm in required_permissions):
                flash("Access Denied: You have no permission to access this resource.", "danger")
                referrer = request.referrer
                if referrer:
                    return redirect(referrer)
                return redirect(url_for('tbl_users.index'))  

            return f(*args, **kwargs)
        return decorated_function
    return decorator