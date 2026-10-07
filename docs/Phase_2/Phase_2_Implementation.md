# Phase 2 – Implementation

## 1. Project Overview

The Campus Career & Internship Management System is a Flask and MySQL application that connects students, companies, recruiters, internship opportunities, applications, interviews, and offers in one normalized DBMS project.

Phase 2 extends the approved Phase 1 database design into a working application. It adds sample DML, database connectivity, a browser-based interface, authentication, role-based authorization, eligibility checking, application workflows, student self-service, company self-service, interview management, and offer management.

## 2. Technology Stack

The implemented system uses:

- Python
- Flask
- MySQL
- `mysql-connector-python`
- HTML
- CSS
- JavaScript
- Bootstrap and Bootstrap Icons through the application templates
- MySQL Workbench for manual database-script execution and inspection

## 3. System Architecture

The application follows this flow:

```text
Browser
    ↓
HTML / CSS / JavaScript + Bootstrap
    ↓
Flask application
    ↓
MySQL database
```

The browser submits requests to Flask routes. Flask validates requests, applies role and ownership checks, executes parameterized MySQL queries, and renders Jinja templates. MySQL stores the normalized project data.

## 4. DML and Sample Data

The Phase 2 sample-data script inserts and verifies fictional records for:

| Table | Sample records |
|---|---:|
| `DEPARTMENT` | 4 |
| `STUDENT` | 8 |
| `SKILL` | 10 |
| `STUDENT_SKILL` | 14 |
| `CERTIFICATION` | 6 |
| `COMPANY` | 4 |
| `RECRUITER` | 5 |
| `JOB` | 8 |
| `JOB_SKILL` | 16 |
| `APPLICATION` | 10 |
| `INTERVIEW` | 5 |
| `OFFER` | 3 |

The data preserves the approved Phase 1 relationships and constraints. Open-job deadlines were prepared for the October 2026 Phase 2 workflow. The sample data includes open and closed jobs, different application statuses, interview records, and accepted or pending offers.

## 5. Database Connectivity

Flask connects to MySQL through [`app/db.py`](../../app/db.py). The connection helper reads:

- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

Database credentials are obtained from environment variables and are not hardcoded in the source code. Database errors are converted into safe application errors without exposing connection details.

## 6. Authentication

The implemented authentication features include:

- Login with email, password, and role.
- Logout through Flask session clearing.
- Student registration.
- Company registration.
- Controlled admin account setup.
- The `USER_ACCOUNT` table for account identity and role linkage.
- Password hashing with Werkzeug.
- Session-based authentication.

`USER_ACCOUNT` stores the account email, password hash, role, and optional student or company relationship. Admin accounts have neither relationship; student accounts link to `STUDENT`; company accounts link to `COMPANY`.

Passwords are never stored in plaintext, placed in the session, printed, or included in this documentation.

## 7. Role-Based Authorization

### Admin

Admins have system-wide monitoring and management access through the administrative dashboard and existing system views, including students, companies, jobs, applications, eligibility information, interviews, and offers.

### Student

Students can access their own profile, skills, certifications, internships, eligibility information, applications, interview information, and offer information. Students cannot manage company jobs, interviews, or offers.

### Company

Companies can manage their own company profile, jobs, required job skills, applicants, application statuses, interviews, and offers.

Route-level role decorators prevent users from entering another role’s protected pages. Ownership checks resolve the authenticated student or company relationship through `USER_ACCOUNT` and compare it with database relationships before reading or changing records.

## 8. Student Self-Service

Authenticated students can:

- Edit their own profile.
- Update name, email, phone, date of birth, CGPA, department, and graduation year.
- Add existing skills.
- Set or update skill proficiency.
- Remove their own skills.
- Add certifications.
- Delete their own certifications.
- View their applications and application status.
- View related interview and offer information.

Student operations use the authenticated `Student_ID`; student IDs supplied by URLs or forms are not trusted for ownership.

## 9. Student Registration

Student registration uses a transaction:

```text
Student registration
        ↓
STUDENT
        ↓
STUDENT_SKILL
        ↓
USER_ACCOUNT
```

The workflow validates the submitted profile, department, skills, email, CGPA, dates, and proficiency values. It inserts the student, obtains the generated `Student_ID`, inserts selected skill relationships, creates the linked student account, and commits the transaction.

If a step fails, the transaction is rolled back so that a partial student, partial skill relationships, or partial account is not left behind.

## 10. Company Self-Service

Authenticated companies can:

- Edit their own company profile.
- Update the company email and corresponding account email together.
- Create jobs and internships.
- Edit their own jobs.
- Replace required job skills using `JOB_SKILL`.
- Close their own jobs without deleting them.
- View applicants for their own jobs.
- Update application statuses for their own jobs.

Company profile and job operations use parameterized SQL and ownership checks based on the authenticated `Company_ID`.

## 11. Eligibility

The eligibility checker evaluates:

- Student minimum CGPA requirements.
- All required job skills.
- Job status.
- Application deadline.
- Whether the student has already applied.

Academic eligibility and duplicate application state are kept separate. A student who meets the CGPA and skill requirements but has already applied is shown as eligible by requirements but cannot submit a duplicate application. A student missing a required skill is not eligible by requirements.

The implemented workflow includes the tested distinction between Aarav Mehta’s eligible existing application and Diya Nair’s missing-SQL case for the Python Developer Intern opportunity.

## 12. Application Management

Students can apply for eligible internships or jobs. The application workflow checks:

- Student ownership.
- CGPA.
- Required skills.
- Job status.
- Application deadline.
- Duplicate applications.

