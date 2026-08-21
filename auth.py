from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from models import User

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'unauthorized, login required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verify user is active
        user = get_current_user()
        if not user or not user.active:
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({'error': 'account is inactive'}), 403
            flash('Your account has been deactivated. Please contact administrator.', 'danger')
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'unauthorized, login required'}), 401
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            
            user = get_current_user()
            if not user or not user.active:
                session.clear()
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'account is inactive'}), 403
                flash('Account is inactive.', 'danger')
                return redirect(url_for('auth.login'))
                
            user_role = session.get('role')
            if user_role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': f'forbidden: requires one of {allowed_roles}'}), 403
                flash('You do not have permission to access this resource.', 'danger')
                
                # Redirect to appropriate dashboard based on actual role
                if user_role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user_role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
