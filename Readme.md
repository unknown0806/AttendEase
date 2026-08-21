# AttendEase

**Smart Attendance Management System**

> Web app that locks teacher attendance after submit, skips repeat logins across classes, and warns students per-subject when attendance drops below 75%.

---

## Problem

Manual and semi-digital attendance tracking (paper registers, spreadsheets, basic forms) is slow, error-prone, and easy to manipulate. Teachers waste time re-logging in between back-to-back classes. Students often don't realize they're below the attendance threshold until it's too late. There is no tamper-proof record-locking mechanism to prevent post-submission edits.

---

## Solution

A lightweight 3-role web application:
- **Teacher** logs in once — session persists across multiple class attendance sessions, no repeated login.
- Teacher marks attendance per period/session → submission locks the record.
- **Student** dashboard displays attendance percentage per subject, with a red alert badge on any subject below 75%.
- **Admin** is the only role permitted to unlock, correct (with mandatory reason), and re-lock submitted attendance — every correction is logged for full audit traceability.

---

## Key Features

- 3-role authentication (Teacher / Student / Admin) with persistent login session
- Attendance marking per class + period, with submit-and-lock mechanism
- Student dashboard — subject-wise attendance %, red alert badge below 75%
- Admin — Manage Students (add/edit/deactivate/assign class)
- Admin — Manage Teachers (add/edit/assign to subject-class/deactivate)
- Admin — Manage Classes & Subjects (create, assign)
- Admin — View Attendance (filter by class/subject/teacher/student/date/period)
- Admin — Correct Locked Attendance (unlock, mandatory reason, edit, auto re-lock, full audit trail via `attendance_corrections`)

---

## Demo

*Placeholder — add link to live demo or demo video here.*

---

## Screenshots

*Placeholder — add screenshots of login page, teacher attendance marking, student dashboard, and admin panel here.*

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap (optional), minimal JS |
| Backend | Python (Flask) |
| Templating | Jinja2 |
| Database | MySQL |
| ORM | Flask-SQLAlchemy |
| Auth | Flask session + Werkzeug password hashing |
| Hosting (demo) | Render / PythonAnywhere / Replit *(placeholder — confirm actual choice)* |

---

## Architecture Overview

Single Flask app, server-rendered pages (Jinja2 templates) — no separate frontend framework, no microservices, no Docker.

```
[Browser] → [Flask App (single instance)] → [MySQL Database]
```

- **Auth:** session-based login (Flask `session`), role checked server-side on every protected route.
- **Lock mechanism:** `locked` boolean on `attendance` table; teacher cannot edit once `locked=True`; only admin route bypasses this check.
- **Correction:** admin-only, single atomic action — unlock, edit, log to `attendance_corrections` (mandatory reason), re-lock.

---

## Project Structure

```
attendease/
├── app.py                     # main Flask app + routes
├── db.py                      # database connection setup
├── models.py                  # SQLAlchemy table definitions
├── auth.py                    # login/session helper functions
├── requirements.txt           # Flask, mysql-connector, etc.
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   └── mark_attendance.html
│   ├── student/
│   │   └── dashboard.html
│   └── admin/
│       ├── dashboard.html
│       ├── manage_students.html
│       ├── manage_teachers.html
│       ├── manage_classes.html
│       ├── view_attendance.html
│       └── correct_attendance.html
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## Prerequisites

- Python 3.x
- MySQL Server
- pip (Python package manager)

*Placeholder — confirm exact versions used.*

---

## Installation

```bash
# clone the repository
git clone <repository-url>
cd attendease

# create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=<your-flask-secret-key>
DB_HOST=<your-mysql-host>
DB_USER=<your-mysql-user>
DB_PASSWORD=<your-mysql-password>
DB_NAME=attendease
```

*Placeholder — adjust variable names to match actual config code.*

---

## How to Run Frontend

Frontend is server-rendered by Flask (Jinja2 templates) — no separate frontend build/run step needed. It runs automatically when the backend Flask server starts (see below).

---

## How to Run Backend

```bash
python app.py
```

App will be available at `http://localhost:5000` *(placeholder — confirm actual port).*

---

## Database Setup

1. Create the MySQL database:
```sql
CREATE DATABASE attendease;
```

2. Run the schema (see full SQL in `DB_Schema_AttendEase.md`):
```sql
-- creates: users, classes, subjects, class_subjects, teacher_subjects,
-- students, periods, attendance, attendance_corrections
```

3. *(Optional)* Seed initial admin user and sample data — placeholder, add seed script path if available.

---

## API Documentation

Full REST API specification (24 endpoints covering auth, teacher attendance marking, student dashboard, and admin management/correction) is available in `API_Spec_AttendEase.md`.

Summary of endpoint groups:
- `/api/auth/*` — login, logout
- `/api/teacher/*` — class list, student list, submit attendance
- `/api/student/attendance` — subject-wise % + alerts
- `/api/admin/*` — manage students, teachers, classes, subjects, view attendance, correct locked records

---

## Testing

*Placeholder — add testing approach once implemented (e.g. manual click-through testing for demo, or specific test files if written).*

---

## Deployment

Single-app deployment, no load balancer or multi-server setup needed for hackathon demo:

```
[Browser] → [Flask App (single instance)] → [MySQL Database]
```

- Host Flask app on Render, Railway, or PythonAnywhere (free tier, auto HTTPS)
- MySQL: managed MySQL from hosting provider, or free tier (Railway MySQL / Clever Cloud)
- Environment variables stored in host's config panel, not hardcoded

*Placeholder — confirm actual deployment URL once live.*

---

## Future Improvements

- Attendance trend charts/graphs
- Email/SMS notification to student on low attendance
- Export attendance as PDF/Excel
- Search/filter enhancements
- UI polish (dark mode, improved styling)

*(Explicitly out of scope for this hackathon build: biometric/facial recognition, native mobile app, AI-based prediction/analytics, multi-school support, third-party SMS/payment integration.)*

---

## Team Members

*Placeholder — add team member names and roles.*