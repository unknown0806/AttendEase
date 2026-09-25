import os
import time
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from db import db
from models import (
    User, Class, Subject, ClassSubject, TeacherSubject,
    Student, Period, Attendance, AttendanceCorrection
)
from auth import role_required, get_current_user

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_avatar_file(file_storage, prefix='avatar'):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    clean_prefix = secure_filename(prefix).replace('.', '_')
    filename = f"{clean_prefix}_{int(time.time() * 1000)}.{ext}"
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file_storage.save(file_path)
    return f"/static/uploads/avatars/{filename}"

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_classes = Class.query.count()
    total_subjects = Subject.query.count()
    total_attendance_records = Attendance.query.count()
    total_corrections = AttendanceCorrection.query.count()
    
    recent_corrections = AttendanceCorrection.query.order_by(AttendanceCorrection.corrected_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_attendance_records=total_attendance_records,
        total_corrections=total_corrections,
        recent_corrections=recent_corrections
    )

# ==========================================
# ADMIN — MANAGE STUDENTS
# ==========================================
@admin_bp.route('/students', methods=['GET', 'POST'])
@role_required('admin')
def manage_students():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', 'student123').strip()
        roll_no = request.form.get('roll_no', '').strip()
        class_id = request.form.get('class_id', type=int)
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        father_name = request.form.get('father_name', '').strip()
        mother_name = request.form.get('mother_name', '').strip()
        father_phone = request.form.get('father_phone', '').strip()
        mother_phone = request.form.get('mother_phone', '').strip()
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        photo_url_input = request.form.get('photo_url', '').strip()
        photo_file = request.files.get('photo_file')

        if not name or not email or not roll_no or not class_id:
            flash('Name, email, roll number, and class are required.', 'danger')
            return redirect(url_for('admin.manage_students'))

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('admin.manage_students'))

        if Student.query.filter_by(roll_no=roll_no).first():
            flash('A student with this roll number already exists.', 'danger')
            return redirect(url_for('admin.manage_students'))

        # Handle photo
        final_photo = None
        saved_file = save_avatar_file(photo_file, prefix=f"stu_{roll_no}")
        if saved_file:
            final_photo = saved_file
        elif photo_url_input:
            final_photo = photo_url_input

        try:
            # Atomic creation of User and Student records
            new_user = User(
                name=name,
                email=email,
                role='student',
                phone=phone if phone else None,
                address=address if address else None,
                photo_url=final_photo,
                active=True
            )
            new_user.set_password(password if password else 'student123')
            db.session.add(new_user)
            db.session.flush() # populate user_id

            new_student = Student(
                user_id=new_user.user_id,
                roll_no=roll_no,
                class_id=class_id,
                father_name=father_name if father_name else None,
                mother_name=mother_name if mother_name else None,
                father_phone=father_phone if father_phone else None,
                mother_phone=mother_phone if mother_phone else None,
                dob=dob if dob else None,
                gender=gender if gender else None,
                blood_group=blood_group if blood_group else None
            )
            db.session.add(new_student)
            db.session.commit()

            flash(f'Student "{name}" ({roll_no}) registered successfully with full profile details!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')

        return redirect(url_for('admin.manage_students'))

    # GET filter handling
    class_filter = request.args.get('class_id', type=int)
    active_filter = request.args.get('active')

    query = Student.query.join(User)
    if class_filter:
        query = query.filter(Student.class_id == class_filter)
    if active_filter is not None and active_filter != '':
        is_active = active_filter.lower() in ['true', '1', 'yes']
        query = query.filter(User.active == is_active)

    students = query.order_by(Student.roll_no).all()
    classes = Class.query.order_by(Class.class_name).all()

    return render_template(
        'admin/manage_students.html',
        students=students,
        classes=classes,
        selected_class_id=class_filter,
        selected_active=active_filter
    )

