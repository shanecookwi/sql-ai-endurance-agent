import os
import json
import pyodbc
from anthropic import Anthropic
from dotenv import load_dotenv
from utils import age_at_workout, athlete_gender

load_dotenv()

# ---------------------------------------------------------
# ENV VARS
# ---------------------------------------------------------
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_AI_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_AI_MODEL")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

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

# ---------------------------------------------------------
# AI CALL (Anthropic)
# ---------------------------------------------------------
def call_ai_for_workout(row):
    data = {
        "swim_workout_id": row.swim_workout_id,
        "activity_type": row.activity_type,
        "workout_date": str(row.workout_date),
        "title": row.title,
        "distance_yards": row.distance_yards,
        "calories": row.calories,
        "time": row.time,
        "avg_hr": row.avg_hr,
        "max_hr": row.max_hr,
        "aerobic_te": row.aerobic_te,
        "avg_pace": row.avg_pace,
        "best_pace": row.best_pace,
        "total_strokes": row.total_strokes,
        "avg_swolf": row.avg_swolf,
        "avg_stroke_rate": row.avg_stroke_rate,
        "best_lap_time": row.best_lap_time,
        "number_of_laps": row.number_of_laps,
        "moving_time": row.moving_time,
        "elapsed_time": row.elapsed_time,
        "training_stress_score": row.training_stress_score,
    }

    age = age_at_workout(row.workout_date)

    prompt = f"""
You are an expert endurance swim coach. Analyze the following swim workout and return STRICT JSON.

Workout details:
{json.dumps(data, indent=2)}

The athlete was {age} years old at the time of this workout.
The athlete is {athlete_gender}. Use gender only to interpret heart‑rate‑based physiology, not as a determinant of performance.
Use age only to interpret heart‑rate‑based metrics, not as the primary determinant of difficulty.

Generate:
1. "summary": 2–3 sentences describing how the swim likely felt, focusing on pacing, efficiency, aerobic load, and technique.
2. "felt_rating": one of ["easy", "moderate", "hard"].
3. "perceived_effort": one of ["low", "medium", "high"].

Return ONLY valid JSON in this exact shape, with NO code fences:
{{
  "summary": "string",
  "felt_rating": "easy|moderate|hard",
  "perceived_effort": "low|medium|high"
}}
"""

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    content = response.content[0].text

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(f"Model did not return valid JSON: {content}")

    return (
        parsed.get("summary"),
        parsed.get("felt_rating"),
        parsed.get("perceived_effort")
    )

# ---------------------------------------------------------
# FETCH WORKOUTS NEEDING AI FIELDS
# ---------------------------------------------------------
def fetch_pending(conn, batch_size=25):
    query = """
    SELECT TOP (?) *
    FROM swim_workouts
    WHERE notes IS NULL
       OR felt_rating IS NULL
       OR perceived_effort IS NULL
    ORDER BY swim_workout_id;
    """
    cur = conn.cursor()
    cur.execute(query, batch_size)
    rows = cur.fetchall()
    cur.close()
    return rows

# ---------------------------------------------------------
# UPDATE WORKOUT
# ---------------------------------------------------------
def update_workout(conn, workout_id, summary, felt_rating, perceived_effort):
    query = """
    UPDATE swim_workouts
    SET
        notes = ?,
        felt_rating = ?,
        perceived_effort = ?
    WHERE swim_workout_id = ?;
    """
    cur = conn.cursor()
    cur.execute(query, (summary, felt_rating, perceived_effort, workout_id))
    conn.commit()
    cur.close()

# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------
def main():
    conn = get_connection()

    try:
        while True:
            rows = fetch_pending(conn)

            if not rows:
                print("All swim workouts have AI fields.")
                break

            for row in rows:
                wid = row.swim_workout_id
                print(f"Processing swim_workout_id={wid}...")

                try:
                    summary, felt_rating, perceived_effort = call_ai_for_workout(row)

                    print(f"  summary={summary}")
                    print(f"  felt_rating={felt_rating}, perceived_effort={perceived_effort}")

                    update_workout(conn, wid, summary, felt_rating, perceived_effort)

                except Exception as e:
                    print(f"  ERROR on swim_workout_id={wid}: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()