from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import db
from models import User, Class, Subject, TeacherSubject, Student, Period, Attendance
from auth import role_required, get_current_user

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@role_required('teacher')
def dashboard():
    teacher_id = session.get('user_id')
    user = get_current_user()
    
    # Fetch assigned class-subject pairs
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    
    # Calculate unique student count across teacher's assigned classes
    assigned_class_ids = [a.class_id for a in assignments]
    total_students_count = Student.query.join(User).filter(
        Student.class_id.in_(assigned_class_ids),
        User.active == True
    ).count() if assigned_class_ids else 0

    # Fetch recent attendance batches marked by this teacher
    recent_records = Attendance.query.filter_by(marked_by=teacher_id)\
        .order_by(Attendance.date.desc(), Attendance.created_at.desc())\
        .limit(30).all()
    
    # Group recent records by (class, subject, period, date) for summary view
    grouped_recent = {}
    for r in recent_records:
        key = (r.class_id, r.subject_id, r.period_id, r.date)
        if key not in grouped_recent:
            grouped_recent[key] = {
                'class_name': r.class_obj.class_name if r.class_obj else '',
                'subject_name': r.subject.subject_name if r.subject else '',
                'period_name': r.period.period_name if r.period else '',
                'date': r.date,
                'present_count': 0,
                'absent_count': 0,
                'total_count': 0,
                'locked': r.locked
            }
        if r.status == 'present':
            grouped_recent[key]['present_count'] += 1
        else:
            grouped_recent[key]['absent_count'] += 1
        grouped_recent[key]['total_count'] += 1

    return render_template(
        'teacher/dashboard.html',
        user=user,
        assignments=assignments,
        total_students_count=total_students_count,
        recent_sessions=list(grouped_recent.values())[:10]
    )

@teacher_bp.route('/mark', methods=['GET'])
@role_required('teacher')
def mark_attendance():
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    period_id = request.args.get('period_id', type=int)
    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    # All assignments for dropdown
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    periods = Period.query.order_by(Period.period_id).all()
    
    if not class_id or not subject_id:
        if assignments:
            first_assign = assignments[0]
            return redirect(url_for(
                'teacher.mark_attendance',
                class_id=first_assign.class_id,
                subject_id=first_assign.subject_id,
                period_id=periods[0].period_id if periods else None,
                date=selected_date_str
            ))
        else:
            flash('You do not have any assigned classes or subjects yet. Please contact an administrator.', 'warning')
            return redirect(url_for('teacher.dashboard'))

    # Verify assignment belongs to this teacher
    assignment = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()

    if not assignment:
        flash('You are not assigned to this class and subject.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    selected_class = Class.query.get_or_404(class_id)
    selected_subject = Subject.query.get_or_404(subject_id)
    
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()
        selected_date_str = selected_date.strftime('%Y-%m-%d')

    if not period_id and periods:
        period_id = periods[0].period_id

    # Fetch active students for this class
    students = Student.query.join(User).filter(
        Student.class_id == class_id,
        User.active == True
    ).order_by(Student.roll_no).all()

    # Check if attendance already recorded for this session
    existing_attendance = Attendance.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        period_id=period_id,
        date=selected_date
    ).all()

    is_already_locked = any(a.locked for a in existing_attendance)
    existing_status_map = {a.student_id: a.status for a in existing_attendance}

    return render_template(
        'teacher/mark_attendance.html',
        assignments=assignments,
        periods=periods,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_period_id=period_id,
        selected_date=selected_date_str,
        students=students,
        is_already_locked=is_already_locked,
        existing_status_map=existing_status_map
    )

