from flask import session, redirect, url_for, flash
from functools import wraps

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You currently do not have access to this area', 'danger')
            return redirect(url_for('auth.login'))
    return wrap

# Ensure user is Admin


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['user_type'] == "Admin":
            return f(*args, **kwargs)
        else:
            flash('You currently do not have admin access to this area', 'danger')
            return redirect(url_for('main.home'))
    return wrap

# route decorater


def route(*a, **kw):
    kw['strict_slashes'] = kw.get('strict_slashes', False)
    return app.route(*a, **kw)

# decorater for files


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