@admin_bp.route('/students/<int:student_id>/edit', methods=['POST'])
@role_required('admin')
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = request.form.get('name', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    class_id = request.form.get('class_id', type=int)
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    father_name = request.form.get('father_name', '').strip()
    mother_name = request.form.get('mother_name', '').strip()
    father_phone = request.form.get('father_phone', '').strip()
    mother_phone = request.form.get('mother_phone', '').strip()
    dob = request.form.get('dob', '').strip()
    gender = request.form.get('gender', '').strip()
    blood_group = request.form.get('blood_group', '').strip()
    photo_url_input = request.form.get('photo_url', '').strip()
    photo_file = request.files.get('photo_file')

    if not name or not roll_no or not class_id:
        flash('Name, roll number, and class are required.', 'danger')
        return redirect(url_for('admin.manage_students'))

    # Check roll_no conflict
    existing = Student.query.filter(Student.roll_no == roll_no, Student.student_id != student_id).first()
    if existing:
        flash('Roll number already assigned to another student.', 'danger')
        return redirect(url_for('admin.manage_students'))

    # Handle photo update
    saved_file = save_avatar_file(photo_file, prefix=f"stu_{roll_no}")
    if saved_file:
        student.user.photo_url = saved_file
    elif photo_url_input:
        student.user.photo_url = photo_url_input

    student.user.name = name
    student.user.phone = phone if phone else None
    student.user.address = address if address else None
    student.roll_no = roll_no
    student.class_id = class_id
    student.father_name = father_name if father_name else None
    student.mother_name = mother_name if mother_name else None
    student.father_phone = father_phone if father_phone else None
    student.mother_phone = mother_phone if mother_phone else None
    student.dob = dob if dob else None
    student.gender = gender if gender else None
    student.blood_group = blood_group if blood_group else None
    db.session.commit()

    flash(f'Student "{name}" profile updated successfully.', 'success')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/students/<int:student_id>/deactivate', methods=['POST'])
@role_required('admin')
def toggle_student_active(student_id):
    student = Student.query.get_or_404(student_id)
    student.user.active = not student.user.active
    db.session.commit()

    status_str = "activated" if student.user.active else "deactivated (soft-deleted)"
    flash(f'Student "{student.user.name}" has been {status_str}.', 'info')
    return redirect(url_for('admin.manage_students'))

# ==========================================
# ADMIN — MANAGE TEACHERS
# ==========================================
@admin_bp.route('/teachers', methods=['GET', 'POST'])
@role_required('admin')
def manage_teachers():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', 'teacher123').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        qualification = request.form.get('qualification', '').strip()
        photo_url_input = request.form.get('photo_url', '').strip()
        photo_file = request.files.get('photo_file')

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('admin.manage_teachers'))

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('admin.manage_teachers'))

        # Handle photo
        final_photo = None
        saved_file = save_avatar_file(photo_file, prefix="faculty")
        if saved_file:
            final_photo = saved_file
        elif photo_url_input:
            final_photo = photo_url_input

        new_teacher = User(
            name=name,
            email=email,
            role='teacher',
            phone=phone if phone else None,
            address=address if address else None,
            department=department if department else None,
            designation=designation if designation else None,
            qualification=qualification if qualification else None,
            photo_url=final_photo,
            active=True
        )
        new_teacher.set_password(password if password else 'teacher123')
        db.session.add(new_teacher)
        db.session.commit()

        flash(f'Faculty member "{name}" registered successfully!', 'success')
        return redirect(url_for('admin.manage_teachers'))

    teachers = User.query.filter_by(role='teacher').order_by(User.name).all()
    classes = Class.query.order_by(Class.class_name).all()
    subjects = Subject.query.order_by(Subject.subject_name).all()
    assignments = TeacherSubject.query.all()

    return render_template(
        'admin/manage_teachers.html',
        teachers=teachers,
        classes=classes,
        subjects=subjects,
        assignments=assignments
    )

