# AttendX — Smart College ERP & Attendance Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20MySQL-orange.svg)](https://www.sqlalchemy.org/)
[![UI/UX](https://img.shields.io/badge/Design-Academic%20Blue%20%7C%20Mobile--First-10376d.svg)](#-design-system--uiux)
[![Tests](https://img.shields.io/badge/Tests-8%2F8%20Passing-brightgreen.svg)](#-test-suite--quality-assurance)

> **AttendX** is a next-generation, mobile-first College ERP and Smart Attendance Management System designed to eliminate manual attendance overhead, prevent post-submission record tampering via submit-and-lock security, skip redundant logins across back-to-back lectures, and proactively alert students when their subject attendance drops below 75%.

---

## 📌 Executive Summary & Problem Solved

Traditional paper registers and spreadsheets are vulnerable to proxy attendance, post-facto tampering, and delayed notifications. Students discover critical shortages only right before exam hall tickets are withheld. Furthermore, faculty members lose valuable teaching time re-logging into cumbersome portals between consecutive classes.

**AttendX solves these challenges through:**
1. **Submit-and-Lock Tamper Protection:** Once a teacher submits attendance for a lecture/lab, the record is immediately and permanently frozen (`locked=True`). Teachers cannot alter submitted sessions.
2. **Audited Admin Correction Workflow:** Only designated College Administrators can unlock a submitted record. Corrections require a mandatory audit justification reason and are automatically re-locked and permanently recorded in an immutable audit ledger (`attendance_corrections`).
3. **Persistent Teacher Session:** Teachers authenticate once and can seamlessly transition across classes and subject batches throughout the day without repeated login prompts.
4. **Real-Time 75% Shortage Alert:** Conic-gradient circular gauges display Theory, Practical, and Overall attendance metrics in real-time, instantly highlighting subjects below the 75% regulatory requirement with danger badges.
5. **Modern Academic ERP Experience:** Designed with an academic navy-blue color palette (`#10376d`), 9-card interactive action grid, student ID badge headers, and mobile bottom tab navigation.

---

## 🚀 Key Features by User Role

### 👨‍🎓 1. Student Portal (`student`)
- **Visual Circular Gauges:** Real-time CSS conic-gradient circular meters for **Theory Attendance (78.5%)**, **Practical Attendance (91.2%)**, and **Overall Attendance (84.8%)**.
- **Subject-Wise Attendance Breakdown:** Lists total sessions conducted, attended, and current attendance percentage with automated **Shortage Alert Badges** (`<75% Defaulter`).
- **Interactive Action Hub (9 Sub-Pages):**
  - 📅 **Schedule:** Weekly class timetable with room numbers, faculty details, and live time slots.
  - 📝 **Assignments:** Track homework, lab submissions, due dates, and grading status.
  - 💳 **Fee Details:** View semester fee summaries, paid receipts, and pending dues with payment portal links.
  - 📊 **Results & CGPA:** Semester-wise SGPA/CGPA cards, grade distributions, and mark sheets.
  - 📢 **College Notices:** Real-time administrative circulars and urgent college announcements.
  - 🪪 **Digital Profile & ID:** College digital identity card with roll number, program, semester, and contact information.
  - 💬 **Messages:** Direct communication channel with course professors and mentors.
  - 🔔 **Notifications:** System alerts for low attendance, assignment deadlines, and exam schedules.

### 👩‍🏫 2. Teacher Portal (`teacher`)
- **Persistent Session Workflow:** Mark attendance across multiple classes and subjects in succession without session timeouts.
- **Rapid Attendance Marking Interface:**
  - One-click **"All Present"** and **"All Absent"** batch selectors.
  - Interactive switch toggles with visual Present/Absent badges per student.
- **Submit-and-Lock Security:** Instant record freeze upon submit with visual lockout prevention and warning dialogs.
- **Teacher Action Hub (9 Quick Actions):**
  - 📋 **Take Attendance:** Select class, subject, date, and period slot to record attendance.
  - 👥 **My Classes & Rosters:** View enrolled student directories, roll numbers, and historical attendance rates.
  - 📝 **Assignment Publisher:** Create and distribute course assignments with deadlines and attachment notes.
  - 🎯 **CIA / Internal Marks Entry:** Record continuous internal assessment and midterm marks.
  - 📅 **Faculty Timetable:** Weekly teaching schedule with lab hours and room allocations.
  - 📢 **Department Notices:** Post subject-specific notices to assigned class batches.
  - 💬 **Faculty Messages & Notifications:** Receive student queries and institutional memos.

### 🛡️ 3. Admin Control Center (`admin`)
- **Executive Institutional Dashboard:** High-level analytics cards showing Total Enrolled Students, Active Faculty, Campus-wide Average Attendance, and Active Shortage Alerts.
- **Comprehensive User Management:** Full CRUD capabilities for Students and Faculty with **Soft-Deactivation** (preserves historical attendance integrity even if a user leaves the institution).
- **Curriculum & Section Mapping:** Configure programs, semesters, subjects (Theory/Practical), and assign faculty to specific class sections.
- **Master Institutional Attendance Explorer:** Filter and audit attendance logs by date range, department, class section, subject, and faculty member.
- **Audited Record Correction:**
  - View locked session details.
  - Modify individual student status (e.g. Absent ➔ Present for college-sanctioned medical leave or sports duty).
  - Enforce mandatory written justification before changes are committed.
  - Full audit logging: Stores `admin_id`, `attendance_id`, `old_status`, `new_status`, `reason`, and `corrected_at` timestamp.
- **Shortage Analytics Report:** One-click exportable list of all students currently below 75% minimum threshold for remedial action.
- **Institutional Broadcast System:** Publish campus-wide announcements.

---

## 🎨 Design System & UI/UX

AttendX features a custom, lightweight CSS design system inspired by modern academic ERP mobile applications:

| Token | Value | Purpose |
|---|---|---|
| **Primary Navy** | `#10376d` | Navigation bars, primary buttons, headers |
| **Accent Sky** | `#0dcaf0` | Icons, active indicators, highlights |
| **Danger Red** | `#dc3545` | Attendance shortage alerts (<75%), absent status |
| **Success Green** | `#198754` | Attendance compliance (≥75%), present status |
| **Card Background** | `#ffffff` | Clean elevated white cards with soft drop shadows |
| **App Canvas** | `#f0f3f8` | Neutral, high-contrast background |

- **Circular Ring Meters:** Dynamic CSS variables `--p: <percentage>` driving 360-degree conic gradients.
- **Responsive Layout:** Dynamic bottom navigation bar on mobile/tablet viewports (<768px) and top navbar on desktop viewports.

---

## 🏗️ Architecture & Database Schema

AttendX is built with a clean monolithic Flask architecture designed for high maintainability, rapid response times (<50ms), and zero client-side compilation dependencies:

```
[Browser / Mobile Client]
         │
         ▼
[Flask 3.x Application] ── (Session Auth + Role-Based Access Control)
         │
         ├── Jinja2 Server-Side Rendered Templates (Student / Teacher / Admin)
         ├── 24 JSON REST API Endpoints (/api/*)
         │
         ▼
[Flask-SQLAlchemy ORM]
         │
         ▼
[SQLite (Local Dev) / MySQL 8.0+ (Production Engine)]
```

### Relational Schema (9 Core Tables)

1. `users`: Authentication credentials (bcrypt/werkzeug hash), full name, email, role (`admin`, `teacher`, `student`), and `active` soft-delete flag.
2. `classes`: Academic sections (e.g. `BCA 3A`, `B.Tech CSE 4B`, `BCA 3B`).
3. `subjects`: Courses with code, title, and type (`theory`, `practical`).
4. `class_subjects`: Associative link between classes and curriculum subjects.
5. `teacher_subjects`: Faculty teaching assignments per class section.
6. `students`: Extended student profiles, roll numbers, enrollment dates, and foreign key to `users` and `classes`.
7. `periods`: Scheduled timetable slots (start time, end time, label).
8. `attendance`: Attendance transaction log (`student_id`, `class_subject_id`, `teacher_id`, `period_id`, `date`, `status`, `locked`).
9. `attendance_corrections`: Immutable audit log of administrative overrides with before/after state and mandatory rationale.

---

## 🔌 Complete REST API Specification (24 Endpoints)

AttendX provides a comprehensive RESTful JSON API alongside server-rendered views:

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/auth/login` | Authenticate user & start session | Public |
| `POST` | `/api/auth/logout` | Terminate session | Authenticated |
| `GET` | `/api/auth/me` | Get current user profile & role | Authenticated |
| `GET` | `/api/teacher/classes` | List assigned classes & subjects | Teacher |
| `GET` | `/api/teacher/classes/<id>/students` | Get student roster for marking | Teacher |
| `POST` | `/api/teacher/attendance` | Submit & lock attendance session | Teacher |
| `GET` | `/api/teacher/attendance/history` | View teacher's past marked sessions | Teacher |
| `GET` | `/api/student/attendance` | Get overall & subject-wise % with alerts | Student |
| `GET` | `/api/student/attendance/history` | Detailed day-by-day attendance log | Student |
| `GET` | `/api/admin/dashboard-stats` | Summary KPI counts & health metrics | Admin |
| `GET` | `/api/admin/students` | List all students with class filters | Admin |
| `POST` | `/api/admin/students` | Create new student profile | Admin |
| `PUT` | `/api/admin/students/<id>` | Update student profile | Admin |
| `DELETE` | `/api/admin/students/<id>` | Soft-deactivate student profile | Admin |
| `GET` | `/api/admin/teachers` | List faculty members & assignments | Admin |
| `POST` | `/api/admin/teachers` | Create new faculty account | Admin |
| `PUT` | `/api/admin/teachers/<id>` | Update faculty details | Admin |
| `DELETE` | `/api/admin/teachers/<id>` | Soft-deactivate faculty member | Admin |
| `GET` | `/api/admin/classes` | List classes & curriculum mappings | Admin |
| `POST` | `/api/admin/classes` | Create new academic class section | Admin |
| `GET` | `/api/admin/attendance` | Filterable institutional attendance log | Admin |
| `POST` | `/api/admin/attendance/correct` | Unlock, adjust status, and log audit trail | Admin |
| `GET` | `/api/admin/attendance/corrections` | Fetch complete audit trail records | Admin |
| `GET` | `/api/admin/reports/shortage` | Fetch students with <75% attendance | Admin |

---

## 🧪 Test Suite & Quality Assurance

AttendX includes an automated test suite verifying business logic and security constraints:

```bash
python -m unittest test_app.py
```

### Verified Test Cases (8/8 Passing):
- `test_login_logout_flow`: Multi-role login, invalid credential rejection, and secure session clearing.
- `test_teacher_session_persistence`: Multi-class marking without re-authentication.
- `test_teacher_submit_and_lock`: Immediate record freezing and rejection of post-submit teacher edits.
- `test_student_attendance_calculation_and_alert`: Percentage calculation and `< 75%` danger flag trigger.
- `test_admin_correction_with_reason_and_audit`: Record modification, mandatory justification enforcement, auto-relock, and `attendance_corrections` logging.
- `test_teacher_soft_deactivation`: Inactive teacher login prevention while retaining past attendance records.
- `test_period_and_duplicate_attendance_prevention`: Duplicate slot detection for the same student/subject/date/period.
- `test_rest_api_endpoints`: Verification of JSON REST API responses and HTTP status codes.

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- pip & virtualenv

### 2. Setup Environment
```bash
# Clone the repository
git clone <repository-url>
cd attendx

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Database (.env)
A default `.env.example` file is provided. To run with SQLite out-of-the-box (zero configuration needed):
```bash
cp .env.example .env
```

To run with MySQL, set your database credentials in `.env`:
```ini
SECRET_KEY=attendx-secret-key-hackathon-2026
DB_NAME=attendx
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
```

### 4. Seed Database with Demo Accounts
```bash
python seed.py
```

### 5. Launch Development Server
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🔑 Demo Credentials

| Role | Email | Password | Assigned Section / Subject |
|---|---|---|---|
| **Admin** | `priya@college.edu` | `admin123` | Institutional Control Center |
| **Teacher** | `suresh@college.edu` | `teacher123` | BCA 3A (Data Structures, DBMS) |
| **Teacher** | `meera@college.edu` | `teacher123` | BCA 3A & 3B (Operating Systems) |
| **Student** | `rahul@student.edu` | `student123` | Roll No: BCA21 (BCA 3A) |
| **Student** | `anita@student.edu` | `student123` | Roll No: BCA22 (BCA 3A) |
| **Student** | `rohan@student.edu` | `student123` | Roll No: BCA23 (BCA 3A) |

---

## 📁 Project Directory Structure

```
attendx/
├── app.py                      # Flask Application Factory & Route Registration
├── config.py                   # Environment & Database Configuration (AttendX)
├── db.py                       # SQLAlchemy Instance Initialization
├── models.py                   # 9 Relational SQLAlchemy Database Models
├── auth.py                     # Session & Role-Based Access Control Decorators
├── seed.py                     # Demo Data Seeder with Multi-Subject Attendance
├── test_app.py                 # 8 Automated Unittest Suites
├── requirements.txt            # Python Dependencies
├── .env.example                # Sample Environment Template
├── routes/
│   ├── auth_routes.py          # Login, Logout, Session Handlers
│   ├── student_routes.py       # Student Dashboard & 9 Sub-Pages
│   ├── teacher_routes.py       # Teacher Hub, Marking, & 9 Sub-Pages
│   ├── admin_routes.py         # Admin Control Center, CRUD & Audit Workflow
│   └── api_routes.py           # 24 REST JSON Endpoints
├── static/
│   ├── css/
│   │   └── style.css           # Custom Academic Blue ERP Design System
│   └── js/
│       ├── main.js             # Circular Ring Gauges & Alert Auto-Dismiss
│       ├── teacher.js          # Rapid Mark Attendance & Bulk Toggles
│       └── admin.js            # Admin Audit Modals & Correction Handlers
└── templates/
    ├── base.html               # Master Layout with Dynamic Mobile Bottom Bar
    ├── login.html              # ERP Login Interface
    ├── student/                # 9 Student Sub-Page Templates
    │   ├── dashboard.html      # Main Student Hub with Conic Gauges
    │   ├── attendance.html     # Subject-Wise Detail & Shortage Badges
    │   ├── schedule.html       # Timetable
    │   ├── assignments.html    # Coursework
    │   ├── fees.html           # Fee Receipts & Dues
    │   ├── results.html        # SGPA/CGPA & Marksheets
    │   ├── notices.html        # Institutional Circulars
    │   ├── profile.html        # Digital Student ID Card
    │   ├── messages.html       # Faculty Chat
    │   └── notifications.html  # System Alerts
    ├── teacher/                # 9 Teacher Sub-Page Templates
    │   ├── dashboard.html      # Teacher Hub & Action Matrix
    │   ├── mark_attendance.html# Rapid Attendance Marker with Lockout
    │   ├── classes.html        # Assigned Class Sections
    │   ├── students.html       # Enrolled Student Roster
    │   ├── assignments.html    # Homework Publisher
    │   ├── marks.html          # CIA & Midterm Marks Entry
    │   ├── timetable.html      # Faculty Weekly Schedule
    │   ├── notices.html        # Department Notices
    │   ├── messages.html       # Student Queries
    │   └── profile.html        # Faculty Profile
    └── admin/                  # Admin Governance Templates
        ├── dashboard.html      # Institutional Analytics & KPI Overview
        ├── manage_students.html# Student Directory & CRUD
        ├── manage_teachers.html# Faculty Directory & Section Mapping
        ├── manage_classes.html # Curriculum & Section Config
        ├── view_attendance.html# Master Attendance Log Explorer
        ├── correct_attendance.html # Audited Correction Workflow
        ├── audit_log.html      # Permanent Immutable Audit Ledger
        ├── reports.html        # <75% Shortage Analytics
        ├── notices.html        # Broadcast Publisher
        ├── timetable.html      # Institutional Timetable Matrix
        └── profile.html        # Administrator Profile
```

---

## 🔒 Security & Compliance Highlights

- **Password Protection:** Cryptographic hashing using PBKDF2 / SHA256 via Werkzeug security.
- **Server-Side Authorization:** Zero client-side trust; each route verifies session role (`@role_required('admin')`, `@role_required('teacher')`, `@role_required('student')`).
- **Submit-and-Lock Immutability:** Enforced at database and route levels to prevent attendance tampering.
- **Strict Audit Integrity:** No silent edits allowed. Any change to a locked attendance record requires an Admin user, an explicit justification string, and generates a non-erasable record in `attendance_corrections`.
- **Safe Soft Deactivation:** Deactivating faculty or students updates `active=False`, preventing future logins while preserving historical attendance accuracy.

---

## 📜 License
Distributed under the MIT License for educational and institutional evaluation.
