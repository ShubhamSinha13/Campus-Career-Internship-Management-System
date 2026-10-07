from datetime import date, datetime
from functools import wraps
import re

from flask import Flask, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection


app = Flask(__name__)
app.secret_key = __import__("os").environ.get("FLASK_SECRET_KEY", "change-this-development-secret")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                return render_template("forbidden.html"), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def execute_transaction(statements):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        results = []
        for query, params in statements:
            cursor.execute(query, params)
            results.append(cursor.lastrowid)
        connection.commit()
        return results
    except (RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        raise RuntimeError("The requested operation could not be completed.")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def set_authenticated_user(account):
    session.clear()
    session["user_id"] = account["User_ID"]
    session["role"] = account["Role"]


def validate_account_relationship(role, student_id=None, company_id=None):
    valid = (
        (role == "ADMIN" and student_id is None and company_id is None)
        or (role == "STUDENT" and student_id is not None and company_id is None)
        or (role == "COMPANY" and student_id is None and company_id is not None)
    )
    if not valid:
        raise ValueError("Invalid authentication account relationship.")


def get_linked_account_id(column):
    if column not in {"Student_ID", "Company_ID"}:
        raise ValueError("Invalid account link column.")
    account = query_db(
        f"SELECT {column} FROM USER_ACCOUNT WHERE User_ID = %s AND Role = %s",
        (session["user_id"], session["role"]),
        fetch_one=True,
    )
    return account[column] if account else None


@app.context_processor
def authentication_context():
    return {"current_role": session.get("role")}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "").upper()
        account = query_db(
            """SELECT User_ID, Email, Password_Hash, Role, Student_ID, Company_ID
               FROM USER_ACCOUNT WHERE Email = %s AND Role = %s""",
            (email, role), fetch_one=True)
        if account and check_password_hash(account["Password_Hash"], password):
            set_authenticated_user(account)
            destination = {"ADMIN": "admin", "STUDENT": "student_dashboard",
                           "COMPANY": "company_dashboard"}[account["Role"]]
            return redirect(url_for(destination))
        flash("Invalid email, password, or role.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    try:
        departments = query_db("SELECT Department_ID, Department_Name FROM DEPARTMENT ORDER BY Department_Name")
        skills = query_db("SELECT Skill_ID, Skill_Name FROM SKILL ORDER BY Skill_Name")
    except RuntimeError:
        return render_database_error()
    if request.method == "POST":
        form = request.form
        try:
            cgpa = float(form.get("cgpa", ""))
            department_id = int(form.get("department_id", ""))
            graduation_year = int(form.get("graduation_year", ""))
            selected_skills = [(int(skill_id), form.get(f"proficiency_{skill_id}", "Beginner"))
                               for skill_id in form.getlist("skills")]
            if not 0 <= cgpa <= 10:
                raise ValueError
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO STUDENT
                (Name, Email, Phone, DOB, CGPA, Graduation_Year, Department_ID)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (form["name"].strip(), form["email"].strip().lower(), form.get("phone"),
                 form["dob"], cgpa, graduation_year, department_id))
            student_id = cursor.lastrowid
            for skill_id, proficiency in selected_skills:
                cursor.execute("INSERT INTO STUDENT_SKILL (Student_ID, Skill_ID, Proficiency) VALUES (%s,%s,%s)",
                               (student_id, skill_id, proficiency))
            validate_account_relationship("STUDENT", student_id=student_id)
            cursor.execute("""INSERT INTO USER_ACCOUNT
                (Email, Password_Hash, Role, Student_ID) VALUES (%s,%s,'STUDENT',%s)""",
                (form["email"].strip().lower(), generate_password_hash(form["password"]), student_id))
            connection.commit()
            cursor.close()
            connection.close()
            account = query_db("SELECT User_ID, Role FROM USER_ACCOUNT WHERE Student_ID = %s",
                               (student_id,), fetch_one=True)
            set_authenticated_user(account)
            return redirect(url_for("student_dashboard"))
        except (KeyError, TypeError, ValueError, RuntimeError, Error):
            if "connection" in locals() and connection is not None:
                connection.rollback()
                connection.close()
            flash("Please provide valid registration details. Email addresses must be unique.", "danger")
    return render_template("register_student.html", departments=departments, skills=skills)


@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        form = request.form
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO COMPANY
                (Company_Name, Industry, Location, Website, Email, Phone)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (form["name"].strip(), form["industry"].strip(), form["location"].strip(),
                 form.get("website"), form["email"].strip().lower(), form.get("phone")))
            company_id = cursor.lastrowid
            validate_account_relationship("COMPANY", company_id=company_id)
            cursor.execute("""INSERT INTO USER_ACCOUNT
                (Email, Password_Hash, Role, Company_ID) VALUES (%s,%s,'COMPANY',%s)""",
                (form["email"].strip().lower(), generate_password_hash(form["password"]), company_id))
            connection.commit()
            cursor.close()
            connection.close()
            account = query_db("SELECT User_ID, Role FROM USER_ACCOUNT WHERE Company_ID = %s",
                               (company_id,), fetch_one=True)
            set_authenticated_user(account)
            return redirect(url_for("company_dashboard"))
        except (KeyError, TypeError, ValueError, RuntimeError, Error):
            if connection is not None:
                connection.rollback()
                connection.close()
            flash("Please provide valid company details. Account email must be unique.", "danger")
    return render_template("register_company.html")


@app.route("/admin")
@role_required("ADMIN")
def admin():
    try:
        stats = {
            "students": query_db("SELECT COUNT(*) AS total FROM STUDENT", fetch_one=True)["total"],
            "companies": query_db("SELECT COUNT(*) AS total FROM COMPANY", fetch_one=True)["total"],
            "opportunities": query_db("SELECT COUNT(*) AS total FROM JOB", fetch_one=True)["total"],
            "open_opportunities": query_db("SELECT COUNT(*) AS total FROM JOB WHERE Status='Open'", fetch_one=True)["total"],
            "applications": query_db("SELECT COUNT(*) AS total FROM APPLICATION", fetch_one=True)["total"],
            "shortlisted": query_db("SELECT COUNT(*) AS total FROM APPLICATION WHERE Status='Shortlisted'", fetch_one=True)["total"],
            "selected": query_db("SELECT COUNT(*) AS total FROM APPLICATION WHERE Status='Selected'", fetch_one=True)["total"],
            "rejected": query_db("SELECT COUNT(*) AS total FROM APPLICATION WHERE Status='Rejected'", fetch_one=True)["total"],
            "interviews": query_db("SELECT COUNT(*) AS total FROM INTERVIEW", fetch_one=True)["total"],
            "offers": query_db("SELECT COUNT(*) AS total FROM OFFER", fetch_one=True)["total"],
        }
        return render_template("admin.html", stats=stats)
    except RuntimeError:
        return render_database_error()


