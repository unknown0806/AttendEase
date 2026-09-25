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
        # 1. Admin User
        admin = User(
            name="Priya Rao",
            email="priya@college.edu",
            role="admin",
            phone="+91 98260 99881",
            address="Administrative Block, Room 101, College Campus, Indore",
            department="Institutional Governance & Academic Records",
            designation="Principal / System Administrator",
            qualification="Ph.D. in Computer Science & Information Systems",
            photo_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # 2. Faculty / Teachers (5 Members)
        teachers_data = [
            (
                "Suresh Kumar", "suresh@college.edu", "teacher123",
                "+91 98265 11223", "12 Professors Colony, Old Palasia, Indore, MP",
                "Computer Science & Engineering", "HOD & Associate Professor", "Ph.D. (CSE), M.Tech (Software Engg)",
                "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Meera Patel", "meera@college.edu", "teacher123",
                "+91 98265 22334", "45 Saket Nagar, Main Road, Indore, MP",
                "Information Technology", "Assistant Professor", "M.Tech (Network Systems), B.E.",
                "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Dr. Rajesh Iyer", "rajesh@college.edu", "teacher123",
                "+91 98265 33445", "78 Silver Springs, AB Road, Indore, MP",
                "Data Science & Artificial Intelligence", "Senior Professor", "Ph.D. (AI & Cloud Computing), M.S.",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Ananya Sen", "ananya@college.edu", "teacher123",
                "+91 98265 44556", "23 Geeta Bhawan Square, Indore, MP",
                "Software Engineering", "Assistant Professor", "MCA, B.Sc (Computer Science)",
                "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Vikram Malhotra", "vikram@college.edu", "teacher123",
                "+91 98265 55667", "66 Annapurna Road, Sector C, Indore, MP",
                "Computer Networks & Security", "Senior Lecturer", "M.Sc (Cyber Security), CCNA",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
            )
        ]

        teacher_objs = {}
        for name, email, pwd, phone, addr, dept, desig, qual, photo in teachers_data:
            t = User(
                name=name, email=email, role="teacher",
                phone=phone, address=addr, department=dept,
                designation=desig, qualification=qual, photo_url=photo,
                active=True
            )
            t.set_password(pwd)
            db.session.add(t)
            teacher_objs[email] = t

        # 3. Classes
        print("Seeding Classes...")
        class_3a = Class(class_name="BCA 3A")
        class_3b = Class(class_name="BCA 3B")
        class_mca = Class(class_name="MCA 1A")
        db.session.add_all([class_3a, class_3b, class_mca])
        db.session.commit()

        # 4. Subjects
        print("Seeding Subjects...")
        sub_dbms = Subject(subject_name="DBMS")
        sub_python = Subject(subject_name="Python")
        sub_cn = Subject(subject_name="Computer Networks")
        sub_dsa = Subject(subject_name="Data Structures")
        sub_cloud = Subject(subject_name="Cloud Computing")
        db.session.add_all([sub_dbms, sub_python, sub_cn, sub_dsa, sub_cloud])
        db.session.commit()

        # Link Class Subjects
        print("Linking Class Subjects...")
        for c in [class_3a, class_3b]:
            for s in [sub_dbms, sub_python, sub_cn, sub_dsa]:
                db.session.add(ClassSubject(class_id=c.class_id, subject_id=s.subject_id))

        for s in [sub_dbms, sub_python, sub_cn, sub_cloud]:
            db.session.add(ClassSubject(class_id=class_mca.class_id, subject_id=s.subject_id))
        db.session.commit()

        # 5. Assign Teachers to Subjects and Classes
        print("Assigning Teachers to Subjects and Classes...")
        t_suresh = teacher_objs["suresh@college.edu"]
        t_meera = teacher_objs["meera@college.edu"]
        t_rajesh = teacher_objs["rajesh@college.edu"]
        t_ananya = teacher_objs["ananya@college.edu"]
        t_vikram = teacher_objs["vikram@college.edu"]

        db.session.add(TeacherSubject(teacher_id=t_suresh.user_id, subject_id=sub_dbms.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=t_suresh.user_id, subject_id=sub_python.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=t_meera.user_id, subject_id=sub_cn.subject_id, class_id=class_3a.class_id))
        db.session.add(TeacherSubject(teacher_id=t_ananya.user_id, subject_id=sub_dsa.subject_id, class_id=class_3a.class_id))

        db.session.add(TeacherSubject(teacher_id=t_suresh.user_id, subject_id=sub_dbms.subject_id, class_id=class_3b.class_id))
        db.session.add(TeacherSubject(teacher_id=t_meera.user_id, subject_id=sub_python.subject_id, class_id=class_3b.class_id))
        db.session.add(TeacherSubject(teacher_id=t_vikram.user_id, subject_id=sub_cn.subject_id, class_id=class_3b.class_id))
        db.session.add(TeacherSubject(teacher_id=t_ananya.user_id, subject_id=sub_dsa.subject_id, class_id=class_3b.class_id))

        db.session.add(TeacherSubject(teacher_id=t_rajesh.user_id, subject_id=sub_cloud.subject_id, class_id=class_mca.class_id))
        db.session.add(TeacherSubject(teacher_id=t_suresh.user_id, subject_id=sub_dbms.subject_id, class_id=class_mca.class_id))
        db.session.add(TeacherSubject(teacher_id=t_vikram.user_id, subject_id=sub_cn.subject_id, class_id=class_mca.class_id))
        db.session.commit()

        # 6. Student Users (23 Detailed Records)
        print("Seeding 23 Students with Full Parent & Contact Details...")
        students_raw = [
            # BCA 3A (10 Students)
            (
                "Rahul Sharma", "rahul@student.edu", "BCA21", class_3a,
                "+91 98260 11001", "14 Scheme 54, Vijay Nagar, Indore, MP",
                "Mr. Rajesh Sharma", "Mrs. Sunita Sharma", "+91 98261 11001", "+91 98262 11001",
                "2004-05-12", "Male", "B+",
                "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Anita Verma", "anita@student.edu", "BCA22", class_3a,
                "+91 98260 11002", "45 Silver Springs, AB Road, Indore, MP",
                "Mr. Alok Verma", "Mrs. Rekha Verma", "+91 98261 11002", "+91 98262 11002",
                "2004-08-21", "Female", "O+",
                "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Rohan Gupta", "rohan@student.edu", "BCA23", class_3a,
                "+91 98260 11003", "88 Mahalaxmi Nagar, Sector A, Indore, MP",
                "Mr. Sunil Gupta", "Mrs. Kavita Gupta", "+91 98261 11003", "+91 98262 11003",
                "2003-11-04", "Male", "A+",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Sneha Reddy", "sneha@student.edu", "BCA24", class_3a,
                "+91 98260 11004", "12 South Tukoganj, Near Treasure Island, Indore, MP",
                "Mr. Mohan Reddy", "Mrs. Shobha Reddy", "+91 98261 11004", "+91 98262 11004",
                "2004-02-18", "Female", "AB+",
                "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Amit Singh", "amit@student.edu", "BCA25", class_3a,
                "+91 98260 11005", "302 Kalani Nagar, Airport Road, Indore, MP",
                "Mr. Virendra Singh", "Mrs. Maya Singh", "+91 98261 11005", "+91 98262 11005",
                "2003-09-15", "Male", "B-",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Priya Tiwari", "priyatiwari@student.edu", "BCA26", class_3a,
                "+91 98260 11006", "78 Rau Bypass Road, Silicon Valley, Indore, MP",
                "Mr. Manoj Tiwari", "Mrs. Poonam Tiwari", "+91 98261 11006", "+91 98262 11006",
                "2004-07-29", "Female", "A-",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Deepak Chauhan", "deepak@student.edu", "BCA27", class_3a,
                "+91 98260 11007", "56 Silicon City, AB Road, Indore, MP",
                "Mr. Harish Chauhan", "Mrs. Lalita Chauhan", "+91 98261 11007", "+91 98262 11007",
                "2004-01-10", "Male", "O-",
                "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Neha Kapoor", "neha@student.edu", "BCA28", class_3a,
                "+91 98260 11008", "104 Scheme 78, Part 2, Vijay Nagar, Indore, MP",
                "Mr. Sanjay Kapoor", "Mrs. Rashmi Kapoor", "+91 98261 11008", "+91 98262 11008",
                "2004-06-14", "Female", "B+",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Gaurav Pandey", "gaurav@student.edu", "BCA29", class_3a,
                "+91 98260 11009", "22 Annapurna Road, Sector A, Indore, MP",
                "Mr. Satish Pandey", "Mrs. Seema Pandey", "+91 98261 11009", "+91 98262 11009",
                "2003-12-25", "Male", "A+",
                "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Swati Jain", "swati@student.edu", "BCA30", class_3a,
                "+91 98260 11010", "61 Sarafa Bazar, M.G. Road, Indore, MP",
                "Mr. Pradeep Jain", "Mrs. Neeta Jain", "+91 98261 11010", "+91 98262 11010",
                "2004-03-30", "Female", "O+",
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&auto=format&fit=crop&q=80"
            ),

            # BCA 3B (7 Students)
            (
                "Pooja Joshi", "pooja@student.edu", "BCA31", class_3b,
                "+91 98260 11011", "90 Tilak Nagar Main Road, Indore, MP",
                "Mr. Devendra Joshi", "Mrs. Gita Joshi", "+91 98261 11011", "+91 98262 11011",
                "2004-04-19", "Female", "B+",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Vikas Nair", "vikas@student.edu", "BCA32", class_3b,
                "+91 98260 11012", "33 Manoramaganj, Near Gita Bhawan, Indore, MP",
                "Mr. K.P. Nair", "Mrs. Lakshmi Nair", "+91 98261 11012", "+91 98262 11012",
                "2003-10-11", "Male", "A+",
                "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Divya Saxena", "divya@student.edu", "BCA33", class_3b,
                "+91 98260 11013", "17 Geeta Bhawan, Navlakha, Indore, MP",
                "Mr. Ramesh Saxena", "Mrs. Alka Saxena", "+91 98261 11013", "+91 98262 11013",
                "2004-09-08", "Female", "AB+",
                "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Harsh Vardhan", "harsh@student.edu", "BCA34", class_3b,
                "+91 98260 11014", "49 Bengali Square, Ring Road, Indore, MP",
                "Mr. Arvind Vardhan", "Mrs. Sarita Vardhan", "+91 98261 11014", "+91 98262 11014",
                "2003-08-22", "Male", "O+",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Ritu Agarwal", "ritu@student.edu", "BCA35", class_3b,
                "+91 98260 11015", "81 Navlakha Main Road, Indore, MP",
                "Mr. Pawan Agarwal", "Mrs. Manju Agarwal", "+91 98261 11015", "+91 98262 11015",
                "2004-11-15", "Female", "B-",
                "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Aditya Mishra", "aditya@student.edu", "BCA36", class_3b,
                "+91 98260 11016", "112 Sudama Nagar, Ring Road, Indore, MP",
                "Mr. B.K. Mishra", "Mrs. Sushma Mishra", "+91 98261 11016", "+91 98262 11016",
                "2003-07-07", "Male", "A-",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Ananya Roy", "ananyaroy@student.edu", "BCA37", class_3b,
                "+91 98260 11017", "39 Palasia Main Road, Indore, MP",
                "Mr. Subhash Roy", "Mrs. Anita Roy", "+91 98261 11017", "+91 98262 11017",
                "2004-12-01", "Female", "O+",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80"
            ),

            # MCA 1A (6 Students)
            (
                "Kavita Nair", "kavita@student.edu", "MCA01", class_mca,
                "+91 98260 11018", "105 Apollo DB City, Nipania, Indore, MP",
                "Mr. G. Nair", "Mrs. Radhika Nair", "+91 98261 11018", "+91 98262 11018",
                "2002-03-14", "Female", "A+",
                "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Varun Bhatia", "varun@student.edu", "MCA02", class_mca,
                "+91 98260 11019", "28 Race Course Road, Indore, MP",
                "Mr. Rajeev Bhatia", "Mrs. Sangeeta Bhatia", "+91 98261 11019", "+91 98262 11019",
                "2002-05-20", "Male", "B+",
                "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Tanvi Mehta", "tanvi@student.edu", "MCA03", class_mca,
                "+91 98260 11020", "73 Yashwant Niwas Road, Indore, MP",
                "Mr. Bharat Mehta", "Mrs. Priti Mehta", "+91 98261 11020", "+91 98262 11020",
                "2002-10-09", "Female", "O+",
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Manish Yadav", "manish@student.edu", "MCA04", class_mca,
                "+91 98260 11021", "64 Rajendra Nagar, AB Road, Indore, MP",
                "Mr. Ram Yadav", "Mrs. Kamla Yadav", "+91 98261 11021", "+91 98262 11021",
                "2001-12-18", "Male", "AB+",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Shreya Sen", "shreya@student.edu", "MCA05", class_mca,
                "+91 98260 11022", "52 Scheme 140, Pipliyahana, Indore, MP",
                "Mr. S.K. Sen", "Mrs. Rupa Sen", "+91 98261 11022", "+91 98262 11022",
                "2002-08-31", "Female", "B+",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            ),
            (
                "Kunal Deshmukh", "kunal@student.edu", "MCA06", class_mca,
                "+91 98260 11023", "19 Mhow Naka, Dhar Road, Indore, MP",
                "Mr. Vinayak Deshmukh", "Mrs. Pratibha Deshmukh", "+91 98261 11023", "+91 98262 11023",
                "2002-01-26", "Male", "A+",
                "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"
            )
        ]

        created_students = {}
        for name, email, roll, target_cls, phone, addr, f_name, m_name, f_phone, m_phone, dob, gen, bg, photo in students_raw:
            stu_u = User(
                name=name,
                email=email,
                role="student",
                phone=phone,
                address=addr,
                photo_url=photo,
                active=True
            )
            stu_u.set_password("student123")
            db.session.add(stu_u)
            db.session.flush()

            stu = Student(
                user_id=stu_u.user_id,
                roll_no=roll,
                class_id=target_cls.class_id,
                father_name=f_name,
                mother_name=m_name,
                father_phone=f_phone,
                mother_phone=m_phone,
                dob=dob,
                gender=gen,
                blood_group=bg
            )
            db.session.add(stu)
            created_students[email] = stu

        db.session.commit()

        # 7. Periods
        print("Seeding Periods...")
        p1 = Period(period_name="Period 1", start_time=time(9, 0), end_time=time(9, 50))
        p2 = Period(period_name="Period 2", start_time=time(10, 0), end_time=time(10, 50))
        p3 = Period(period_name="Period 3", start_time=time(11, 0), end_time=time(11, 50))
        p4 = Period(period_name="Period 4", start_time=time(12, 0), end_time=time(12, 50))
        p5 = Period(period_name="Period 5", start_time=time(14, 0), end_time=time(14, 50))
        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit()

        # 8. Sample Attendance Records
        print("Seeding Sample Attendance Records across classes...")
        bca_3a_students = Student.query.filter_by(class_id=class_3a.class_id).all()
        rahul_student = created_students["rahul@student.edu"]

        base_date = date.today() - timedelta(days=45)

        # 1. DBMS for BCA 3A: 40 sessions. Rahul present 30 (75.0%)
        curr_date = base_date
        dbms_sessions_created = 0
        while dbms_sessions_created < 40:
            if curr_date.weekday() < 5:
                for stu in bca_3a_students:
                    if stu.student_id == rahul_student.student_id:
                        status = "present" if dbms_sessions_created < 30 else "absent"
                    else:
                        status = "present" if (stu.student_id + dbms_sessions_created) % 7 != 0 else "absent"

                    att = Attendance(
                        student_id=stu.student_id,
                        subject_id=sub_dbms.subject_id,
                        class_id=class_3a.class_id,
                        period_id=p1.period_id,
                        date=curr_date,
                        status=status,
                        locked=True,
                        marked_by=t_suresh.user_id
                    )
                    db.session.add(att)
                dbms_sessions_created += 1
            curr_date += timedelta(days=1)

        # 2. Python for BCA 3A: 30 sessions. Rahul present 20 (66.7% -> Shortage Alert!)
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
                        marked_by=t_suresh.user_id
                    )
                    db.session.add(att)
                python_sessions_created += 1
            curr_date += timedelta(days=1)

        # 3. Computer Networks for BCA 3A: 35 sessions. Rahul present 32 (91.4%)
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
                        marked_by=t_meera.user_id
                    )
                    db.session.add(att)
                cn_sessions_created += 1
            curr_date += timedelta(days=1)

        db.session.commit()

        # 9. Continuous Internal Assessment (CIA) Marks for all students
        print("Seeding Sample Student Marks...")
        all_students = Student.query.all()
        for stu in all_students:
            is_rahul = (stu.student_id == rahul_student.student_id)
            # DBMS Marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_dbms.subject_id,
                teacher_id=t_suresh.user_id,
                midterm=18.0 if is_rahul else 16.0,
                assignment=9.0 if is_rahul else 8.0,
                total=27.0 if is_rahul else 24.0
            ))
            # Python Marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_python.subject_id,
                teacher_id=t_suresh.user_id,
                midterm=17.0 if is_rahul else 15.0,
                assignment=8.5 if is_rahul else 7.5,
                total=25.5 if is_rahul else 22.5
            ))
            # CN Marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_cn.subject_id,
                teacher_id=t_meera.user_id,
                midterm=19.0 if is_rahul else 14.0,
                assignment=9.5 if is_rahul else 8.0,
                total=28.5 if is_rahul else 22.0
            ))
            # Data Structures Marks
            db.session.add(StudentMark(
                student_id=stu.student_id,
                subject_id=sub_dsa.subject_id,
                teacher_id=t_ananya.user_id,
                midterm=18.5 if is_rahul else 15.5,
                assignment=9.0 if is_rahul else 8.0,
                total=27.5 if is_rahul else 23.5
            ))
        db.session.commit()

        # Seed sample correction for audit trail demo
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
                reason="Medical leave approved by Dean, certificate verified",
                corrected_at=datetime.now() - timedelta(days=2)
            )
            sample_att.status = "present"
            sample_att.locked = True
            db.session.add(correction)
            db.session.commit()

        print("\n==========================================")
        print("DATABASE SEEDED SUCCESSFULLY WITH 23 STUDENTS & 5 FACULTY MEMBERS!")
        print("==========================================")
        print("\n=== Demo Logins ===")
        print("Admin:   priya@college.edu   / admin123")
        print("Teacher: suresh@college.edu  / teacher123 (DBMS, Python)")
        print("Teacher: meera@college.edu   / teacher123 (Computer Networks)")
        print("Teacher: rajesh@college.edu  / teacher123 (Cloud Computing)")
        print("Teacher: ananya@college.edu  / teacher123 (Data Structures)")
        print("Student: rahul@student.edu   / student123 (BCA 3A - Shortage Alert)")
        print("Student: anita@student.edu   / student123 (BCA 3A - High Attendance)")
        print("Student: pooja@student.edu   / student123 (BCA 3B)")
        print("Student: kavita@student.edu  / student123 (MCA 1A)")
        print("==========================================\n")

if __name__ == "__main__":
    seed_database()
