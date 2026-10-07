# Campus Career & Internship Management System

A Flask and MySQL DBMS application for managing student profiles, skills, certifications, internship opportunities, applications, interviews, and offers.

## Objectives

- Maintain student academic profiles, skills, certifications, and applications.
- Allow companies to manage profiles, jobs, required skills, applicants, interviews, and offers.
- Provide eligibility checking using CGPA and required skills.
- Demonstrate normalized relational design, constraints, transactions, authentication, and role-based access.

## Technology stack

- Python 3.12+
- Flask
- MySQL 8+
- `mysql-connector-python`
- Bootstrap, HTML, CSS, and JavaScript

## Architecture

- `database/`: MySQL database, schema, sample data, authentication-table, and query scripts.
- `app/app.py`: Flask routes, validation, authentication, authorization, and business workflows.
- `app/db.py`: environment-based MySQL connection helper.
- `app/templates/`: Jinja templates.
- `app/static/`: CSS and JavaScript assets.
- `diagrams/`: ER diagrams.
- `docs/`: database design documentation.

## Database

The approved Phase 1 schema contains:

`DEPARTMENT`, `STUDENT`, `SKILL`, `STUDENT_SKILL`, `CERTIFICATION`, `COMPANY`, `RECRUITER`, `JOB`, `JOB_SKILL`, `APPLICATION`, `INTERVIEW`, and `OFFER`.

Phase 2 adds `USER_ACCOUNT` for authentication. The scripts are intended to be reviewed and executed manually in MySQL Workbench; the Flask application does not create or alter the schema automatically.

## Main features

- Student registration and login.
- Company registration and login.
- Admin, student, and company role-based dashboards.
- Student profile, skill, and certification self-service.
- Company profile and job self-service.
- Job browsing and eligibility checking.
- Application submission and status tracking.
- Company interview scheduling, editing, and cancellation.
- Company offer creation, editing, and historical withdrawal.
- Application, interview, and offer detail views.
- Parameterized SQL and transactional multi-table updates.

## Roles

### Student

Students can manage their own profile, skills, and certifications; browse jobs; check eligibility; apply; and view only their own applications, interviews, and offers.

### Company

Companies can manage their own profile and jobs, required job skills, applicants, application statuses, interviews, and offers. Ownership is checked through the authenticated `USER_ACCOUNT.Company_ID`.

### Admin

Admins can access the administrative dashboard and existing system-wide monitoring views. There is no public admin-registration workflow.

## Setup

Create and activate a Python virtual environment, then install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and provide local values. `.env` is ignored by Git and must never be committed:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=campus_career_db
DEMO_ADMIN_PASSWORD=
DEMO_STUDENT_PASSWORD=
DEMO_COMPANY_PASSWORD=
FLASK_SECRET_KEY=
```

The application defaults to `localhost`, `root`, and `campus_career_db` when corresponding database variables are absent. Set `DB_PASSWORD` and a strong `FLASK_SECRET_KEY` through the environment for real use.

## Database preparation

Review the SQL scripts in order and execute them manually in MySQL Workbench:

1. `database/01_create_database.sql`
2. `database/02_create_tables.sql`
3. `database/03_insert_sample_data.sql`
4. `database/05_create_user_account.sql`

`database/04_queries.sql` contains read-only demonstrations and commented maintenance examples. Do not run scripts against a production database without reviewing them first.

## Demo accounts

Set these environment variables locally before running the controlled demo-account setup:

- `DEMO_ADMIN_PASSWORD`
- `DEMO_STUDENT_PASSWORD`
- `DEMO_COMPANY_PASSWORD`

Then run:

```powershell
.\venv\Scripts\python.exe app\create_demo_accounts.py
```

The script hashes passwords with Werkzeug, does not print them, and does not write plaintext passwords to files. Never place real password values in source code, documentation, `.env.example`, or Git.

## Run Flask

From the repository root:

```powershell
$env:FLASK_APP = "app/app.py"
.\venv\Scripts\python.exe -m flask run
```

Open the local URL shown by Flask in a browser.

## Repository safety

Before committing, review:

```powershell
git status --short
git diff --check
git diff --stat
```

Do not stage `.env`, virtual environments, caches, local database files, logs, or credentials. Use an explicit `git add` file list after reviewing the status; never commit or push secrets.