The database’s unique `(Student_ID, Job_ID)` constraint provides an additional duplicate-prevention safeguard.

Companies can view applicants for their own jobs and update application statuses. Students can view only their own applications. Admins retain application visibility.

The implemented recruitment workflow is:

```text
Applied
    → Shortlisted
    → Interview
    → Selected / Rejected
    → Offer
```

## 13. Interview Management

Companies can schedule, edit, and cancel interviews for applications belonging to their own jobs.

Interview fields include:

- Interview date
- Interview time
- Mode
- Status
- Remarks

Existing interview statuses are preserved:

- `Scheduled`
- `Completed`
- `Cancelled`

Existing interview modes are preserved:

- `Online`
- `In-person`

Cancellation changes the status to `Cancelled` rather than deleting the historical interview record. Company ownership is validated through `INTERVIEW → APPLICATION → JOB → COMPANY`.

Students can view interview information for their own applications, while companies receive management controls only for their own applications. Admins retain viewing access.

## 14. Offer Management

Companies can create, edit, and withdraw offers for applications belonging to their own jobs.

Offer fields include:

- Offer date
- Job title
- Salary
- Joining date
- Offer status

An offer can be issued only when the application status is `Selected`. The unique `OFFER.Application_ID` constraint ensures that an application cannot receive duplicate offers. The application checks for an existing offer before insertion and directs the company to edit the existing offer instead.

The sample data uses `Accepted` and `Pending` offer statuses. The implementation also uses the application-level `Withdrawn` status for safe historical withdrawal. Offers are updated rather than physically deleted.

Students can view offer information for their own applications. Companies can edit or withdraw only offers connected to their own jobs.

## 15. Security

Implemented security controls include:

- Password hashing with `generate_password_hash`.
- Password verification with `check_password_hash`.
- Parameterized SQL queries.
- Flask session-based authentication.
- Minimal session identity data.
- Role-based route protection.
- Student ownership checks.
- Company ownership checks.
- Transactions for related multi-step changes.
- Rollback on failed registration and update operations.
- No plaintext passwords.
- Environment variables for database credentials and demo-account passwords.

The application does not execute database schema creation automatically. SQL scripts are reviewed and executed manually in MySQL Workbench.

## 16. Validation and Testing

The repository implementation was validated through:

- Python syntax validation.
- Pylance diagnostics with no reported errors for the main application module.
- Python `compileall`.
- Flask route loading and URL-map inspection.
- Jinja template loading checks.
- `git diff --check`.
- Mocked authentication and password-verification checks.
- Session-minimality checks.
- Mocked role and ownership protection checks.
- Mocked student and company registration transaction-sequence checks.
- Input-validation checks for student profile, skill, certification, company, job, interview, and offer workflows.
- Verification of existing eligibility and application workflow routing.
- Verification of interview and offer route registration.

No live SQL was executed during the implementation and documentation work described here. Database behavior was validated through schema inspection, parameterized query review, and mocked or local application checks.

## 17. Project Structure

```text
Campus-Career-Internship-Management-System/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── app.py
│   ├── create_demo_accounts.py
│   ├── db.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
├── database/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_insert_sample_data.sql
│   ├── 04_queries.sql
│   └── 05_create_user_account.sql
├── diagrams/
│   ├── ER_Diagram.drawio
│   └── Campus_Career_Internship_ER_Diagram_Clean (1).drawio.png
└── docs/
    ├── Phase_1/
    │   ├── .gitkeep
    │   └── Phase_1_Database_Design.md
    └── Phase_2/
        └── Phase_2_Implementation.md
```

## 18. Phase 2 Assessment Mapping

### DML — Completed

`database/03_insert_sample_data.sql` provides fictional records across the approved relational tables. The data supports demonstrations of joins, eligibility, applications, interviews, offers, and dashboard statistics.

### Frontend — Completed

The Flask application renders Bootstrap-based HTML templates with shared navigation, dashboards, forms, tables, detail views, status displays, and responsive CSS/JavaScript assets.

### Business Logic — Completed

The application implements registration, authentication, role protection, ownership checks, eligibility, duplicate application prevention, student self-service, company self-service, application status updates, interview workflows, and offer workflows.

### Connectivity — Completed

`app/db.py` connects Flask to MySQL using environment-based settings and `mysql-connector-python`. Application routes use parameterized queries and transaction handling for related updates.

## 19. Evidence Checklist

The following screenshots or recordings should be captured for the final submission:

- [ ] Student registration form and successful registration result.
- [ ] Student dashboard.
- [ ] Student profile editing.
- [ ] Student skills and proficiency management.
- [ ] Student certification management.
- [ ] Company dashboard.
- [ ] Job creation form and created opportunity.
- [ ] Job editing, required skills, and job closing.
- [ ] Eligibility checker showing CGPA and required-skill evaluation.
- [ ] Application submission and application detail.
- [ ] Company applicant view and application status update.
- [ ] Interview scheduling, editing, and cancellation.
- [ ] Offer creation, editing, and withdrawal.
- [ ] Admin dashboard and monitoring views.
- [ ] MySQL Workbench showing the approved tables and sample data.
- [ ] Flask application running in the browser.

These are evidence items to capture from the working system; no screenshots are embedded in this document.

## 20. Conclusion

Phase 2 transformed the approved relational design into a working Flask and MySQL DBMS application. It now includes verified sample data, environment-based connectivity, secure authentication, role-based access, student and company self-service, eligibility evaluation, application tracking, interview management, and offer management while preserving the normalized database structure and existing relationships.
