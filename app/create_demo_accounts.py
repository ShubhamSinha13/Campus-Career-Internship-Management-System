"""Create authentication accounts using passwords supplied in the environment.

Set DEMO_ADMIN_PASSWORD, DEMO_STUDENT_PASSWORD, and DEMO_COMPANY_PASSWORD
before running this script. Passwords are never printed or stored in source.
"""

import os

from db import get_db_connection
from mysql.connector import Error
from werkzeug.security import generate_password_hash


def validate_account_relationship(role, student_id=None, company_id=None):
    valid = (
        (role == "ADMIN" and student_id is None and company_id is None)
        or (role == "STUDENT" and student_id is not None and company_id is None)
        or (role == "COMPANY" and student_id is None and company_id is not None)
    )
    if not valid:
        raise ValueError("Invalid authentication account relationship.")


def build_demo_accounts():
    passwords = {
        "admin@campuscareer.local": os.environ["DEMO_ADMIN_PASSWORD"],
        "student@campuscareer.local": os.environ["DEMO_STUDENT_PASSWORD"],
        "company@campuscareer.local": os.environ["DEMO_COMPANY_PASSWORD"],
    }
    accounts = [
        ("admin@campuscareer.local", generate_password_hash(passwords["admin@campuscareer.local"]), "ADMIN", None, None),
        ("student@campuscareer.local", generate_password_hash(passwords["student@campuscareer.local"]), "STUDENT", 1, None),
        ("company@campuscareer.local", generate_password_hash(passwords["company@campuscareer.local"]), "COMPANY", None, 1),
    ]
    for _, _, role, student_id, company_id in accounts:
        validate_account_relationship(role, student_id, company_id)
    return accounts


def create_demo_accounts():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        for account in build_demo_accounts():
            cursor.execute(
                """INSERT INTO USER_ACCOUNT
                   (Email, Password_Hash, Role, Student_ID, Company_ID)
                   VALUES (%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE Password_Hash=VALUES(Password_Hash)""",
                account,
            )
        connection.commit()
    except Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_demo_accounts()
    print("Demo authentication accounts created or refreshed.")
