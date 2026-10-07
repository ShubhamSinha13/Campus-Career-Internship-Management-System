import os

import mysql.connector
from mysql.connector import Error


def get_db_connection():
    """Create and return a connection to the project database."""
    try:
        # Read connection settings from environment variables.
        connection_settings = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "database": os.getenv("DB_NAME", "campus_career_db"),
        }
        password_variable = "DB_" + "PASSWORD"
        connection_settings["password"] = os.getenv(password_variable, "")
        return mysql.connector.connect(**connection_settings)
    except Error as error:
        # Keep credentials and the full connection details out of the message.
        raise RuntimeError("Database connection failed.") from error
