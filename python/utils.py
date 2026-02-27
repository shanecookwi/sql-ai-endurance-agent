import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

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