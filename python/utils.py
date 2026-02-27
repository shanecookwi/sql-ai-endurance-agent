import os
import pyodbc
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# ENV VARS
# ---------------------------------------------------------
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")


# ---------------------------------------------------------
# DB CONNECTION
# ---------------------------------------------------------
def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USER};"
        f"PWD={SQL_PASSWORD};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

# Birthdate
birthdate_str = os.getenv("ATHLETE_BIRTHDATE")
if not birthdate_str:
    raise RuntimeError("ATHLETE_BIRTHDATE is not set in .env")

birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()

def age_at_workout(workout_date: date) -> int:
    return workout_date.year - birthdate.year - (
        (workout_date.month, workout_date.day) < (birthdate.month, birthdate.day)
    )

# Gender
athlete_gender = os.getenv("ATHLETE_GENDER")
if not athlete_gender:
    raise RuntimeError("ATHLETE_GENDER is not set in .env")