from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from db import db
from models import (
    User, Class, Subject, ClassSubject, TeacherSubject,
    Student, Period, Attendance, AttendanceCorrection
)
from auth import role_required, login_required, get_current_user

api_bp = Blueprint('api', __name__)

# ----------------------------------------------------
# 1 & 2. Auth API Endpoints
# ----------------------------------------------------
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid email or password'}), 401

    if not user.active:
        return jsonify({'error': 'account is inactive'}), 403

    session.clear()
    session['user_id'] = user.user_id
    session['role'] = user.role
    session['user_name'] = user.name
    session.permanent = True

    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'role': user.role
    }), 200

@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    session.clear()
    return jsonify({'message': 'logged out'}), 200


# ----------------------------------------------------
# 3, 4, 5. Teacher Attendance API Endpoints
# ----------------------------------------------------
@api_bp.route('/teacher/classes', methods=['GET'])
@role_required('teacher')
def api_teacher_classes():
    teacher_id = session.get('user_id')
    assignments = TeacherSubject.query.filter_by(teacher_id=teacher_id).all()
    results = []
    for a in assignments:
        results.append({
            'class_id': a.class_id,
            'class_name': a.class_obj.class_name if a.class_obj else None,
            'subject_id': a.subject_id,
            'subject_name': a.subject.subject_name if a.subject else None
        })
    return jsonify(results), 200

@api_bp.route('/teacher/students', methods=['GET'])
@role_required('teacher')
def api_teacher_students():
    teacher_id = session.get('user_id')
    class_id = request.args.get('class_id', type=int)

    if not class_id:
        return jsonify({'error': 'class_id query parameter required'}), 400

    target_class = Class.query.get(class_id)
    if not target_class:
        return jsonify({'error': 'class not found'}), 404

    # Verify teacher is assigned to this class
    assigned = TeacherSubject.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
    if not assigned:
        return jsonify({'error': 'teacher not assigned to this class'}), 403

    students = Student.query.join(User).filter(
        Student.class_id == class_id,
        User.active == True
    ).order_by(Student.roll_no).all()

    results = [{
        'student_id': s.student_id,
        'name': s.user.name,
        'roll_no': s.roll_no
    } for s in students]

    return jsonify(results), 200

@api_bp.route('/teacher/attendance', methods=['POST'])
@role_required('teacher')
def api_teacher_submit_attendance():
    teacher_id = session.get('user_id')
    data = request.get_json(silent=True) or {}

    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    period_id = data.get('period_id')
    date_str = data.get('date')
    records = data.get('records', [])

    if not class_id or not subject_id or not period_id or not date_str or not records:
        return jsonify({'error': 'class_id, subject_id, period_id, date, and non-empty records required'}), 400

    # Verify teacher assignment
    assigned = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()
    if not assigned:
        return jsonify({'error': 'teacher not assigned to this class/subject'}), 403

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'invalid date format (YYYY-MM-DD)'}), 400

    # Check for conflict
    existing_locked = Attendance.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        period_id=period_id,
        date=att_date,
        locked=True
    ).first()
    if existing_locked:
        return jsonify({'error': 'attendance already submitted and locked for this session'}), 409

    count = 0
    for r in records:
        stu_id = r.get('student_id')
        status = r.get('status', '').lower()
        if not stu_id or status not in ['present', 'absent']:
            return jsonify({'error': f'invalid record structure or status: {r}'}), 400

        existing = Attendance.query.filter_by(
            student_id=stu_id,
            subject_id=subject_id,
            period_id=period_id,
            date=att_date
        ).first()

        if existing:
            existing.status = status
            existing.locked = True
            existing.marked_by = teacher_id
        else:
            new_record = Attendance(
                student_id=stu_id,
                subject_id=subject_id,
                class_id=class_id,
                period_id=period_id,
                date=att_date,
                status=status,
                locked=True,
                marked_by=teacher_id
            )
            db.session.add(new_record)
        count += 1

    db.session.commit()
    return jsonify({'message': 'attendance submitted and locked', 'count': count}), 201


