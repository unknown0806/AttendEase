from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
from auth import get_current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', email=email)

        if not user.active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return render_template('login.html', email=email)

        # Set session
        session.clear()
        session['user_id'] = user.user_id
        session['role'] = user.role
        session['user_name'] = user.name
        session.permanent = True

        flash(f'Welcome back, {user.name}!', 'success')

        # Redirect to appropriate dashboard
        if user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))
