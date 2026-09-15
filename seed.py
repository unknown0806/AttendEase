import os
from datetime import date, time, datetime, timedelta
from app import create_app
from db import db
from models import (
    User, Class, Subject, ClassSubject, TeacherSubject,
    Student, Period, Attendance, AttendanceCorrection, StudentMark
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping existing tables and creating fresh schema...")
        db.drop_all()
        db.create_all()

        print("Seeding Users...")
        # Admin
        admin = User(
            name="Priya Rao",
            email="priya@college.edu",
            role="admin",
            photo_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # Teachers
        teacher1 = User(
            name="Suresh Kumar",
            email="suresh@college.edu",
            role="teacher",
            photo_url="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80",
            active=True
        )
        teacher1.set_password("teacher123")
        db.session.add(teacher1)

        teacher2 = User(
            name="Meera Patel",
            email="meera@college.edu",
            role="teacher",
            photo_url="https://images.unsplash.com/photo-1580894732444-8ecded7900cd?w=150&auto=format&fit=crop&q=80",
            active=True
        )
        teacher2.set_password("teacher123")
        db.session.add(teacher2)

        # Student Users
        students_raw = [
            ("Rahul Sharma", "rahul@student.edu", "BCA21", "BCA 3A", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"),
            ("Anita Verma", "anita@student.edu", "BCA22", "BCA 3A", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"),
            ("Rohan Gupta", "rohan@student.edu", "BCA23", "BCA 3A", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"),
            ("Sneha Reddy", "sneha@student.edu", "BCA24", "BCA 3A", "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"),
            ("Amit Singh", "amit@student.edu", "BCA25", "BCA 3A", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"),
            ("Pooja Joshi", "pooja@student.edu", "BCA31", "BCA 3B", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"),
            ("Vikas Nair", "vikas@student.edu", "BCA32", "BCA 3B", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"),
        ]

        student_user_objects = []
        for name, email, roll, _, photo in students_raw:
            stu_u = User(
                name=name,
                email=email,
                role="student",
                photo_url=photo,
                active=True
            )
            stu_u.set_password("student123")
            db.session.add(stu_u)
            student_user_objects.append((stu_u, roll, _))

        db.session.commit()

        print("Seeding Classes...")
        class_3a = Class(class_name="BCA 3A")
        class_3b = Class(class_name="BCA 3B")
        db.session.add_all([class_3a, class_3b])
        db.session.commit()

        print("Seeding Students profile...")
        created_students = {}
        for user_obj, roll, cls_name in student_user_objects:
            target_class = class_3a if cls_name == "BCA 3A" else class_3b
            stu = Student(
                user_id=user_obj.user_id,
                roll_no=roll,
                class_id=target_class.class_id
            )
            db.session.add(stu)
            created_students[user_obj.email] = stu
        db.session.commit()

        print("Seeding Subjects...")
        sub_dbms = Subject(subject_name="DBMS")
        sub_python = Subject(subject_name="Python")
        sub_cn = Subject(subject_name="Computer Networks")
        db.session.add_all([sub_dbms, sub_python, sub_cn])
        db.session.commit()

        print("Linking Class Subjects...")
        for c in [class_3a, class_3b]:
            for s in [sub_dbms, sub_python, sub_cn]:
                db.session.add(ClassSubject(class_id=c.class_id, subject_id=s.subject_id))
        db.session.commit()

        print("Assigning Teachers to Subjects and Classes...")
        # Suresh Kumar teaches DBMS (3A, 3B) and Python (3A)
        # Meera Patel teaches Computer Networks (3A) and Python (3B)
        db.session.add(TeacherSubject(teacher_id=teacher1.user_id, subject_id=sub_dbms.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=teacher1.user_id, subject_id=sub_dbms.subject_id, class_id=class_3b.class_id))
        db.session.add(TeacherSubject(teacher_id=teacher1.user_id, subject_id=sub_python.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=teacher2.user_id, subject_id=sub_cn.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=teacher2.user_id, subject_id=sub_python.subject_id, class_id=class_3b.class_id))
        db.session.commit()

        print("Seeding Periods...")
        p1 = Period(period_name="Period 1", start_time=time(9, 0), end_time=time(9, 50))
        p2 = Period(period_name="Period 2", start_time=time(10, 0), end_time=time(10, 50))
        p3 = Period(period_name="Period 3", start_time=time(11, 0), end_time=time(11, 50))
        p4 = Period(period_name="Period 4", start_time=time(12, 0), end_time=time(12, 50))
        p5 = Period(period_name="Period 5", start_time=time(14, 0), end_time=time(14, 50))
        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit()

        print("Seeding Sample Attendance Records...")
        # Get BCA 3A students
        bca_3a_students = Student.query.filter_by(class_id=class_3a.class_id).all()
        rahul_student = created_students["rahul@student.edu"]

        base_date = date.today() - timedelta(days=45)
        
        # 1. DBMS: 40 sessions. Rahul present 30 (75.0%)
        curr_date = base_date
        dbms_sessions_created = 0
        while dbms_sessions_created < 40:
            if curr_date.weekday() < 5: # Monday - Friday
                # Rahul present for first 30, absent for remaining 10
                for stu in bca_3a_students:
                    if stu.student_id == rahul_student.student_id:
                        status = "present" if dbms_sessions_created < 30 else "absent"
                    else:
                        # other students mostly present
                        status = "present" if (stu.student_id + dbms_sessions_created) % 7 != 0 else "absent"
                    
                    att = Attendance(
                        student_id=stu.student_id,
                        subject_id=sub_dbms.subject_id,
                        class_id=class_3a.class_id,
                        period_id=p1.period_id,
                        date=curr_date,
                        status=status,
                        locked=True,
                        marked_by=teacher1.user_id
                    )
                    db.session.add(att)
                dbms_sessions_created += 1
            curr_date += timedelta(days=1)

        # 2. Python: 30 sessions. Rahul present 20 (66.7% -> Red Alert!)
        curr_date = base_date
        python_sessions_created = 0
        while python_sessions_created < 30:
            if curr_date.weekday() < 5:
                for stu in bca_3a_students:
                    if stu.student_id == rahul_student.student_id:
                        status = "present" if python_sessions_created < 20 else "absent"
                    else:
                        status = "present" if (stu.student_id + python_sessions_created) % 5 != 0 else "absent"
                    
                    att = Attendance(
                        student_id=stu.student_id,
                        subject_id=sub_python.subject_id,
                        class_id=class_3a.class_id,
                        period_id=p2.period_id,
                        date=curr_date,
                        status=status,
                        locked=True,
                        marked_by=teacher1.user_id
                    )
                    db.session.add(att)
                python_sessions_created += 1
            curr_date += timedelta(days=1)

        # 3. Computer Networks: 35 sessions. Rahul present 32 (91.4%)
        curr_date = base_date
        cn_sessions_created = 0
        while cn_sessions_created < 35:
            if curr_date.weekday() < 5:
                for stu in bca_3a_students:
                    if stu.student_id == rahul_student.student_id:
                        status = "present" if cn_sessions_created < 32 else "absent"
                    else:
                        status = "present" if (stu.student_id + cn_sessions_created) % 6 != 0 else "absent"
                    
                    att = Attendance(
                        student_id=stu.student_id,
                        subject_id=sub_cn.subject_id,
                        class_id=class_3a.class_id,
                        period_id=p3.period_id,
                        date=curr_date,
                        status=status,
                        locked=True,
                        marked_by=teacher2.user_id
                    )
                    db.session.add(att)
                cn_sessions_created += 1
            curr_date += timedelta(days=1)

        db.session.commit()

        # Seed sample correction
        sample_att = Attendance.query.filter_by(
            student_id=rahul_student.student_id,
            subject_id=sub_dbms.subject_id
        ).first()

        if sample_att:
            correction = AttendanceCorrection(
                attendance_id=sample_att.attendance_id,
                admin_id=admin.user_id,
                old_status="absent",
                new_status="present",
                reason="Teacher marked wrong row by mistake, student was present",
                corrected_at=datetime.now() - timedelta(days=1)
            )
            sample_att.status = "present"
            sample_att.locked = True
        # Seed sample Continuous Internal Assessment (CIA) marks
        print("Seeding Sample Student Marks...")
        all_students = Student.query.all()
        for stu in all_students:
            # Seed DBMS marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_dbms.subject_id,
                teacher_id=teacher1.user_id,
                midterm=18.0 if stu.student_id == rahul_student.student_id else 16.0,
                assignment=9.0 if stu.student_id == rahul_student.student_id else 8.0,
                total=27.0 if stu.student_id == rahul_student.student_id else 24.0
            ))
            # Seed Python marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_python.subject_id,
                teacher_id=teacher1.user_id,
                midterm=17.0 if stu.student_id == rahul_student.student_id else 15.0,
                assignment=8.5 if stu.student_id == rahul_student.student_id else 7.5,
                total=25.5 if stu.student_id == rahul_student.student_id else 22.5
            ))
            # Seed Computer Networks marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_cn.subject_id,
                teacher_id=teacher2.user_id,
                midterm=19.0 if stu.student_id == rahul_student.student_id else 14.0,
                assignment=9.5 if stu.student_id == rahul_student.student_id else 8.0,
                total=28.5 if stu.student_id == rahul_student.student_id else 22.0
            ))
        db.session.commit()

        print("Database seeded successfully!")
        print("\n=== Demo Credentials ===")
        print("Admin:   priya@college.edu   / admin123")
        print("Teacher: suresh@college.edu  / teacher123")
        print("Teacher: meera@college.edu   / teacher123")
        print("Student: rahul@student.edu   / student123")

if __name__ == "__main__":
    seed_database()