@app.route("/student")
@role_required("STUDENT")
def student_dashboard():
    try:
        student_id = get_linked_account_id("Student_ID")
        if student_id is None:
            return render_template("forbidden.html"), 403
        student = query_db("""SELECT s.*, d.Department_Name FROM STUDENT s
            JOIN DEPARTMENT d ON d.Department_ID=s.Department_ID WHERE s.Student_ID=%s""",
            (student_id,), fetch_one=True)
        skills = query_db("""SELECT sk.Skill_ID, sk.Skill_Name, ss.Proficiency FROM STUDENT_SKILL ss
            JOIN SKILL sk ON sk.Skill_ID=ss.Skill_ID WHERE ss.Student_ID=%s ORDER BY sk.Skill_Name""", (student_id,))
        applications = query_db("""SELECT a.Application_ID, j.Job_Title, c.Company_Name, a.Status
            FROM APPLICATION a JOIN JOB j ON j.Job_ID=a.Job_ID JOIN COMPANY c ON c.Company_ID=j.Company_ID
            WHERE a.Student_ID=%s ORDER BY a.Application_Date DESC""", (student_id,))
        certifications = query_db("""SELECT Certification_ID, Certification_Name,
            Issuing_Organization, Issue_Date, Expiry_Date
            FROM CERTIFICATION WHERE Student_ID=%s ORDER BY Issue_Date DESC""", (student_id,))
        available_skills = query_db("SELECT Skill_ID, Skill_Name FROM SKILL ORDER BY Skill_Name")
        return render_template("student_dashboard.html", student=student, skills=skills,
                               applications=applications, certifications=certifications,
                               available_skills=available_skills)
    except RuntimeError:
        return render_database_error()


def parse_student_id():
    student_id = get_linked_account_id("Student_ID")
    if student_id is None:
        raise ValueError("Student account is not linked.")
    return student_id


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def parse_date_value(value, required=True):
    if not value and not required:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.route("/student/profile/edit", methods=["GET", "POST"])
@role_required("STUDENT")
def edit_student_profile():
    connection = None
    cursor = None
    try:
        student_id = parse_student_id()
        if request.method == "POST":
            form = request.form
            name = form.get("name", "").strip()
            email = form.get("email", "").strip().lower()
            phone = form.get("phone", "").strip()
            cgpa = float(form.get("cgpa", ""))
            department_id = int(form.get("department_id", ""))
            graduation_year = int(form.get("graduation_year", ""))
            dob = parse_date_value(form.get("dob", ""))
            if not name or not valid_email(email) or not 0 <= cgpa <= 10:
                raise ValueError
            if (graduation_year < 1900 or graduation_year > 2200 or
                    (phone and not re.fullmatch(r"[0-9+().\-\s]{7,20}", phone))):
                raise ValueError
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT Department_ID FROM DEPARTMENT WHERE Department_ID = %s",
                (department_id,),
            )
            if cursor.fetchone() is None:
                raise ValueError
            cursor.execute(
                """SELECT User_ID FROM USER_ACCOUNT
                   WHERE Email = %s AND User_ID <> %s""",
                (email, session["user_id"]),
            )
            if cursor.fetchone() is not None:
                raise ValueError
            cursor.execute(
                """UPDATE STUDENT
                   SET Name=%s, Email=%s, Phone=%s, DOB=%s, CGPA=%s,
                       Graduation_Year=%s, Department_ID=%s
                   WHERE Student_ID=%s""",
                (name, email, phone or None, dob, cgpa, graduation_year,
                 department_id, student_id),
            )
            cursor.execute(
                """UPDATE USER_ACCOUNT SET Email=%s
                   WHERE User_ID=%s AND Role='STUDENT' AND Student_ID=%s""",
                (email, session["user_id"], student_id),
            )
            connection.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("student_dashboard"))
        student = query_db(
            """SELECT s.*, d.Department_Name FROM STUDENT s
               JOIN DEPARTMENT d ON d.Department_ID=s.Department_ID
               WHERE s.Student_ID=%s""",
            (student_id,), fetch_one=True,
        )
        departments = query_db(
            "SELECT Department_ID, Department_Name FROM DEPARTMENT ORDER BY Department_Name"
        )
        return render_template("student_profile_edit.html",
                               student=student, departments=departments)
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid profile details. Email must be unique.", "danger")
        if request.method == "POST":
            return redirect(url_for("edit_student_profile"))
        return render_database_error()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def skill_transaction(skill_id, proficiency=None, delete=False, allow_update=False):
    student_id = parse_student_id()
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        if delete:
            cursor.execute(
                "DELETE FROM STUDENT_SKILL WHERE Student_ID=%s AND Skill_ID=%s",
                (student_id, skill_id),
            )
        else:
            if proficiency not in {"Beginner", "Intermediate", "Advanced"}:
                raise ValueError
            cursor.execute("SELECT Skill_ID FROM SKILL WHERE Skill_ID=%s", (skill_id,))
            if cursor.fetchone() is None:
                raise ValueError
            cursor.execute(
                "SELECT Skill_ID FROM STUDENT_SKILL WHERE Student_ID=%s AND Skill_ID=%s",
                (student_id, skill_id),
            )
            exists = cursor.fetchone() is not None
            if exists and allow_update:
                cursor.execute(
                    """UPDATE STUDENT_SKILL SET Proficiency=%s
                       WHERE Student_ID=%s AND Skill_ID=%s""",
                    (proficiency, student_id, skill_id),
                )
            elif exists:
                raise ValueError
            else:
                cursor.execute(
                    """INSERT INTO STUDENT_SKILL
                       (Student_ID, Skill_ID, Proficiency) VALUES (%s,%s,%s)""",
                    (student_id, skill_id, proficiency),
                )
        connection.commit()
    except (ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        raise RuntimeError("Skill changes could not be saved.")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.post("/student/skills/add")
@role_required("STUDENT")
def add_student_skill():
    try:
        skill_transaction(int(request.form["skill_id"]),
                          request.form.get("proficiency", "Beginner"))
        flash("Skill saved successfully.", "success")
    except (KeyError, TypeError, ValueError, RuntimeError):
        flash("That skill could not be saved.", "danger")
    return redirect(url_for("student_dashboard"))


@app.post("/student/skills/update/<int:skill_id>")
@role_required("STUDENT")
def update_student_skill(skill_id):
    try:
        skill_transaction(skill_id, request.form.get("proficiency"),
                          allow_update=True)
        flash("Skill proficiency updated.", "success")
    except RuntimeError:
        flash("That skill could not be updated.", "danger")
    return redirect(url_for("student_dashboard"))


@app.post("/student/skills/delete/<int:skill_id>")
@role_required("STUDENT")
def delete_student_skill(skill_id):
    try:
        skill_transaction(skill_id, delete=True)
        flash("Skill removed.", "success")
    except RuntimeError:
        flash("That skill could not be removed.", "danger")
    return redirect(url_for("student_dashboard"))


@app.post("/student/certifications/add")
@role_required("STUDENT")
def add_student_certification():
    connection = None
    cursor = None
    try:
        student_id = parse_student_id()
        form = request.form
        name = form.get("certification_name", "").strip()
        organization = form.get("issuing_organization", "").strip()
        issue_date = parse_date_value(form.get("issue_date", ""))
        expiry_date = parse_date_value(form.get("expiry_date", ""), required=False)
        if not name or not organization or (expiry_date and expiry_date < issue_date):
            raise ValueError
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO CERTIFICATION
               (Student_ID, Certification_Name, Issuing_Organization,
                Issue_Date, Expiry_Date)
               VALUES (%s,%s,%s,%s,%s)""",
            (student_id, name, organization, issue_date, expiry_date),
        )
        connection.commit()
        flash("Certification added successfully.", "success")
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid certification details.", "danger")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
    return redirect(url_for("student_dashboard"))


@app.post("/student/certifications/delete/<int:certification_id>")
@role_required("STUDENT")
def delete_student_certification(certification_id):
    connection = None
    cursor = None
    try:
        student_id = parse_student_id()
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """DELETE FROM CERTIFICATION
               WHERE Certification_ID=%s AND Student_ID=%s""",
            (certification_id, student_id),
        )
        connection.commit()
        flash("Certification removed.", "success")
    except (RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("That certification could not be removed.", "danger")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
    return redirect(url_for("student_dashboard"))


@app.route("/company")
@role_required("COMPANY")
def company_dashboard():
    try:
        company_id = get_linked_account_id("Company_ID")
        if company_id is None:
            return render_template("forbidden.html"), 403
        company = query_db("SELECT * FROM COMPANY WHERE Company_ID=%s", (company_id,), fetch_one=True)
        stats = query_db("""SELECT
            (SELECT COUNT(*) FROM RECRUITER WHERE Company_ID=%s) recruiters,
            (SELECT COUNT(*) FROM JOB WHERE Company_ID=%s) opportunities,
            (SELECT COUNT(*) FROM JOB j JOIN APPLICATION a ON a.Job_ID=j.Job_ID WHERE j.Company_ID=%s) applicants,
            (SELECT COUNT(*) FROM JOB WHERE Company_ID=%s AND Status='Open') open_opportunities""",
            (company_id, company_id, company_id, company_id), fetch_one=True)
        jobs = query_db("SELECT * FROM JOB WHERE Company_ID=%s ORDER BY Job_ID DESC", (company_id,))
        job_skills = query_db("""SELECT js.Job_ID, sk.Skill_Name
            FROM JOB_SKILL js JOIN SKILL sk ON sk.Skill_ID=js.Skill_ID
            JOIN JOB j ON j.Job_ID=js.Job_ID
            WHERE j.Company_ID=%s ORDER BY sk.Skill_Name""", (company_id,))
        skills_by_job = {}
        for skill in job_skills:
            skills_by_job.setdefault(skill["Job_ID"], []).append(skill["Skill_Name"])
        return render_template("company_dashboard.html", company=company, stats=stats,
                               jobs=jobs, skills_by_job=skills_by_job)
    except RuntimeError:
        return render_database_error()


def parse_company_id():
    company_id = get_linked_account_id("Company_ID")
    if company_id is None:
        raise ValueError("Company account is not linked.")
    return company_id


def valid_company_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def valid_website(website):
    return not website or bool(re.fullmatch(r"https?://[^\s]+", website))


def valid_phone(phone):
    return not phone or bool(re.fullmatch(r"[0-9+().\-\s]{7,20}", phone))


@app.route("/company/profile/edit", methods=["GET", "POST"])
@role_required("COMPANY")
def edit_company_profile():
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        if request.method == "POST":
            form = request.form
            name = form.get("company_name", "").strip()
            industry = form.get("industry", "").strip()
            location = form.get("location", "").strip()
            website = form.get("website", "").strip()
            email = form.get("email", "").strip().lower()
            phone = form.get("phone", "").strip()
            if (not name or not industry or not location or
                    not valid_company_email(email) or
                    not valid_website(website) or not valid_phone(phone)):
                raise ValueError
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT User_ID FROM USER_ACCOUNT
                   WHERE Email=%s AND User_ID<>%s""",
                (email, session["user_id"]),
            )
            if cursor.fetchone() is not None:
                raise ValueError
            cursor.execute(
                """SELECT Company_ID FROM COMPANY
                   WHERE Email=%s AND Company_ID<>%s""",
                (email, company_id),
            )
            if cursor.fetchone() is not None:
                raise ValueError
            cursor.execute(
                """SELECT Company_ID FROM COMPANY
                   WHERE Company_Name=%s AND Company_ID<>%s""",
                (name, company_id),
            )
            if cursor.fetchone() is not None:
                raise ValueError
            cursor.execute(
                """UPDATE COMPANY SET Company_Name=%s, Industry=%s,
                   Location=%s, Website=%s, Email=%s, Phone=%s
                   WHERE Company_ID=%s""",
                (name, industry, location, website or None, email,
                 phone or None, company_id),
            )
            cursor.execute(
                """UPDATE USER_ACCOUNT SET Email=%s
                   WHERE User_ID=%s AND Role='COMPANY' AND Company_ID=%s""",
                (email, session["user_id"], company_id),
            )
            connection.commit()
            flash("Company profile updated successfully.", "success")
            return redirect(url_for("company_dashboard"))
        company = query_db(
            "SELECT * FROM COMPANY WHERE Company_ID=%s",
            (company_id,), fetch_one=True,
        )
        return render_template("company_profile_edit.html", company=company)
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid company details. Email and name must be unique.", "danger")
        if request.method == "POST":
            return redirect(url_for("edit_company_profile"))
        return render_database_error()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def load_company_job(company_id, job_id):
    job = query_db(
        """SELECT * FROM JOB
           WHERE Job_ID=%s AND Company_ID=%s""",
        (job_id, company_id), fetch_one=True,
    )
    if job is None:
        return None
    return job


