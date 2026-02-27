import os
import pyodbc
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- ENVIRONMENT VARIABLES ---
openai_api_key = os.getenv("OPENAI_API_KEY")
model_endpoint_url = os.getenv("MODEL_ENDPOINT_URL")
EMBED_MODEL = "text-embedding-3-small"

if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY missing in .env")

if not model_endpoint_url:
    raise RuntimeError("MODEL_ENDPOINT_URL missing in .env")

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

# --- GITHUB MODELS CLIENT ---
client = OpenAI(
    api_key=openai_api_key,
    base_url=model_endpoint_url
)

# --- EMBEDDING FUNCTION ---
def embed_text(text: str):
    """Generate a 1536‑dim embedding using GitHub Models."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    vec = response.data[0].embedding
    if len(vec) != 1536:
        raise RuntimeError(f"Unexpected embedding length: {len(vec)}")
    return vec

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

        time.sleep(1.5) # <-- prevents GitHub rate limit

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