@admin_bp.route('/teachers/<int:teacher_id>/edit', methods=['POST'])
@role_required('admin')
def edit_teacher(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first_or_404()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    department = request.form.get('department', '').strip()
    designation = request.form.get('designation', '').strip()
    qualification = request.form.get('qualification', '').strip()
    photo_url_input = request.form.get('photo_url', '').strip()
    photo_file = request.files.get('photo_file')

    if not name or not email:
        flash('Name and email are required.', 'danger')
        return redirect(url_for('admin.manage_teachers'))

    existing = User.query.filter(User.email == email, User.user_id != teacher_id).first()
    if existing:
        flash('Email already used by another user.', 'danger')
        return redirect(url_for('admin.manage_teachers'))

    saved_file = save_avatar_file(photo_file, prefix=f"faculty_{teacher_id}")
    if saved_file:
        teacher.photo_url = saved_file
    elif photo_url_input:
        teacher.photo_url = photo_url_input

    teacher.name = name
    teacher.email = email
    teacher.phone = phone if phone else None
    teacher.address = address if address else None
    teacher.department = department if department else None
    teacher.designation = designation if designation else None
    teacher.qualification = qualification if qualification else None
    db.session.commit()

    flash(f'Faculty "{name}" profile updated successfully.', 'success')
    return redirect(url_for('admin.manage_teachers'))

@admin_bp.route('/teachers/<int:teacher_id>/assign', methods=['POST'])
@role_required('admin')
def assign_teacher(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first_or_404()
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)

    if not class_id or not subject_id:
        flash('Please select both a class and a subject.', 'danger')
        return redirect(url_for('admin.manage_teachers'))

    # Check if already assigned
    existing = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()

    if existing:
        flash('This teacher is already assigned to this class and subject.', 'warning')
        return redirect(url_for('admin.manage_teachers'))

    # Ensure class has this subject assigned in class_subjects as well
    cs = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if not cs:
        db.session.add(ClassSubject(class_id=class_id, subject_id=subject_id))

    assignment = TeacherSubject(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    )
    db.session.add(assignment)
    db.session.commit()

    flash(f'Teacher "{teacher.name}" assigned to class and subject successfully!', 'success')
    return redirect(url_for('admin.manage_teachers'))

@admin_bp.route('/teachers/assign', methods=['POST'])
@admin_bp.route('/teachers/assign-bulk', methods=['POST'])
@role_required('admin')
def assign_teacher_bulk():
    teacher_id = request.form.get('teacher_id', type=int)
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)

    if not teacher_id or not class_id or not subject_id:
        flash('Please select a teacher, class, and subject.', 'danger')
        return redirect(url_for('admin.manage_teachers'))

    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first_or_404()

    existing = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()

    if existing:
        flash('This teacher is already assigned to this class and subject.', 'warning')
        return redirect(url_for('admin.manage_teachers'))

    cs = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if not cs:
        db.session.add(ClassSubject(class_id=class_id, subject_id=subject_id))

    assignment = TeacherSubject(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    )
    db.session.add(assignment)
    db.session.commit()

    flash(f'Faculty "{teacher.name}" successfully assigned to class and subject!', 'success')
    return redirect(url_for('admin.manage_teachers'))