# ----------------------------------------------------
# 6. Student Attendance API Endpoint
# ----------------------------------------------------
@api_bp.route('/student/attendance', methods=['GET'])
@role_required('student')
def api_student_attendance():
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'student record not found'}), 404

    class_subjects = ClassSubject.query.filter_by(class_id=student.class_id).all()
    results = []

    for cs in class_subjects:
        sub = cs.subject
        records = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=sub.subject_id
        ).all()

        total = len(records)
        present = sum(1 for r in records if r.status == 'present')
        pct = round((present / total) * 100, 1) if total > 0 else 100.0
        alert = pct < 75.0 if total > 0 else False

        results.append({
            'subject_id': sub.subject_id,
            'subject_name': sub.subject_name,
            'present': present,
            'total': total,
            'percentage': pct,
            'alert': alert
        })

    return jsonify(results), 200


# ----------------------------------------------------
# 7, 8, 9, 10. Admin Students Management API
# ----------------------------------------------------
@api_bp.route('/admin/students', methods=['GET'])
@role_required('admin')
def api_admin_get_students():
    class_id = request.args.get('class_id', type=int)
    active_str = request.args.get('active')

    query = Student.query.join(User)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if active_str is not None and active_str != '':
        is_active = active_str.lower() in ['true', '1']
        query = query.filter(User.active == is_active)

    students = query.order_by(Student.roll_no).all()
    results = [{
        'student_id': s.student_id,
        'name': s.user.name,
        'roll_no': s.roll_no,
        'class_name': s.class_obj.class_name if s.class_obj else None,
        'active': s.user.active
    } for s in students]

    return jsonify(results), 200

@api_bp.route('/admin/students', methods=['POST'])
@role_required('admin')
def api_admin_add_student():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', 'temp123').strip()
    roll_no = data.get('roll_no', '').strip()
    class_id = data.get('class_id')

    if not name or not email or not roll_no or not class_id:
        return jsonify({'error': 'name, email, roll_no, and class_id are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already exists'}), 409

    if Student.query.filter_by(roll_no=roll_no).first():
        return jsonify({'error': 'roll_no already exists'}), 409

    target_class = Class.query.get(class_id)
    if not target_class:
        return jsonify({'error': 'class_id not found'}), 404

    new_user = User(name=name, email=email, role='student', active=True)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.flush()

    new_student = Student(user_id=new_user.user_id, roll_no=roll_no, class_id=class_id)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'student_id': new_student.student_id, 'message': 'student added'}), 201

@api_bp.route('/admin/students/<int:student_id>', methods=['PUT'])
@role_required('admin')
def api_admin_edit_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'student not found'}), 404

    data = request.get_json(silent=True) or {}
    name = data.get('name')
    roll_no = data.get('roll_no')
    class_id = data.get('class_id')

    if name is not None:
        student.user.name = name.strip()
    if roll_no is not None:
        roll_no = roll_no.strip()
        existing = Student.query.filter(Student.roll_no == roll_no, Student.student_id != student_id).first()
        if existing:
            return jsonify({'error': 'roll_no already exists'}), 409
        student.roll_no = roll_no
    if class_id is not None:
        target_class = Class.query.get(class_id)
        if not target_class:
            return jsonify({'error': 'class_id not found'}), 404
        student.class_id = class_id

    db.session.commit()
    return jsonify({'message': 'student updated'}), 200

@api_bp.route('/admin/students/<int:student_id>/deactivate', methods=['PATCH'])
@role_required('admin')
def api_admin_deactivate_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'student not found'}), 404

    student.user.active = False
    db.session.commit()
    return jsonify({'message': 'student deactivated'}), 200


# ----------------------------------------------------
# 11, 12, 13, 14, 15. Admin Teachers Management API
# ----------------------------------------------------
@api_bp.route('/admin/teachers', methods=['GET'])
@role_required('admin')
def api_admin_get_teachers():
    active_str = request.args.get('active')
    query = User.query.filter_by(role='teacher')
    if active_str is not None and active_str != '':
        is_active = active_str.lower() in ['true', '1']
        query = query.filter_by(active=is_active)

    teachers = query.order_by(User.name).all()
    results = [{
        'user_id': t.user_id,
        'name': t.name,
        'email': t.email,
        'active': t.active
    } for t in teachers]

    return jsonify(results), 200

@api_bp.route('/admin/teachers', methods=['POST'])
@role_required('admin')
def api_admin_add_teacher():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', 'temp123').strip()

    if not name or not email:
        return jsonify({'error': 'name and email are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email exists'}), 409

    new_teacher = User(name=name, email=email, role='teacher', active=True)
    new_teacher.set_password(password)
    db.session.add(new_teacher)
    db.session.commit()

    return jsonify({'user_id': new_teacher.user_id, 'message': 'teacher added'}), 201

