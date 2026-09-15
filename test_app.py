import unittest
import json
from datetime import date
from app import create_app
from db import db
from models import (
    User, Class, Subject, ClassSubject, TeacherSubject,
    Student, Period, Attendance, AttendanceCorrection
)
from seed import seed_database

class AttendXTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        seed_database()

    # ----------------------------------------------------
    # 1. Auth & Session Tests
    # ----------------------------------------------------
    def test_login_logout_flow(self):
        # Teacher login
        resp = self.client.post('/login', data={
            'email': 'suresh@college.edu',
            'password': 'teacher123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Suresh Kumar', resp.data)

        # Logout
        resp_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(resp_logout.status_code, 200)
        self.assertIn(b'Login', resp_logout.data)

    def test_invalid_login(self):
        resp = self.client.post('/login', data={
            'email': 'suresh@college.edu',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Invalid email or password', resp.data)

    # ----------------------------------------------------
    # 2. Teacher Attendance & Submit-and-Lock Tests
    # ----------------------------------------------------
    def test_teacher_mark_and_lock_attendance(self):
        # Login as teacher Suresh
        self.client.post('/login', data={'email': 'suresh@college.edu', 'password': 'teacher123'})
        
        with self.app.app_context():
            class_obj = Class.query.filter_by(class_name='BCA 3A').first()
            subject_obj = Subject.query.filter_by(subject_name='DBMS').first()
            period_obj = Period.query.first()
            students = Student.query.filter_by(class_id=class_obj.class_id).all()
            
            test_date = '2026-09-01'

            post_data = {
                'class_id': class_obj.class_id,
                'subject_id': subject_obj.subject_id,
                'period_id': period_obj.period_id,
                'date': test_date
            }
            for stu in students:
                post_data[f'status_{stu.student_id}'] = 'present'

        # Submit attendance
        resp = self.client.post('/teacher/submit', data=post_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'submitted and locked', resp.data)

        # Verify in DB that records are locked
        with self.app.app_context():
            saved_records = Attendance.query.filter_by(
                class_id=class_obj.class_id,
                subject_id=subject_obj.subject_id,
                period_id=period_obj.period_id,
                date=date(2026, 9, 1)
            ).all()
            self.assertEqual(len(saved_records), len(students))
            for r in saved_records:
                self.assertTrue(r.locked)

        # Attempt to modify locked record as teacher (should be rejected)
        resp2 = self.client.post('/teacher/submit', data=post_data, follow_redirects=True)
        self.assertIn(b'already submitted and locked', resp2.data)

    # ----------------------------------------------------
    # 3. Student Dashboard & <75% Red Alert Tests
    # ----------------------------------------------------
    def test_student_dashboard_alert_calculation(self):
        # Login as student Rahul
        resp = self.client.post('/login', data={'email': 'rahul@student.edu', 'password': 'student123'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Rahul Sharma', resp.data)
        self.assertIn(b'Attendance Overview', resp.data)
        # Check that shortage alert is rendered with needed classes
        self.assertIn(b'Attendance Shortage', resp.data)
        self.assertIn(b'You must attend the next', resp.data)

        # Check attendance page
        att_page = self.client.get('/student/attendance')
        self.assertEqual(att_page.status_code, 200)
        self.assertIn(b'Shortage Alert', att_page.data)
        self.assertIn(b'Attend next', att_page.data)

    def test_admin_photo_management(self):
        # Login as Admin
        self.client.post('/login', data={'email': 'priya@college.edu', 'password': 'admin123'})

        # Update student photo via URL
        with self.app.app_context():
            stu = Student.query.first()
            stu_id = stu.student_id

        edit_res = self.client.post(f'/admin/students/{stu_id}/edit', data={
            'name': 'Rahul Sharma Updated',
            'roll_no': 'BCA21',
            'class_id': 1,
            'photo_url': 'https://example.com/custom_photo.jpg'
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        with self.app.app_context():
            updated_stu = Student.query.get(stu_id)
            self.assertEqual(updated_stu.user.photo_url, 'https://example.com/custom_photo.jpg')
    def test_admin_mandatory_reason_correction_and_relock(self):
        # Login as Admin Priya
        self.client.post('/login', data={'email': 'priya@college.edu', 'password': 'admin123'})

        with self.app.app_context():
            att = Attendance.query.filter_by(status='absent').first()
            att_id = att.attendance_id
            old_status = att.status

        # 1. Attempt correction with EMPTY reason (should fail)
        resp_empty_reason = self.client.post(f'/admin/attendance/{att_id}/correct', data={
            'new_status': 'present',
            'reason': ''
        }, follow_redirects=True)
        self.assertIn(b'Mandatory correction reason is required', resp_empty_reason.data)

        # 2. Correction with valid reason
        resp_success = self.client.post(f'/admin/attendance/{att_id}/correct', data={
            'new_status': 'present',
            'reason': 'Student attended lab session, verified by HOD.'
        }, follow_redirects=True)
        self.assertEqual(resp_success.status_code, 200)
        self.assertIn(b're-locked successfully', resp_success.data)

        # 3. Verify in DB: status updated, locked=True, and audit row added
        with self.app.app_context():
            updated_att = Attendance.query.get(att_id)
            self.assertEqual(updated_att.status, 'present')
            self.assertTrue(updated_att.locked)

            correction_row = AttendanceCorrection.query.filter_by(attendance_id=att_id).order_by(AttendanceCorrection.correction_id.desc()).first()
            self.assertIsNotNone(correction_row)
            self.assertEqual(correction_row.old_status, old_status)
            self.assertEqual(correction_row.new_status, 'present')
            self.assertEqual(correction_row.reason, 'Student attended lab session, verified by HOD.')

    # ----------------------------------------------------
    # 5. REST API Spec 24 Endpoints Verification
    # ----------------------------------------------------
    def test_api_auth_and_teacher_endpoints(self):
        # 1. POST /api/auth/login
        login_res = self.client.post('/api/auth/login', json={
            'email': 'suresh@college.edu',
            'password': 'teacher123'
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()['role'], 'teacher')

        # 3. GET /api/teacher/classes
        classes_res = self.client.get('/api/teacher/classes')
        self.assertEqual(classes_res.status_code, 200)
        self.assertTrue(len(classes_res.get_json()) > 0)

        # 4. GET /api/teacher/students?class_id=1
        students_res = self.client.get('/api/teacher/students?class_id=1')
        self.assertEqual(students_res.status_code, 200)
        self.assertTrue(len(students_res.get_json()) > 0)

        # 2. POST /api/auth/logout
        logout_res = self.client.post('/api/auth/logout')
        self.assertEqual(logout_res.status_code, 200)

    def test_api_student_attendance(self):
        # Student Login
        self.client.post('/api/auth/login', json={'email': 'rahul@student.edu', 'password': 'student123'})
        
        # 6. GET /api/student/attendance
        res = self.client.get('/api/student/attendance')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(len(data) > 0)
        
        # Find Python subject and check alert is True
        python_sub = next(s for s in data if s['subject_name'] == 'Python')
        self.assertTrue(python_sub['alert'])
        self.assertLess(python_sub['percentage'], 75.0)

    def test_api_admin_full_crud_and_corrections(self):
        # Admin Login
        self.client.post('/api/auth/login', json={'email': 'priya@college.edu', 'password': 'admin123'})

        # 7. GET /api/admin/students
        students_res = self.client.get('/api/admin/students')
        self.assertEqual(students_res.status_code, 200)

        # 8. POST /api/admin/students
        add_stu = self.client.post('/api/admin/students', json={
            'name': 'API Test Student',
            'email': 'apitest@student.edu',
            'password': 'password123',
            'roll_no': 'TEST99',
            'class_id': 1
        })
        self.assertEqual(add_stu.status_code, 201)
        new_stu_id = add_stu.get_json()['student_id']

        # 9. PUT /api/admin/students/{id}
        edit_stu = self.client.put(f'/api/admin/students/{new_stu_id}', json={'name': 'Updated API Student'})
        self.assertEqual(edit_stu.status_code, 200)

        # 10. PATCH /api/admin/students/{id}/deactivate
        deact_stu = self.client.patch(f'/api/admin/students/{new_stu_id}/deactivate')
        self.assertEqual(deact_stu.status_code, 200)

        # 11. GET /api/admin/teachers
        teachers_res = self.client.get('/api/admin/teachers')
        self.assertEqual(teachers_res.status_code, 200)

        # 12. POST /api/admin/teachers
        add_teach = self.client.post('/api/admin/teachers', json={
            'name': 'API Teacher',
            'email': 'apiteacher@college.edu',
            'password': 'password123'
        })
        self.assertEqual(add_teach.status_code, 201)
        new_teach_id = add_teach.get_json()['user_id']

        # 13. PUT /api/admin/teachers/{id}
        edit_teach = self.client.put(f'/api/admin/teachers/{new_teach_id}', json={'name': 'Updated API Teacher'})
        self.assertEqual(edit_teach.status_code, 200)

        # 14. POST /api/admin/teachers/{id}/assign
        assign_teach = self.client.post(f'/api/admin/teachers/{new_teach_id}/assign', json={'class_id': 1, 'subject_id': 3})
        self.assertEqual(assign_teach.status_code, 201)

        # 15. PATCH /api/admin/teachers/{id}/deactivate
        deact_teach = self.client.patch(f'/api/admin/teachers/{new_teach_id}/deactivate')
        self.assertEqual(deact_teach.status_code, 200)

        # 16. GET /api/admin/classes
        classes_res = self.client.get('/api/admin/classes')
        self.assertEqual(classes_res.status_code, 200)

        # 17. POST /api/admin/classes
        create_class = self.client.post('/api/admin/classes', json={'class_name': 'BCA 3Z'})
        self.assertEqual(create_class.status_code, 201)
        new_class_id = create_class.get_json()['class_id']

        # 18. GET /api/admin/subjects
        subjects_res = self.client.get('/api/admin/subjects')
        self.assertEqual(subjects_res.status_code, 200)

        # 19. POST /api/admin/subjects
        create_sub = self.client.post('/api/admin/subjects', json={'subject_name': 'DevOps'})
        self.assertEqual(create_sub.status_code, 201)
        new_sub_id = create_sub.get_json()['subject_id']

        # 20. POST /api/admin/classes/{id}/subjects
        map_sub = self.client.post(f'/api/admin/classes/{new_class_id}/subjects', json={'subject_id': new_sub_id})
        self.assertEqual(map_sub.status_code, 201)

        # 21. GET /api/admin/attendance
        att_list = self.client.get('/api/admin/attendance')
        self.assertEqual(att_list.status_code, 200)

        # 22. GET /api/admin/attendance/{id}
        with self.app.app_context():
            sample_att = Attendance.query.first()
            sample_id = sample_att.attendance_id

        single_att = self.client.get(f'/api/admin/attendance/{sample_id}')
        self.assertEqual(single_att.status_code, 200)

        # 23. PATCH /api/admin/attendance/{id}/correct
        correct_res = self.client.patch(f'/api/admin/attendance/{sample_id}/correct', json={
            'new_status': 'present',
            'reason': 'API test mandatory correction reason'
        })
        self.assertEqual(correct_res.status_code, 200)
        self.assertEqual(correct_res.get_json()['new_status'], 'present')

        # 24. GET /api/admin/attendance/{id}/corrections
        hist_res = self.client.get(f'/api/admin/attendance/{sample_id}/corrections')
        self.assertEqual(hist_res.status_code, 200)
        self.assertTrue(len(hist_res.get_json()) > 0)

if __name__ == '__main__':
    unittest.main()