@admin_bp.route('/teachers/<int:teacher_id>/deactivate', methods=['POST'])
@role_required('admin')
def toggle_teacher_active(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first_or_404()
    teacher.active = not teacher.active
    db.session.commit()

    status_str = "activated" if teacher.active else "deactivated (soft-deleted)"
    flash(f'Teacher "{teacher.name}" has been {status_str}.', 'info')
    return redirect(url_for('admin.manage_teachers'))

# ==========================================
# ADMIN — MANAGE CLASSES & SUBJECTS
# ==========================================
@admin_bp.route('/classes', methods=['GET', 'POST'])
@role_required('admin')
def manage_classes():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_class':
            class_name = request.form.get('class_name', '').strip()
            if not class_name:
                flash('Class name is required.', 'danger')
            elif Class.query.filter_by(class_name=class_name).first():
                flash('Class with this name already exists.', 'danger')
            else:
                db.session.add(Class(class_name=class_name))
                db.session.commit()
                flash(f'Class "{class_name}" created successfully.', 'success')

        elif action == 'create_subject':
            subject_name = request.form.get('subject_name', '').strip()
            if not subject_name:
                flash('Subject name is required.', 'danger')
            elif Subject.query.filter_by(subject_name=subject_name).first():
                flash('Subject with this name already exists.', 'danger')
            else:
                db.session.add(Subject(subject_name=subject_name))
                db.session.commit()
                flash(f'Subject "{subject_name}" added successfully.', 'success')

        elif action == 'assign_subject':
            class_id = request.form.get('class_id', type=int)
            subject_id = request.form.get('subject_id', type=int)
            if not class_id or not subject_id:
                flash('Please select both a class and a subject.', 'danger')
            elif ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first():
                flash('Subject is already mapped to this class.', 'warning')
            else:
                db.session.add(ClassSubject(class_id=class_id, subject_id=subject_id))
                db.session.commit()
                flash('Subject mapped to class successfully.', 'success')

        return redirect(url_for('admin.manage_classes'))

    classes = Class.query.order_by(Class.class_name).all()
    subjects = Subject.query.order_by(Subject.subject_name).all()
    class_subjects = ClassSubject.query.all()

    return render_template(
        'admin/manage_classes.html',
        classes=classes,
        subjects=subjects,
        class_subjects=class_subjects
    )

# ==========================================
# ADMIN — VIEW ATTENDANCE
# ==========================================
@admin_bp.route('/attendance')
@role_required('admin')
def view_attendance():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    student_id = request.args.get('student_id', type=int)
    period_id = request.args.get('period_id', type=int)
    date_filter_str = request.args.get('date', '').strip()

    query = Attendance.query

    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    if teacher_id:
        query = query.filter(Attendance.marked_by == teacher_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if period_id:
        query = query.filter(Attendance.period_id == period_id)
    if date_filter_str:
        try:
            d_val = datetime.strptime(date_filter_str, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == d_val)
        except ValueError:
            pass

    records = query.order_by(Attendance.date.desc(), Attendance.created_at.desc()).all()

    # Group by session: (class_id, subject_id, period_id, date)
    sessions_map = {}
    for r in records:
        key = (r.class_id, r.subject_id, r.period_id, r.date)
        if key not in sessions_map:
            sessions_map[key] = {
                'sample_attendance_id': r.attendance_id,
                'class_id': r.class_id,
                'class_name': r.class_obj.class_name if r.class_obj else '',
                'subject_id': r.subject_id,
                'subject_name': r.subject.subject_name if r.subject else '',
                'period_id': r.period_id,
                'period_name': r.period.period_name if r.period else '',
                'date': r.date,
                'marked_by_name': r.marker.name if r.marker else '',
                'present_count': 0,
                'absent_count': 0,
                'total_count': 0,
                'locked': r.locked
            }
        if r.status == 'present':
            sessions_map[key]['present_count'] += 1
        else:
            sessions_map[key]['absent_count'] += 1
        sessions_map[key]['total_count'] += 1

    classes = Class.query.order_by(Class.class_name).all()
    subjects = Subject.query.order_by(Subject.subject_name).all()
    teachers = User.query.filter_by(role='teacher').order_by(User.name).all()
    periods = Period.query.order_by(Period.period_id).all()

    return render_template(
        'admin/view_attendance.html',
        sessions=list(sessions_map.values()),
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        periods=periods,
        selected_class_id=class_id,
        selected_subject_id=subject_id,
        selected_teacher_id=teacher_id,
        selected_period_id=period_id,
        selected_date=date_filter_str
    )

@admin_bp.route('/attendance/session')
@role_required('admin')
def view_session_detail():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    period_id = request.args.get('period_id', type=int)
    date_str = request.args.get('date', '').strip()

    if not class_id or not subject_id or not period_id or not date_str:
        flash('Missing session parameters.', 'danger')
        return redirect(url_for('admin.view_attendance'))

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date.', 'danger')
        return redirect(url_for('admin.view_attendance'))

    records = Attendance.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        period_id=period_id,
        date=att_date
    ).join(Student).order_by(Student.roll_no).all()

    target_class = Class.query.get_or_404(class_id)
    target_subject = Subject.query.get_or_404(subject_id)
    target_period = Period.query.get_or_404(period_id)

    return render_template(
        'admin/view_session_detail.html',
        records=records,
        target_class=target_class,
        target_subject=target_subject,
        target_period=target_period,
        target_date=date_str
    )

# ==========================================
# ADMIN — CORRECT LOCKED ATTENDANCE
# ==========================================
@admin_bp.route('/attendance/<int:attendance_id>/correct', methods=['GET', 'POST'])
@role_required('admin')
def correct_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    admin_id = session.get('user_id')

    if request.method == 'POST':
        new_status = request.form.get('new_status', '').strip().lower()
        reason = request.form.get('reason', '').strip()

        # Validation: reason mandatory, new_status valid
        if not reason:
            flash('Mandatory correction reason is required. Correction blocked.', 'danger')
            return render_template('admin/correct_attendance.html', attendance=attendance)

        if new_status not in ['present', 'absent']:
            flash('Invalid status selected.', 'danger')
            return render_template('admin/correct_attendance.html', attendance=attendance)

        if new_status == attendance.status:
            flash('Selected status is the same as current status. No change needed.', 'info')
            return redirect(url_for(
                'admin.view_session_detail',
                class_id=attendance.class_id,
                subject_id=attendance.subject_id,
                period_id=attendance.period_id,
                date=attendance.date.strftime('%Y-%m-%d')
            ))

        old_status = attendance.status

        try:
            # Single atomic operation:
            # 1. Log to attendance_corrections table
            correction = AttendanceCorrection(
                attendance_id=attendance.attendance_id,
                admin_id=admin_id,
                old_status=old_status,
                new_status=new_status,
                reason=reason,
                corrected_at=datetime.utcnow()
            )
            db.session.add(correction)

            # 2. Update attendance record and auto re-lock
            attendance.status = new_status
            attendance.locked = True
            db.session.commit()

            flash(f'Attendance for {attendance.student.user.name} ({attendance.student.roll_no}) corrected from {old_status.upper()} to {new_status.upper()} and re-locked successfully!', 'success')
            return redirect(url_for(
                'admin.view_session_detail',
                class_id=attendance.class_id,
                subject_id=attendance.subject_id,
                period_id=attendance.period_id,
                date=attendance.date.strftime('%Y-%m-%d')
            ))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving correction: {str(e)}', 'danger')

    return render_template('admin/correct_attendance.html', attendance=attendance)

# ==========================================
# ADMIN — AUDIT LOG & REPORTS
# ==========================================
@admin_bp.route('/audit-log')
@role_required('admin')
def audit_log():
    corrections = AttendanceCorrection.query.order_by(AttendanceCorrection.corrected_at.desc()).all()
    return render_template('admin/audit_log.html', corrections=corrections)

@admin_bp.route('/reports')
@role_required('admin')
def reports():
    students = Student.query.join(User).filter(User.active == True).all()
    classes = Class.query.all()
    subjects = Subject.query.all()
    
    # Calculate shortage list
    shortage_list = []
    for stu in students:
        total = Attendance.query.filter_by(student_id=stu.student_id).count()
        present = Attendance.query.filter_by(student_id=stu.student_id, status='present').count()
        if total > 0:
            pct = round((present / total) * 100, 1)
            if pct < 75.0:
                shortage_list.append({
                    'student': stu,
                    'total': total,
                    'present': present,
                    'percentage': pct
                })
                
    return render_template('admin/reports.html', students=students, classes=classes, subjects=subjects, shortage_list=shortage_list)

@admin_bp.route('/notices', methods=['GET', 'POST'])
@role_required('admin')
def notices():
    if request.method == 'POST':
        title = request.form.get('title')
        flash(f'Notice "{title}" broadcasted to all campus portals!', 'success')
        return redirect(url_for('admin.notices'))
    return render_template('admin/notices.html')

@admin_bp.route('/timetable')
@role_required('admin')
def timetable():
    classes = Class.query.all()
    periods = Period.query.order_by(Period.period_id).all()
    return render_template('admin/timetable.html', classes=classes, periods=periods)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@role_required('admin')
def profile():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        photo_url_input = request.form.get('photo_url', '').strip()
        photo_file = request.files.get('photo_file')

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('admin.profile'))

        existing = User.query.filter(User.email == email, User.user_id != user.user_id).first()
        if existing:
            flash('This email is already registered to another account.', 'danger')
            return redirect(url_for('admin.profile'))

        # Check password update if requested
        if new_password:
            if not current_password or not user.check_password(current_password):
                flash('Current password is required and must be correct to set a new password.', 'danger')
                return redirect(url_for('admin.profile'))
            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'danger')
                return redirect(url_for('admin.profile'))
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return redirect(url_for('admin.profile'))
            user.set_password(new_password)

        # Photo handling
        saved_file = save_avatar_file(photo_file, prefix=f"admin_{user.user_id}")
        if saved_file:
            user.photo_url = saved_file
        elif photo_url_input:
            user.photo_url = photo_url_input

        user.name = name
        user.email = email
        user.phone = phone if phone else None
        user.address = address if address else None
        db.session.commit()

        # Update session display name
        session['user_name'] = user.name
        flash('Admin profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html', user=user)