@api_bp.route('/admin/teachers/<int:teacher_id>', methods=['PUT'])
@role_required('admin')
def api_admin_edit_teacher(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first()
    if not teacher:
        return jsonify({'error': 'teacher not found'}), 404

    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')

    if name is not None:
        teacher.name = name.strip()
    if email is not None:
        email = email.strip()
        existing = User.query.filter(User.email == email, User.user_id != teacher_id).first()
        if existing:
            return jsonify({'error': 'email exists'}), 409
        teacher.email = email

    db.session.commit()
    return jsonify({'message': 'teacher updated'}), 200

@api_bp.route('/admin/teachers/<int:teacher_id>/assign', methods=['POST'])
@role_required('admin')
def api_admin_assign_teacher(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first()
    if not teacher:
        return jsonify({'error': 'teacher not found'}), 404

    data = request.get_json(silent=True) or {}
    subject_id = data.get('subject_id')
    class_id = data.get('class_id')

    if not subject_id or not class_id:
        return jsonify({'error': 'subject_id and class_id are required'}), 400

    if not Subject.query.get(subject_id) or not Class.query.get(class_id):
        return jsonify({'error': 'subject or class not found'}), 404

    existing = TeacherSubject.query.filter_by(
        teacher_id=teacher_id,
        subject_id=subject_id,
        class_id=class_id
    ).first()

    if existing:
        return jsonify({'error': 'assignment already exists'}), 409

    cs = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if not cs:
        db.session.add(ClassSubject(class_id=class_id, subject_id=subject_id))

    assignment = TeacherSubject(teacher_id=teacher_id, subject_id=subject_id, class_id=class_id)
    db.session.add(assignment)
    db.session.commit()

    return jsonify({'message': 'teacher assigned'}), 201

@api_bp.route('/admin/teachers/<int:teacher_id>/deactivate', methods=['PATCH'])
@role_required('admin')
def api_admin_deactivate_teacher(teacher_id):
    teacher = User.query.filter_by(user_id=teacher_id, role='teacher').first()
    if not teacher:
        return jsonify({'error': 'teacher not found'}), 404

    teacher.active = False
    db.session.commit()
    return jsonify({'message': 'teacher deactivated'}), 200


# ----------------------------------------------------
# 16, 17, 18, 19, 20. Admin Classes & Subjects Management API
# ----------------------------------------------------
@api_bp.route('/admin/classes', methods=['GET'])
@role_required('admin')
def api_admin_get_classes():
    classes = Class.query.order_by(Class.class_name).all()
    return jsonify([{'class_id': c.class_id, 'class_name': c.class_name} for c in classes]), 200

@api_bp.route('/admin/classes', methods=['POST'])
@role_required('admin')
def api_admin_create_class():
    data = request.get_json(silent=True) or {}
    class_name = data.get('class_name', '').strip()
    if not class_name:
        return jsonify({'error': 'class_name required'}), 400

    if Class.query.filter_by(class_name=class_name).first():
        return jsonify({'error': 'class_name already exists'}), 409

    new_class = Class(class_name=class_name)
    db.session.add(new_class)
    db.session.commit()

    return jsonify({'class_id': new_class.class_id, 'message': 'class created'}), 201

@api_bp.route('/admin/subjects', methods=['GET'])
@role_required('admin')
def api_admin_get_subjects():
    subjects = Subject.query.order_by(Subject.subject_name).all()
    return jsonify([{'subject_id': s.subject_id, 'subject_name': s.subject_name} for s in subjects]), 200

@api_bp.route('/admin/subjects', methods=['POST'])
@role_required('admin')
def api_admin_create_subject():
    data = request.get_json(silent=True) or {}
    subject_name = data.get('subject_name', '').strip()
    if not subject_name:
        return jsonify({'error': 'subject_name required'}), 400

    if Subject.query.filter_by(subject_name=subject_name).first():
        return jsonify({'error': 'subject_name exists'}), 409

    new_subject = Subject(subject_name=subject_name)
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({'subject_id': new_subject.subject_id, 'message': 'subject added'}), 201

@api_bp.route('/admin/classes/<int:class_id>/subjects', methods=['POST'])
@role_required('admin')
def api_admin_assign_subject_to_class(class_id):
    if not Class.query.get(class_id):
        return jsonify({'error': 'class not found'}), 404

    data = request.get_json(silent=True) or {}
    subject_id = data.get('subject_id')
    if not subject_id or not Subject.query.get(subject_id):
        return jsonify({'error': 'subject not found'}), 404

    if ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first():
        return jsonify({'error': 'already assigned'}), 409

    db.session.add(ClassSubject(class_id=class_id, subject_id=subject_id))
    db.session.commit()

    return jsonify({'message': 'subject assigned to class'}), 201


# ----------------------------------------------------
# 21, 22, 23, 24. Admin View & Correct Attendance API
# ----------------------------------------------------
@api_bp.route('/admin/attendance', methods=['GET'])
@role_required('admin')
def api_admin_get_attendance():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    student_id = request.args.get('student_id', type=int)
    period_id = request.args.get('period_id', type=int)
    date_str = request.args.get('date', '').strip()

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
    if date_str:
        try:
            d_val = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == d_val)
        except ValueError:
            return jsonify({'error': 'invalid date format'}), 400

    records = query.order_by(Attendance.date.desc()).all()

    # Group records by session
    sessions_map = {}
    for r in records:
        key = (r.class_id, r.subject_id, r.period_id, r.date)
        if key not in sessions_map:
            sessions_map[key] = {
                'attendance_id': r.attendance_id,
                'class_name': r.class_obj.class_name if r.class_obj else '',
                'subject_name': r.subject.subject_name if r.subject else '',
                'period_name': r.period.period_name if r.period else '',
                'date': r.date.strftime('%Y-%m-%d'),
                'present_count': 0,
                'absent_count': 0,
                'locked': r.locked
            }
        if r.status == 'present':
            sessions_map[key]['present_count'] += 1
        else:
            sessions_map[key]['absent_count'] += 1

    return jsonify(list(sessions_map.values())), 200

@api_bp.route('/admin/attendance/<int:attendance_id>', methods=['GET'])
@role_required('admin')
def api_admin_get_single_attendance(attendance_id):
    r = Attendance.query.get(attendance_id)
    if not r:
        return jsonify({'error': 'attendance record not found'}), 404

    return jsonify({
        'attendance_id': r.attendance_id,
        'student_id': r.student_id,
        'student_name': r.student.user.name if (r.student and r.student.user) else None,
        'subject_name': r.subject.subject_name if r.subject else None,
        'date': r.date.strftime('%Y-%m-%d'),
        'status': r.status,
        'locked': r.locked,
        'marked_by': r.marker.name if r.marker else str(r.marked_by)
    }), 200

@api_bp.route('/admin/attendance/<int:attendance_id>/correct', methods=['PATCH'])
@role_required('admin')
def api_admin_correct_attendance(attendance_id):
    r = Attendance.query.get(attendance_id)
    if not r:
        return jsonify({'error': 'attendance record not found'}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get('new_status', '').strip().lower()
    reason = data.get('reason', '').strip()

    if not reason:
        return jsonify({'error': 'mandatory reason required'}), 400

    if new_status not in ['present', 'absent']:
        return jsonify({'error': 'invalid new_status value'}), 400

    old_status = r.status
    admin_id = session.get('user_id')

    # Atomic audit logging + status update + re-lock
    correction = AttendanceCorrection(
        attendance_id=r.attendance_id,
        admin_id=admin_id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
        corrected_at=datetime.utcnow()
    )
    db.session.add(correction)
    r.status = new_status
    r.locked = True
    db.session.commit()

    return jsonify({
        'message': 'attendance corrected and re-locked',
        'correction_id': correction.correction_id,
        'old_status': old_status,
        'new_status': new_status
    }), 200

@api_bp.route('/admin/attendance/<int:attendance_id>/corrections', methods=['GET'])
@role_required('admin')
def api_admin_get_corrections(attendance_id):
    r = Attendance.query.get(attendance_id)
    if not r:
        return jsonify({'error': 'attendance record not found'}), 404

    corrections = AttendanceCorrection.query.filter_by(attendance_id=attendance_id)\
        .order_by(AttendanceCorrection.corrected_at.desc()).all()

    results = [{
        'correction_id': c.correction_id,
        'admin_name': c.admin.name if c.admin else None,
        'old_status': c.old_status,
        'new_status': c.new_status,
        'reason': c.reason,
        'corrected_at': c.corrected_at.isoformat() + 'Z' if c.corrected_at else None
    } for c in corrections]

    return jsonify(results), 200
