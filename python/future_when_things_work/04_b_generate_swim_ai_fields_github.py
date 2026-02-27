import os
import json
import pyodbc
import requests
from dotenv import load_dotenv

load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")   # or your chosen model
AI_API_BASE = "https://api.github.com"             # CORRECT BASE URL


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
# AI CALL (GitHub Models — correct endpoint + format)
# ---------------------------------------------------------
def call_ai_for_workout(row):
    """
    row is a pyodbc.Row from swim_workouts.
    """

    # Extract fields safely
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

    # Build prompt
    prompt = f"""
You are an expert endurance swim coach. Analyze the following swim workout and return STRICT JSON.

Workout details:
{json.dumps(data, indent=2)}

Generate:
1. "summary": 2–3 sentences describing how the swim likely felt, focusing on pacing, efficiency, aerobic load, and technique.
2. "felt_rating": one of ["easy", "moderate", "hard"].
3. "perceived_effort": one of ["low", "medium", "high"].

Return ONLY valid JSON in this exact shape:
{{
  "summary": "string",
  "felt_rating": "easy|moderate|hard",
  "perceived_effort": "low|medium|high"
}}
"""

    # GitHub Models API format
    url = f"{AI_API_BASE}/models/{AI_MODEL}/inference"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2024-10-14"
    }

    payload = {
        "input": [
            {"role": "user", "content": prompt}
        ]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(f"AI API error {resp.status_code}: {resp.text}")

    data = resp.json()

    # Extract model output
    content = data["output_text"]

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