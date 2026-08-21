import math
from flask import Blueprint, render_template, session, flash, redirect, url_for
from db import db
from models import User, Student, ClassSubject, Subject, Attendance
from auth import role_required, get_current_user

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    user = get_current_user()
    student = Student.query.filter_by(user_id=user.user_id).first()
    
    if not student:
        flash('Student profile not found. Please contact an administrator.', 'danger')
        return redirect(url_for('auth.logout'))

    # Fetch subjects belonging to student's class
    class_subjects = ClassSubject.query.filter_by(class_id=student.class_id).all()
    
    subject_stats = []
    total_classes_all = 0
    total_present_all = 0

    for cs in class_subjects:
        sub = cs.subject
        # Query all attendance records for this student and subject
        records = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=sub.subject_id
        ).all()

        total = len(records)
        present = sum(1 for r in records if r.status == 'present')
        absent = total - present

        if total > 0:
            pct = round((present / total) * 100, 1)
            is_alert = pct < 75.0
            
            # Recommendation calculation: How many consecutive classes needed to reach 75%?
            # (present + x) / (total + x) >= 0.75 => present + x >= 0.75 * total + 0.75 * x
            # 0.25 * x >= 0.75 * total - present => x >= 3 * total - 4 * present
            needed_classes = 0
            if is_alert:
                needed_classes = max(0, math.ceil(3 * total - 4 * present))
        else:
            pct = 100.0
            is_alert = False
            needed_classes = 0

        total_classes_all += total
        total_present_all += present

        subject_stats.append({
            'subject_id': sub.subject_id,
            'subject_name': sub.subject_name,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': pct,
            'alert': is_alert,
            'needed_classes': needed_classes
        })

    overall_pct = round((total_present_all / total_classes_all) * 100, 1) if total_classes_all > 0 else 100.0
    overall_alert = overall_pct < 75.0 and total_classes_all > 0

    # Recent attendance timeline
    recent_history = Attendance.query.filter_by(student_id=student.student_id)\
        .order_by(Attendance.date.desc(), Attendance.created_at.desc())\
        .limit(15).all()

    return render_template(
        'student/dashboard.html',
        user=user,
        student=student,
        subject_stats=subject_stats,
        total_classes_all=total_classes_all,
        total_present_all=total_present_all,
        overall_pct=overall_pct,
        overall_alert=overall_alert,
        recent_history=recent_history
    )