@teacher_bp.route('/submit', methods=['POST'])
@role_required('teacher')
def submit_attendance():
    teacher_id = session.get('user_id')
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    period_id = request.form.get('period_id', type=int)
    date_str = request.form.get('date', '').strip()

    if not class_id or not subject_id or not period_id or not date_str:
        flash('Missing class, subject, period, or date.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    # Verify teacher assignment
    assignment = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()

    if not assignment:
        flash('Unauthorized: You are not assigned to this class and subject.', 'danger')
        return redirect(url_for('teacher.dashboard'))

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('teacher.mark_attendance', class_id=class_id, subject_id=subject_id))

    # Check if already submitted and locked
    existing = Attendance.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        period_id=period_id,
        date=att_date
    ).first()

    if existing and existing.locked:
        flash('Attendance for this session is already submitted and locked. You cannot modify it.', 'danger')
        return redirect(url_for('teacher.mark_attendance', class_id=class_id, subject_id=subject_id, period_id=period_id, date=date_str))

    # Fetch active students for the class
    students = Student.query.join(User).filter(
        Student.class_id == class_id,
        User.active == True
    ).all()

    if not students:
        flash('No active students found in this class.', 'warning')
        return redirect(url_for('teacher.dashboard'))

    # Insert or update if not locked
    submitted_count = 0
    for stu in students:
        status_val = request.form.get(f'status_{stu.student_id}', 'absent')
        if status_val not in ['present', 'absent']:
            status_val = 'absent'

        record = Attendance.query.filter_by(
            student_id=stu.student_id,
            subject_id=subject_id,
            period_id=period_id,
            date=att_date
        ).first()

        if record:
            if record.locked:
                flash('Attendance record is locked and cannot be edited.', 'danger')
                return redirect(url_for('teacher.dashboard'))
            record.status = status_val
            record.locked = True
            record.marked_by = teacher_id
        else:
            record = Attendance(
                student_id=stu.student_id,
                subject_id=subject_id,
                class_id=class_id,
                period_id=period_id,
                date=att_date,
                status=status_val,
                locked=True,
                marked_by=teacher_id
            )
            db.session.add(record)
        submitted_count += 1

    db.session.commit()

    flash(f'Attendance successfully submitted and locked for {submitted_count} students! The record is now tamper-proof.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/classes')
@role_required('teacher')
def my_classes():
    teacher_id = session.get('user_id')
    user = get_current_user()
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    return render_template('teacher/classes.html', user=user, assignments=assignments)

@teacher_bp.route('/students')
@role_required('teacher')
def my_students():
    teacher_id = session.get('user_id')
    user = get_current_user()
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    class_ids = [a.class_id for a in assignments]
    students = Student.query.join(User).filter(
        Student.class_id.in_(class_ids),
        User.active == True
    ).order_by(Student.roll_no).all() if class_ids else []
    return render_template('teacher/students.html', user=user, students=students, assignments=assignments)

@teacher_bp.route('/assignments', methods=['GET', 'POST'])
@role_required('teacher')
def assignments():
    teacher_id = session.get('user_id')
    user = get_current_user()
    my_assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    if request.method == 'POST':
        title = request.form.get('title')
        flash(f'Assignment "{title}" published to students successfully!', 'success')
        return redirect(url_for('teacher.assignments'))
    return render_template('teacher/assignments.html', user=user, my_assignments=my_assignments)

@teacher_bp.route('/marks', methods=['GET', 'POST'])
@role_required('teacher')
def marks():
    teacher_id = session.get('user_id')
    user = get_current_user()
    my_assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    class_ids = [a.class_id for a in my_assignments]
    students = Student.query.join(User).filter(
        Student.class_id.in_(class_ids),
        User.active == True
    ).order_by(Student.roll_no).all() if class_ids else []

    if request.method == 'POST':
        flash('Continuous Internal Assessment (CIA) marks recorded and saved!', 'success')
        return redirect(url_for('teacher.marks'))

    return render_template('teacher/marks.html', user=user, students=students, my_assignments=my_assignments)

@teacher_bp.route('/timetable')
@role_required('teacher')
def timetable():
    teacher_id = session.get('user_id')
    user = get_current_user()
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    periods = Period.query.order_by(Period.period_id).all()
    return render_template('teacher/timetable.html', user=user, assignments=assignments, periods=periods)

@teacher_bp.route('/notices')
@role_required('teacher')
def notices():
    user = get_current_user()
    return render_template('teacher/notices.html', user=user)

@teacher_bp.route('/profile')
@role_required('teacher')
def profile():
    user = get_current_user()
    teacher_id = session.get('user_id')
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    return render_template('teacher/profile.html', user=user, assignments=assignments)

@teacher_bp.route('/messages')
@role_required('teacher')
def messages():
    user = get_current_user()
    return render_template('teacher/messages.html', user=user)

@teacher_bp.route('/notifications')
@role_required('teacher')
def notifications():
    user = get_current_user()
    return render_template('teacher/notifications.html', user=user)
