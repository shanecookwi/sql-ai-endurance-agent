import os
import pyodbc
import time
from dotenv import load_dotenv
from anthropic import Anthropic


load_dotenv()

# --- ENVIRONMENT VARIABLES ---

# --- SQL CONNECTION SETTINGS ---
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

if not all([SQL_SERVER, SQL_DATABASE, SQL_USER, SQL_PASSWORD]):
    raise RuntimeError("SQL connection settings missing in .env")

# --- DB CONNECTION HELPER ---
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

# --- ANTHROPIC MODELS CLIENT ---
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("ANTHROPIC_EMBED_MODEL", "claude-3-5-sonnet-20241022")

# --- EMBEDDING FUNCTION ---
def embed_text(text: str):
    """Generate a 1536‑dim embedding using Anthropic Models."""
    response = client.embeddings.create(
        model=MODEL,
        input=text
    )
    return response.data[0].embedding

# --- MAIN PIPELINE ---
def regenerate_embeddings():
    conn = get_connection()
    cursor = conn.cursor()

    print("Fetching swim workouts...")
    cursor.execute("SELECT swim_workout_id, notes FROM swim_workouts")
    rows = cursor.fetchall()

    print(f"Found {len(rows)} workouts. Generating embeddings...")

    update_sql = """
        UPDATE swim_workouts
        SET embedding = ?
        WHERE swim_workout_id = ?
    """

    for workout_id, notes in rows:
        text = notes or ""

        time.sleep(1.0) # <-- prevents Anthropic rate limit

        vec = embed_text(text)

        # Convert Python list[float] → SQL VARBINARY
        # pyodbc accepts bytes; pack floats into binary
        import struct
        binary_vec = struct.pack(f"{len(vec)}f", *vec)

        cursor.execute(update_sql, (binary_vec, workout_id))
        conn.commit()

    print("All embeddings updated.")

    print("Rebuilding HNSW index...")
    cursor.execute("ALTER INDEX swim_workouts_embedding_idx ON swim_workouts REBUILD;")
    conn.commit()

    print("Index rebuilt. Running test query...")

    # --- TEST QUERY ---
    test_query = "steady aerobic swim with good technique"
    qvec = embed_text(test_query)
    binary_qvec = struct.pack(f"{len(qvec)}f", *qvec)

    cursor.execute("""
        SELECT TOP 5
            swim_workout_id,
            notes,
            VECTOR_DISTANCE(embedding, ?) AS distance
        FROM swim_workouts
        ORDER BY distance ASC;
    """, (binary_qvec,))

    results = cursor.fetchall()
    print("\nTop matches:")
    for r in results:
        print(f"- ID {r.swim_workout_id}: {r.notes[:80]}... (distance={r.distance})")

    cursor.close()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    regenerate_embeddings()