from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import func
from db import db
from models import User, Student
from auth import get_current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and 'user_id' in session:
        role = session.get('role')
        if role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        # Properly fetch payload whether submitted as JSON, form data, or request values
        data = request.get_json(silent=True) if request.is_json else (request.form or request.values or {})
        
        # Properly fetch email across all standard naming conventions
        email = (
            data.get('email') or 
            data.get('email_address') or 
            data.get('username') or 
            data.get('user_id') or 
            request.form.get('email') or 
            request.values.get('email') or 
            ''
        ).strip()
        
        # Properly fetch password / email password across standard naming conventions
        password = (
            data.get('password') or 
            data.get('email_password') or 
            data.get('emailPassword') or 
            data.get('pass') or 
            request.form.get('password') or 
            request.form.get('email_password') or 
            request.values.get('password') or 
            request.values.get('email_password') or 
            ''
        )

        is_api_request = request.is_json or request.headers.get('Accept') == 'application/json'

        if not email or not password:
            if is_api_request:
                return jsonify({'error': 'Email and password are required.'}), 400
            flash('Email and password are required.', 'danger')
            return render_template('login.html', email=email)

        # Look up user: case-insensitive email match first
        user = User.query.filter(func.lower(User.email) == email.lower()).first()

        # Fallback: support login via Student Roll Number
        if not user:
            student = Student.query.filter(func.lower(Student.roll_no) == email.lower()).first()
            if student and student.user:
                user = student.user

        # Fallback: support login via numeric user ID
        if not user and email.isdigit():
            user = db.session.get(User, int(email))

        # Fallback: exact email lookup
        if not user:
            user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            if is_api_request:
                return jsonify({'error': 'Invalid email or password.'}), 401
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', email=email)

        if not user.active:
            if is_api_request:
                return jsonify({'error': 'Your account has been deactivated. Please contact an administrator.'}), 403
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return render_template('login.html', email=email)

        # Set session
        session.clear()
        session['user_id'] = user.user_id
        session['role'] = user.role
        session['user_name'] = user.name
        session.permanent = True

        if is_api_request:
            return jsonify({
                'message': f'Welcome back, {user.name}!',
                'user_id': user.user_id,
                'name': user.name,
                'role': user.role
            }), 200

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
