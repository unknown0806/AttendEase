from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('teacher', 'student', 'admin', name='user_roles'), nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)
    teacher_assignments = db.relationship('TeacherSubject', backref='teacher', lazy=True)
    marked_attendances = db.relationship('Attendance', backref='marker', lazy=True)
    corrections_made = db.relationship('AttendanceCorrection', backref='admin', lazy=True)

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'photo_url': self.photo_url,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Class(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    students = db.relationship('Student', backref='class_obj', lazy=True)
    class_subjects = db.relationship('ClassSubject', backref='class_obj', lazy=True)
    teacher_subjects = db.relationship('TeacherSubject', backref='class_obj', lazy=True)
    attendances = db.relationship('Attendance', backref='class_obj', lazy=True)

    def to_dict(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Subject(db.Model):
    __tablename__ = 'subjects'
    
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    class_subjects = db.relationship('ClassSubject', backref='subject', lazy=True)
    teacher_subjects = db.relationship('TeacherSubject', backref='subject', lazy=True)
    attendances = db.relationship('Attendance', backref='subject', lazy=True)

    def to_dict(self):
        return {
            'subject_id': self.subject_id,
            'subject_name': self.subject_name
        }


class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', name='unique_class_subject'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id
        }


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'subject_id', 'class_id', name='unique_teacher_assignment'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'subject_id': self.subject_id,
            'class_id': self.class_id
        }


class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)

    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True)

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else None,
            'email': self.user.email if self.user else None,
            'roll_no': self.roll_no,
            'class_id': self.class_id,
            'class_name': self.class_obj.class_name if self.class_obj else None,
            'photo_url': self.user.photo_url if self.user else None,
            'active': self.user.active if self.user else None
        }


class Period(db.Model):
    __tablename__ = 'periods'
    
    period_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    period_name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    # Relationships
    attendances = db.relationship('Attendance', backref='period', lazy=True)

    def to_dict(self):
        return {
            'period_id': self.period_id,
            'period_name': self.period_name,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.period_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent', name='attendance_status'), nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    corrections = db.relationship('AttendanceCorrection', backref='attendance_record', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'period_id', 'date', name='unique_attendance_entry'),
    )

    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'student_name': self.student.user.name if (self.student and self.student.user) else None,
            'roll_no': self.student.roll_no if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.class_name if self.class_obj else None,
            'period_id': self.period_id,
            'period_name': self.period.period_name if self.period else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'status': self.status,
            'locked': self.locked,
            'marked_by': self.marker.name if self.marker else str(self.marked_by),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AttendanceCorrection(db.Model):
    __tablename__ = 'attendance_corrections'
    
    correction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.attendance_id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    old_status = db.Column(db.Enum('present', 'absent', name='old_status_enum'), nullable=False)
    new_status = db.Column(db.Enum('present', 'absent', name='new_status_enum'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    corrected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'correction_id': self.correction_id,
            'attendance_id': self.attendance_id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.name if self.admin else None,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'reason': self.reason,
            'corrected_at': self.corrected_at.isoformat() if self.corrected_at else None
        }