def parse_job_form(form):
    job_title = form.get("job_title", "").strip()
    job_type = form.get("job_type", "").strip()
    description = form.get("description", "").strip()
    location = form.get("location", "").strip()
    minimum_cgpa = float(form.get("minimum_cgpa", ""))
    salary = float(form.get("salary", ""))
    deadline = parse_date_value(form.get("deadline", ""))
    status = form.get("status", "")
    if (not job_title or not job_type or not description or not location or
            not 0 <= minimum_cgpa <= 10 or salary < 0 or
            status not in {"Open", "Closed"}):
        raise ValueError
    selected_skills = list(dict.fromkeys(
        int(skill_id) for skill_id in form.getlist("skills")
    ))
    return (job_title, job_type, description, location, minimum_cgpa,
            deadline, salary, status, selected_skills)


def validate_skill_ids(cursor, skill_ids):
    if not skill_ids:
        return
    placeholders = ",".join(["%s"] * len(skill_ids))
    cursor.execute(
        f"SELECT Skill_ID FROM SKILL WHERE Skill_ID IN ({placeholders})",
        tuple(skill_ids),
    )
    found = {row["Skill_ID"] for row in cursor.fetchall()}
    if found != set(skill_ids):
        raise ValueError


@app.route("/company/jobs/edit/<int:job_id>", methods=["GET", "POST"])
@role_required("COMPANY")
def edit_company_job(job_id):
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        job = load_company_job(company_id, job_id)
        if job is None:
            return render_template("forbidden.html"), 403
        if request.method == "POST":
            values = parse_job_form(request.form)
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            validate_skill_ids(cursor, values[8])
            cursor.execute(
                """UPDATE JOB SET Job_Title=%s, Job_Type=%s, Description=%s,
                   Location=%s, Minimum_CGPA=%s, Application_Deadline=%s,
                   Salary=%s, Status=%s
                   WHERE Job_ID=%s AND Company_ID=%s""",
                (*values[:8], job_id, company_id),
            )
            cursor.execute("DELETE FROM JOB_SKILL WHERE Job_ID=%s", (job_id,))
            for skill_id in values[8]:
                cursor.execute(
                    "INSERT INTO JOB_SKILL (Job_ID, Skill_ID) VALUES (%s,%s)",
                    (job_id, skill_id),
                )
            connection.commit()
            flash("Opportunity updated successfully.", "success")
            return redirect(url_for("company_dashboard"))
        recruiters = query_db(
            """SELECT Recruiter_ID, Recruiter_Name FROM RECRUITER
               WHERE Company_ID=%s ORDER BY Recruiter_Name""",
            (company_id,),
        )
        skills = query_db("SELECT Skill_ID, Skill_Name FROM SKILL ORDER BY Skill_Name")
        selected_skills = query_db(
            "SELECT Skill_ID FROM JOB_SKILL WHERE Job_ID=%s", (job_id,)
        )
        return render_template(
            "job_form.html", job=job, recruiters=recruiters, skills=skills,
            selected_skill_ids={row["Skill_ID"] for row in selected_skills},
            edit_mode=True,
        )
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid opportunity details.", "danger")
        return redirect(url_for("edit_company_job", job_id=job_id))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.post("/company/jobs/close/<int:job_id>")
@role_required("COMPANY")
def close_company_job(job_id):
    try:
        company_id = parse_company_id()
        if load_company_job(company_id, job_id) is None:
            return render_template("forbidden.html"), 403
        execute_transaction([(
            """UPDATE JOB SET Status='Closed'
               WHERE Job_ID=%s AND Company_ID=%s""",
            (job_id, company_id),
        )])
        flash("Opportunity closed. Existing applications were preserved.", "success")
        return redirect(url_for("company_dashboard"))
    except ValueError:
        return render_template("forbidden.html"), 403
    except RuntimeError:
        return render_database_error()


@app.route("/company/jobs/new", methods=["GET", "POST"])
@role_required("COMPANY")
def create_job():
    company_id = get_linked_account_id("Company_ID")
    if company_id is None:
        return render_template("forbidden.html"), 403
    if request.method == "POST":
        form = request.form
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            recruiter_id = int(form["recruiter_id"])
            cursor.execute("SELECT Recruiter_ID FROM RECRUITER WHERE Recruiter_ID=%s AND Company_ID=%s",
                           (recruiter_id, company_id))
            if cursor.fetchone() is None:
                raise ValueError
            cursor.execute("""INSERT INTO JOB
                (Company_ID, Recruiter_ID, Job_Title, Job_Type, Description, Location,
                 Minimum_CGPA, Application_Deadline, Salary, Status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (company_id, recruiter_id, form["job_title"], form["job_type"],
                 form["description"], form["location"], float(form["minimum_cgpa"]),
                 form["deadline"], float(form["salary"]), form["status"]))
            job_id = cursor.lastrowid
            for skill_id in form.getlist("skills"):
                cursor.execute("INSERT INTO JOB_SKILL (Job_ID, Skill_ID) VALUES (%s,%s)",
                               (job_id, int(skill_id)))
            connection.commit()
            return redirect(url_for("company_dashboard"))
        except (KeyError, TypeError, ValueError, RuntimeError, Error):
            if connection is not None:
                connection.rollback()
            flash("Please provide valid opportunity details.", "danger")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
    recruiters = query_db("SELECT Recruiter_ID, Recruiter_Name FROM RECRUITER WHERE Company_ID=%s ORDER BY Recruiter_Name",
                          (company_id,))
    skills = query_db("SELECT Skill_ID, Skill_Name FROM SKILL ORDER BY Skill_Name")
    return render_template("job_form.html", recruiters=recruiters, skills=skills)


@app.route("/company/applicants")
@role_required("COMPANY")
def company_applicants():
    try:
        company_id = get_linked_account_id("Company_ID")
        if company_id is None:
            return render_template("forbidden.html"), 403
        applicants = query_db("""SELECT a.Application_ID, s.Name, s.Email, j.Job_Title,
            a.Application_Date, a.Status,
            (SELECT i.Interview_ID FROM INTERVIEW i
             WHERE i.Application_ID=a.Application_ID
             ORDER BY i.Interview_Date DESC, i.Interview_Time DESC, i.Interview_ID DESC
             LIMIT 1) AS Interview_ID,
            (SELECT i.Interview_Date FROM INTERVIEW i
             WHERE i.Application_ID=a.Application_ID
             ORDER BY i.Interview_Date DESC, i.Interview_Time DESC, i.Interview_ID DESC
             LIMIT 1) AS Interview_Date,
            (SELECT i.Interview_Time FROM INTERVIEW i
             WHERE i.Application_ID=a.Application_ID
             ORDER BY i.Interview_Date DESC, i.Interview_Time DESC, i.Interview_ID DESC
             LIMIT 1) AS Interview_Time,
            (SELECT i.Mode FROM INTERVIEW i
             WHERE i.Application_ID=a.Application_ID
             ORDER BY i.Interview_Date DESC, i.Interview_Time DESC, i.Interview_ID DESC
             LIMIT 1) AS Interview_Mode,
            (SELECT i.Interview_Status FROM INTERVIEW i
             WHERE i.Application_ID=a.Application_ID
             ORDER BY i.Interview_Date DESC, i.Interview_Time DESC, i.Interview_ID DESC
             LIMIT 1) AS Interview_Status
            ,(SELECT o.Offer_ID FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_ID
            ,(SELECT o.Offer_Date FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_Date
            ,(SELECT o.Job_Title FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_Job_Title
            ,(SELECT o.Salary FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_Salary
            ,(SELECT o.Joining_Date FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_Joining_Date
            ,(SELECT o.Offer_Status FROM OFFER o
              WHERE o.Application_ID=a.Application_ID
              LIMIT 1) AS Offer_Status
            FROM APPLICATION a
            JOIN STUDENT s ON s.Student_ID=a.Student_ID JOIN JOB j ON j.Job_ID=a.Job_ID
            WHERE j.Company_ID=%s ORDER BY a.Application_Date DESC""", (company_id,))
        return render_template("company_applicants.html", applicants=applicants)
    except RuntimeError:
        return render_database_error()


INTERVIEW_STATUSES = {"Scheduled", "Completed", "Cancelled"}
INTERVIEW_MODES = {"Online", "In-person"}
OFFER_STATUSES = {"Pending", "Accepted", "Withdrawn"}


def parse_interview_form(form):
    interview_date = datetime.strptime(form.get("interview_date", ""), "%Y-%m-%d").date()
    interview_time = datetime.strptime(form.get("interview_time", ""), "%H:%M").time()
    mode = form.get("mode", "")
    status = form.get("interview_status", "")
    remarks = form.get("remarks", "").strip()
    if mode not in INTERVIEW_MODES or status not in INTERVIEW_STATUSES:
        raise ValueError
    if len(remarks) > 500:
        raise ValueError
    return interview_date, interview_time, mode, status, remarks or None


def owned_application_for_company(company_id, application_id):
    return query_db(
        """SELECT a.Application_ID, j.Job_Title, s.Name AS Student_Name
           FROM APPLICATION a
           JOIN JOB j ON j.Job_ID=a.Job_ID
           JOIN STUDENT s ON s.Student_ID=a.Student_ID
           WHERE a.Application_ID=%s AND j.Company_ID=%s""",
        (application_id, company_id), fetch_one=True,
    )


def owned_interview_for_company(company_id, interview_id):
    return query_db(
        """SELECT i.Interview_ID, i.Application_ID, i.Interview_Date,
                  i.Interview_Time, i.Mode, i.Interview_Status, i.Remarks
           FROM INTERVIEW i
           JOIN APPLICATION a ON a.Application_ID=i.Application_ID
           JOIN JOB j ON j.Job_ID=a.Job_ID
           WHERE i.Interview_ID=%s AND j.Company_ID=%s""",
        (interview_id, company_id), fetch_one=True,
    )


def interview_form_data(interview=None):
    return {
        "interview": interview,
        "interview_statuses": sorted(INTERVIEW_STATUSES),
        "interview_modes": sorted(INTERVIEW_MODES),
    }


@app.route("/company/applications/<int:application_id>/interview", methods=["GET", "POST"])
@role_required("COMPANY")
def schedule_interview(application_id):
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        application = owned_application_for_company(company_id, application_id)
        if application is None:
            return render_template("forbidden.html"), 403
        if request.method == "POST":
            interview_date, interview_time, mode, status, remarks = parse_interview_form(
                request.form
            )
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO INTERVIEW
                   (Application_ID, Interview_Date, Interview_Time, Mode,
                    Interview_Status, Remarks)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (application_id, interview_date, interview_time, mode, status, remarks),
            )
            connection.commit()
            flash("Interview scheduled successfully.", "success")
            return redirect(url_for("application_detail", application_id=application_id))
        return render_template(
            "interview_form.html",
            application=application,
            **interview_form_data(),
        )
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid interview details.", "danger")
        return redirect(url_for("schedule_interview", application_id=application_id))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/company/interviews/edit/<int:interview_id>", methods=["GET", "POST"])
@role_required("COMPANY")
def edit_interview(interview_id):
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        interview = owned_interview_for_company(company_id, interview_id)
        if interview is None:
            return render_template("forbidden.html"), 403
        application = owned_application_for_company(company_id, interview["Application_ID"])
        if request.method == "POST":
            values = parse_interview_form(request.form)
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE INTERVIEW SET Interview_Date=%s, Interview_Time=%s,
                   Mode=%s, Interview_Status=%s, Remarks=%s
                   WHERE Interview_ID=%s""",
                (*values, interview_id),
            )
            connection.commit()
            flash("Interview updated successfully.", "success")
            return redirect(url_for("application_detail",
                                    application_id=interview["Application_ID"]))
        return render_template(
            "interview_form.html",
            application=application,
            **interview_form_data(interview),
        )
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid interview details.", "danger")
        return redirect(url_for("edit_interview", interview_id=interview_id))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.post("/company/interviews/cancel/<int:interview_id>")
@role_required("COMPANY")
def cancel_interview(interview_id):
    try:
        company_id = parse_company_id()
        interview = owned_interview_for_company(company_id, interview_id)
        if interview is None:
            return render_template("forbidden.html"), 403
        execute_transaction([(
            """UPDATE INTERVIEW SET Interview_Status='Cancelled'
               WHERE Interview_ID=%s""",
            (interview_id,),
        )])
        flash("Interview cancelled and preserved in history.", "success")
        return redirect(url_for("application_detail",
                                application_id=interview["Application_ID"]))
    except RuntimeError:
        return render_database_error()


def parse_offer_form(form):
    offer_date = datetime.strptime(form.get("offer_date", ""), "%Y-%m-%d").date()
    joining_date = datetime.strptime(form.get("joining_date", ""), "%Y-%m-%d").date()
    job_title = form.get("job_title", "").strip()
    salary = float(form.get("salary", ""))
    status = form.get("offer_status", "")
    if not job_title or len(job_title) > 150 or salary < 0 or status not in OFFER_STATUSES:
        raise ValueError
    if joining_date < offer_date:
        raise ValueError
    return offer_date, job_title, salary, joining_date, status


def owned_offer_for_company(company_id, offer_id):
    return query_db(
        """SELECT o.Offer_ID, o.Application_ID, o.Offer_Date, o.Job_Title,
                  o.Salary, o.Joining_Date, o.Offer_Status
           FROM OFFER o
           JOIN APPLICATION a ON a.Application_ID=o.Application_ID
           JOIN JOB j ON j.Job_ID=a.Job_ID
           WHERE o.Offer_ID=%s AND j.Company_ID=%s""",
        (offer_id, company_id), fetch_one=True,
    )


def offer_form_data(offer=None):
    return {
        "offer": offer,
        "offer_statuses": sorted(OFFER_STATUSES),
    }


@app.route("/company/applications/<int:application_id>/offer", methods=["GET", "POST"])
@role_required("COMPANY")
def create_offer(application_id):
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        application = owned_application_for_company(company_id, application_id)
        if application is None:
            return render_template("forbidden.html"), 403
        application = query_db(
            """SELECT a.Application_ID, a.Status, j.Job_Title,
                      s.Name AS Student_Name
               FROM APPLICATION a
               JOIN JOB j ON j.Job_ID=a.Job_ID
               JOIN STUDENT s ON s.Student_ID=a.Student_ID
               WHERE a.Application_ID=%s AND j.Company_ID=%s""",
            (application_id, company_id), fetch_one=True,
        )
        if application is None:
            return render_template("forbidden.html"), 403
        if application["Status"] != "Selected":
            flash("Offers can only be issued for selected applications.", "danger")
            return redirect(url_for("company_applicants"))
        existing_offer = query_db(
            "SELECT Offer_ID FROM OFFER WHERE Application_ID=%s",
            (application_id,), fetch_one=True,
        )
        if existing_offer is not None:
            flash("An offer already exists. Edit the existing offer instead.", "warning")
            return redirect(url_for("edit_offer", offer_id=existing_offer["Offer_ID"]))
        if request.method == "POST":
            values = parse_offer_form(request.form)
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT Offer_ID FROM OFFER WHERE Application_ID=%s FOR UPDATE",
                (application_id,),
            )
            if cursor.fetchone() is not None:
                raise ValueError
            cursor.execute(
                """INSERT INTO OFFER
                   (Application_ID, Offer_Date, Job_Title, Salary,
                    Joining_Date, Offer_Status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (application_id, *values),
            )
            connection.commit()
            flash("Offer issued successfully.", "success")
            return redirect(url_for("application_detail", application_id=application_id))
        return render_template(
            "offer_form.html",
            application=application,
            **offer_form_data(),
        )
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid offer details.", "danger")
        return redirect(url_for("create_offer", application_id=application_id))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/company/offers/edit/<int:offer_id>", methods=["GET", "POST"])
@role_required("COMPANY")
def edit_offer(offer_id):
    connection = None
    cursor = None
    try:
        company_id = parse_company_id()
        offer = owned_offer_for_company(company_id, offer_id)
        if offer is None:
            return render_template("forbidden.html"), 403
        application = owned_application_for_company(company_id, offer["Application_ID"])
        if request.method == "POST":
            values = parse_offer_form(request.form)
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE OFFER SET Offer_Date=%s, Job_Title=%s, Salary=%s,
                   Joining_Date=%s, Offer_Status=%s
                   WHERE Offer_ID=%s""",
                (*values, offer_id),
            )
            connection.commit()
            flash("Offer updated successfully.", "success")
            return redirect(url_for("application_detail",
                                    application_id=offer["Application_ID"]))
        return render_template(
            "offer_form.html",
            application=application,
            **offer_form_data(offer),
        )
    except (KeyError, TypeError, ValueError, RuntimeError, Error):
        if connection is not None:
            connection.rollback()
        flash("Please provide valid offer details.", "danger")
        return redirect(url_for("edit_offer", offer_id=offer_id))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.post("/company/offers/withdraw/<int:offer_id>")
@role_required("COMPANY")
def withdraw_offer(offer_id):
    try:
        company_id = parse_company_id()
        offer = owned_offer_for_company(company_id, offer_id)
        if offer is None:
            return render_template("forbidden.html"), 403
        execute_transaction([(
            """UPDATE OFFER SET Offer_Status='Withdrawn'
               WHERE Offer_ID=%s""",
            (offer_id,),
        )])
        flash("Offer withdrawn and preserved in history.", "success")
        return redirect(url_for("application_detail",
                                application_id=offer["Application_ID"]))
    except RuntimeError:
        return render_database_error()


@app.post("/company/applications/<int:application_id>/status")
@role_required("COMPANY")
def update_application_status(application_id):
    status = request.form.get("status", "")
    if status not in {"Applied", "Shortlisted", "Selected", "Rejected"}:
        return render_template("forbidden.html"), 400
    try:
        company_id = get_linked_account_id("Company_ID")
        if company_id is None:
            return render_template("forbidden.html"), 403
        execute_transaction([("""UPDATE APPLICATION a JOIN JOB j ON j.Job_ID=a.Job_ID
            SET a.Status=%s WHERE a.Application_ID=%s AND j.Company_ID=%s""",
                              (status, application_id, company_id))])
        return redirect(url_for("company_applicants"))
    except RuntimeError:
        return render_database_error()


def query_db(query, params=None, fetch_one=False):
    """Run a read-only query and return dictionary-shaped rows."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone() if fetch_one else cursor.fetchall()
    except (RuntimeError, Error) as error:
        app.logger.error("Database read failed: %s", error)
        raise RuntimeError("The database could not be read.") from error
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def render_database_error():
    return render_template("error.html"), 500


def get_eligibility_data(student_id, job_id):
    """Read the student, job, skills, and duplicate state for eligibility."""
    student = query_db(
        """
        SELECT Student_ID, Name, CGPA
        FROM STUDENT
        WHERE Student_ID = %s
        """,
        (student_id,),
        fetch_one=True,
    )
    job = query_db(
        """
        SELECT j.Job_ID, j.Job_Title, j.Minimum_CGPA, j.Application_Deadline,
               j.Status, c.Company_Name
        FROM JOB AS j
        INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
        WHERE j.Job_ID = %s
        """,
        (job_id,),
        fetch_one=True,
    )
    if student is None or job is None:
        return None

    required_skills = query_db(
        """
        SELECT sk.Skill_ID, sk.Skill_Name
        FROM JOB_SKILL AS js
        INNER JOIN SKILL AS sk ON js.Skill_ID = sk.Skill_ID
        WHERE js.Job_ID = %s
        ORDER BY sk.Skill_Name
        """,
        (job_id,),
    )
    student_skills = query_db(
        """
        SELECT sk.Skill_ID, sk.Skill_Name
        FROM STUDENT_SKILL AS ss
        INNER JOIN SKILL AS sk ON ss.Skill_ID = sk.Skill_ID
        WHERE ss.Student_ID = %s
        ORDER BY sk.Skill_Name
        """,
        (student_id,),
    )
    duplicate = query_db(
        """
        SELECT Application_ID
        FROM APPLICATION
        WHERE Student_ID = %s AND Job_ID = %s
        """,
        (student_id, job_id),
        fetch_one=True,
    )
    student_skill_ids = {skill["Skill_ID"] for skill in student_skills}
    missing_skills = [
        skill["Skill_Name"]
        for skill in required_skills
        if skill["Skill_ID"] not in student_skill_ids
    ]
    deadline_passed = date.today() > job["Application_Deadline"]
    reasons = []
    if student["CGPA"] < job["Minimum_CGPA"]:
        reasons.append("CGPA requirement not met.")
    if missing_skills:
        reasons.append("Missing required skills: " + ", ".join(missing_skills))
    if job["Status"] != "Open":
        reasons.append("Opportunity is no longer accepting applications.")
    if deadline_passed:
        if job["Status"] == "Open":
            reasons.append("Opportunity is no longer accepting applications.")
    eligible_by_requirements = not reasons
    already_applied = duplicate is not None
    return {
        "student": student,
        "job": job,
        "required_skills": required_skills,
        "student_skills": student_skills,
        "missing_skills": missing_skills,
        "duplicate": duplicate,
        "deadline_passed": deadline_passed,
        "reasons": reasons,
        "eligible_by_requirements": eligible_by_requirements,
        "already_applied": already_applied,
        "can_apply": eligible_by_requirements and not already_applied,
        "eligible": eligible_by_requirements,
    }


def get_eligibility_options():
    students = query_db(
        """
        SELECT Student_ID, Name
        FROM STUDENT
        ORDER BY Name
        """
    )
    jobs = query_db(
        """
        SELECT j.Job_ID, j.Job_Title, c.Company_Name
        FROM JOB AS j
        INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
        ORDER BY j.Job_Title
        """
    )
    return students, jobs


@app.route("/")
def home():
    try:
        stats = {
            "students": query_db("SELECT COUNT(*) AS total FROM STUDENT", fetch_one=True)["total"],
            "companies": query_db("SELECT COUNT(*) AS total FROM COMPANY", fetch_one=True)["total"],
            "open_jobs": query_db(
                "SELECT COUNT(*) AS total FROM JOB WHERE Status = 'Open'",
                fetch_one=True,
            )["total"],
            "applications": query_db(
                "SELECT COUNT(*) AS total FROM APPLICATION",
                fetch_one=True,
            )["total"],
            "interviews": query_db(
                "SELECT COUNT(*) AS total FROM INTERVIEW",
                fetch_one=True,
            )["total"],
            "offers": query_db("SELECT COUNT(*) AS total FROM OFFER", fetch_one=True)["total"],
        }
        jobs = query_db(
            """
            SELECT j.Job_ID, j.Job_Title, j.Job_Type, j.Location,
                   j.Minimum_CGPA, j.Application_Deadline, j.Status,
                   c.Company_Name
            FROM JOB AS j
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            ORDER BY j.Job_ID DESC
            LIMIT 5
            """
        )
        applications = query_db(
            """
            SELECT a.Application_ID, s.Name AS Student_Name, j.Job_Title,
                   a.Application_Date, a.Status
            FROM APPLICATION AS a
            INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
            INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
            ORDER BY a.Application_Date DESC
            LIMIT 5
            """
        )
        return render_template("index.html", stats=stats, jobs=jobs, applications=applications)
    except RuntimeError:
        return render_database_error()


@app.route("/eligibility", methods=["GET", "POST"])
@role_required("ADMIN", "STUDENT")
def eligibility():
    result = None
    selected_student_id = request.args.get("student_id", "")
    selected_job_id = request.args.get("job_id", "")
    try:
        linked_student_id = None
        if session.get("role") == "STUDENT":
            linked_student_id = get_linked_account_id("Student_ID")
            if linked_student_id is None:
                return render_template("forbidden.html"), 403
            selected_student_id = str(linked_student_id)
        students, jobs = get_eligibility_options()
        if linked_student_id is not None:
            students = [student for student in students if student["Student_ID"] == linked_student_id]
        if request.method == "POST":
            selected_student_id = request.form.get("student_id", "")
            selected_job_id = request.form.get("job_id", "")
            try:
                student_id = int(selected_student_id)
                job_id = int(selected_job_id)
            except (TypeError, ValueError):
                result = {"reasons": ["Please select both a student and an opportunity."]}
            else:
                if session.get("role") == "STUDENT":
                    if student_id != linked_student_id:
                        return render_template("forbidden.html"), 403
                result = get_eligibility_data(student_id, job_id)
                if result is None:
                    result = {"reasons": ["The selected student or opportunity was not found."]}
        return render_template(
            "eligibility.html",
            students=students,
            jobs=jobs,
            result=result,
            selected_student_id=selected_student_id,
            selected_job_id=selected_job_id,
        )
    except RuntimeError:
        return render_database_error()


@app.post("/apply/<int:student_id>/<int:job_id>")
@role_required("STUDENT", "ADMIN")
def apply_for_job(student_id, job_id):
    if session.get("role") == "STUDENT" and student_id != get_linked_account_id("Student_ID"):
        return render_template("forbidden.html"), 403
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        eligibility_data = evaluate_eligibility_for_cursor(cursor, student_id, job_id)
        if eligibility_data is None:
            return render_template("not_found.html", item="Student or opportunity"), 404
        if not eligibility_data["can_apply"]:
            return render_template(
                "eligibility.html",
                students=[],
                jobs=[],
                result=eligibility_data,
                selected_student_id=str(student_id),
                selected_job_id=str(job_id),
            ), 400
        cursor.execute(
            """
            INSERT INTO APPLICATION (Student_ID, Job_ID, Application_Date, Status)
            VALUES (%s, %s, %s, 'Applied')
            """,
            (student_id, job_id, date.today()),
        )
        connection.commit()
        application_id = cursor.lastrowid
        return render_template(
            "application_success.html",
            result=eligibility_data,
            application_id=application_id,
            application_date=date.today(),
        )
    except (RuntimeError, Error) as error:
        if connection is not None:
            connection.rollback()
        app.logger.error("Application submission failed: %s", error)
        return render_template("error.html"), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def evaluate_eligibility_for_cursor(cursor, student_id, job_id):
    """Recheck every business rule using one transaction connection."""
    cursor.execute(
        """
        SELECT Student_ID, Name, CGPA
        FROM STUDENT
        WHERE Student_ID = %s
        """,
        (student_id,),
    )
    student = cursor.fetchone()
    cursor.execute(
        """
        SELECT j.Job_ID, j.Job_Title, j.Minimum_CGPA, j.Application_Deadline,
               j.Status, c.Company_Name
        FROM JOB AS j
        INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
        WHERE j.Job_ID = %s
        """,
        (job_id,),
    )
    job = cursor.fetchone()
    if student is None or job is None:
        return None
    cursor.execute(
        """
        SELECT sk.Skill_ID, sk.Skill_Name
        FROM JOB_SKILL AS js
        INNER JOIN SKILL AS sk ON js.Skill_ID = sk.Skill_ID
        WHERE js.Job_ID = %s
        """,
        (job_id,),
    )
    required_skills = cursor.fetchall()
    cursor.execute(
        """
        SELECT sk.Skill_ID, sk.Skill_Name
        FROM STUDENT_SKILL AS ss
        INNER JOIN SKILL AS sk ON ss.Skill_ID = sk.Skill_ID
        WHERE ss.Student_ID = %s
        """,
        (student_id,),
    )
    student_skills = cursor.fetchall()
    cursor.execute(
        """
        SELECT Application_ID
        FROM APPLICATION
        WHERE Student_ID = %s AND Job_ID = %s
        """,
        (student_id, job_id),
    )
    duplicate = cursor.fetchone()
    student_skill_ids = {skill["Skill_ID"] for skill in student_skills}
    missing_skills = [
        skill["Skill_Name"]
        for skill in required_skills
        if skill["Skill_ID"] not in student_skill_ids
    ]
    reasons = []
    if student["CGPA"] < job["Minimum_CGPA"]:
        reasons.append("CGPA requirement not met.")
    if missing_skills:
        reasons.append("Missing required skills: " + ", ".join(missing_skills))
    if job["Status"] != "Open":
        reasons.append("Opportunity is no longer accepting applications.")
    if date.today() > job["Application_Deadline"]:
        if job["Status"] == "Open":
            reasons.append("Opportunity is no longer accepting applications.")
    eligible_by_requirements = not reasons
    already_applied = duplicate is not None
    return {
        "student": student,
        "job": job,
        "required_skills": required_skills,
        "student_skills": student_skills,
        "missing_skills": missing_skills,
        "duplicate": duplicate,
        "deadline_passed": date.today() > job["Application_Deadline"],
        "reasons": reasons,
        "eligible_by_requirements": eligible_by_requirements,
        "already_applied": already_applied,
        "can_apply": eligible_by_requirements and not already_applied,
        "eligible": eligible_by_requirements,
    }


@app.route("/students")
@role_required("ADMIN")
def students():
    try:
        records = query_db(
            """
            SELECT s.Student_ID, s.Name, s.Email, s.CGPA, s.Graduation_Year,
                   d.Department_Name
            FROM STUDENT AS s
            INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID
            ORDER BY s.Name
            """
        )
        return render_template("students.html", students=records)
    except RuntimeError:
        return render_database_error()


@app.route("/student/<int:student_id>")
@role_required("ADMIN", "STUDENT")
def student_detail(student_id):
    try:
        if session.get("role") == "STUDENT":
            linked_student_id = get_linked_account_id("Student_ID")
            if student_id != linked_student_id:
                return render_template("forbidden.html"), 403
        student = query_db(
            """
            SELECT s.*, d.Department_Name
            FROM STUDENT AS s
            INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID
            WHERE s.Student_ID = %s
            """,
            (student_id,),
            fetch_one=True,
        )
        if student is None:
            return render_template("not_found.html", item="Student"), 404
        skills = query_db(
            """
            SELECT sk.Skill_Name, ss.Proficiency
            FROM STUDENT_SKILL AS ss
            INNER JOIN SKILL AS sk ON ss.Skill_ID = sk.Skill_ID
            WHERE ss.Student_ID = %s
            ORDER BY sk.Skill_Name
            """,
            (student_id,),
        )
        certifications = query_db(
            """
            SELECT Certification_Name, Issuing_Organization, Issue_Date, Expiry_Date
            FROM CERTIFICATION
            WHERE Student_ID = %s
            ORDER BY Issue_Date DESC
            """,
            (student_id,),
        )
        applications = query_db(
            """
            SELECT a.Application_ID, j.Job_Title, c.Company_Name,
                   a.Application_Date, a.Status
            FROM APPLICATION AS a
            INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            WHERE a.Student_ID = %s
            ORDER BY a.Application_Date DESC
            """,
            (student_id,),
        )
        return render_template(
            "student_detail.html",
            student=student,
            skills=skills,
            certifications=certifications,
            applications=applications,
        )
    except RuntimeError:
        return render_database_error()


@app.route("/jobs")
@role_required("ADMIN", "STUDENT", "COMPANY")
def jobs():
    try:
        job_filter = ""
        job_params = ()
        if session.get("role") == "COMPANY":
            company_id = get_linked_account_id("Company_ID")
            if company_id is None:
                return render_template("forbidden.html"), 403
            job_filter = " WHERE j.Company_ID = %s"
            job_params = (company_id,)
        records = query_db(
            """
            SELECT j.Job_ID, j.Job_Title, j.Job_Type, j.Location,
                   j.Minimum_CGPA, j.Application_Deadline, j.Salary, j.Status,
                   c.Company_Name
            FROM JOB AS j
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            """ + job_filter + """
            ORDER BY j.Status, j.Application_Deadline
            """,
            job_params,
        )
        skills = query_db(
            """
            SELECT js.Job_ID, sk.Skill_Name
            FROM JOB_SKILL AS js
            INNER JOIN SKILL AS sk ON js.Skill_ID = sk.Skill_ID
            ORDER BY js.Job_ID, sk.Skill_Name
            """
        )
        skills_by_job = {}
        for skill in skills:
            skills_by_job.setdefault(skill["Job_ID"], []).append(skill["Skill_Name"])
        for job in records:
            job["Required_Skills"] = skills_by_job.get(job["Job_ID"], [])
        return render_template("jobs.html", jobs=records)
    except RuntimeError:
        return render_database_error()


@app.route("/job/<int:job_id>")
@role_required("ADMIN", "STUDENT", "COMPANY")
def job_detail(job_id):
    try:
        job = query_db(
            """
            SELECT j.*, c.Company_Name, c.Industry AS Company_Industry,
                   c.Location AS Company_Location, c.Website AS Company_Website,
                   c.Email AS Company_Email, r.Recruiter_Name
            FROM JOB AS j
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            INNER JOIN RECRUITER AS r ON j.Recruiter_ID = r.Recruiter_ID
            WHERE j.Job_ID = %s
            """,
            (job_id,),
            fetch_one=True,
        )
        if job is None:
            return render_template("not_found.html", item="Opportunity"), 404
        if session.get("role") == "COMPANY":
            company_id = get_linked_account_id("Company_ID")
            if company_id is None or job["Company_ID"] != company_id:
                return render_template("forbidden.html"), 403
        skills = query_db(
            """
            SELECT sk.Skill_Name
            FROM JOB_SKILL AS js
            INNER JOIN SKILL AS sk ON js.Skill_ID = sk.Skill_ID
            WHERE js.Job_ID = %s
            ORDER BY sk.Skill_Name
            """,
            (job_id,),
        )
        return render_template("job_detail.html", job=job, skills=skills)
    except RuntimeError:
        return render_database_error()


@app.route("/companies")
@role_required("ADMIN", "STUDENT")
def companies():
    try:
        records = query_db(
            """
            SELECT c.Company_ID, c.Company_Name, c.Industry, c.Location,
                   c.Website, c.Email,
                   COUNT(DISTINCT r.Recruiter_ID) AS Recruiter_Count,
                   COUNT(DISTINCT j.Job_ID) AS Opportunity_Count
            FROM COMPANY AS c
            LEFT JOIN RECRUITER AS r ON c.Company_ID = r.Company_ID
            LEFT JOIN JOB AS j ON c.Company_ID = j.Company_ID
            GROUP BY c.Company_ID, c.Company_Name, c.Industry, c.Location,
                     c.Website, c.Email
            ORDER BY c.Company_Name
            """
        )
        return render_template("companies.html", companies=records)
    except RuntimeError:
        return render_database_error()


@app.route("/applications")
@role_required("ADMIN", "STUDENT", "COMPANY")
def applications():
    try:
        filter_clause = ""
        filter_params = ()
        if session.get("role") == "STUDENT":
            student_id = get_linked_account_id("Student_ID")
            filter_clause = " WHERE a.Student_ID = %s"
            filter_params = (student_id,)
        elif session.get("role") == "COMPANY":
            company_id = get_linked_account_id("Company_ID")
            filter_clause = " WHERE j.Company_ID = %s"
            filter_params = (company_id,)
        records = query_db(
            """
            SELECT a.Application_ID, s.Name AS Student_Name, j.Job_Title,
                   c.Company_Name, a.Application_Date, a.Status
            FROM APPLICATION AS a
            INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
            INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            """ + filter_clause + " ORDER BY a.Application_Date DESC",
            filter_params,
        )
        summary_rows = query_db(
            """
            SELECT Status, COUNT(*) AS Total
            FROM APPLICATION AS a
            INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
            """ + filter_clause + """
            GROUP BY Status
            """,
            filter_params,
        )
        total = query_db(
            "SELECT COUNT(*) AS Total FROM APPLICATION AS a INNER JOIN JOB AS j ON a.Job_ID=j.Job_ID" + filter_clause,
            filter_params,
            fetch_one=True,
        )["Total"]
        summary = {row["Status"]: row["Total"] for row in summary_rows}
        return render_template(
            "applications.html",
            applications=records,
            summary=summary,
            total=total,
        )
    except RuntimeError:
        return render_database_error()


@app.route("/application/<int:application_id>")
@role_required("ADMIN", "STUDENT", "COMPANY")
def application_detail(application_id):
    try:
        application = query_db(
            """
            SELECT a.Application_ID, a.Application_Date, a.Status,
                   a.Student_ID, j.Company_ID, s.Name AS Student_Name, s.Email AS Student_Email,
                   s.CGPA, d.Department_Name,
                   j.Job_Title, j.Job_Type, j.Location,
                   c.Company_Name, r.Recruiter_Name
            FROM APPLICATION AS a
            INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
            INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID
            INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
            INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
            INNER JOIN RECRUITER AS r ON j.Recruiter_ID = r.Recruiter_ID
            WHERE a.Application_ID = %s
            """,
            (application_id,),
            fetch_one=True,
        )
        if application is None:
            return render_template("not_found.html", item="Application"), 404
        if session.get("role") == "STUDENT" and application["Student_ID"] != get_linked_account_id("Student_ID"):
            return render_template("forbidden.html"), 403
        if session.get("role") == "COMPANY" and application["Company_ID"] != get_linked_account_id("Company_ID"):
            return render_template("forbidden.html"), 403

        interviews = query_db(
            """
            SELECT Interview_ID, Interview_Date, Interview_Time, Mode,
                   Interview_Status, Remarks
            FROM INTERVIEW
            WHERE Application_ID = %s
            ORDER BY Interview_Date, Interview_Time
            """,
            (application_id,),
        )
        offer = query_db(
            """
            SELECT Offer_ID, Offer_Date, Job_Title, Salary, Joining_Date, Offer_Status
            FROM OFFER
            WHERE Application_ID = %s
            """,
            (application_id,),
            fetch_one=True,
        )
        return render_template(
            "application_detail.html",
            application=application,
            interviews=interviews,
            offer=offer,
        )
    except RuntimeError:
        return render_database_error()


if __name__ == "__main__":
    app.run(debug=True)
