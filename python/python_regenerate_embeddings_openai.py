import os
import pyodbc
import time
from dotenv import load_dotenv
from openai import OpenAI
from utils import get_connection
import struct

load_dotenv()

# --- ENVIRONMENT VARIABLES ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY missing in .env")

# Use OpenAI’s official API (NOT GitHub Models)
client = OpenAI(api_key=openai_api_key)

EMBED_MODEL = "text-embedding-3-small"   # 1536-dim

# --- EMBEDDING FUNCTION ---
def embed_text(text: str):
    """Generate a 1536‑dim embedding using OpenAI."""
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

        time.sleep(0.5)  # OpenAI is stable; small delay is enough

        vec = embed_text(text)

        # Convert Python list[float] → SQL VARBINARY
        binary_vec = struct.pack(f"{len(vec)}f", *vec)

        cursor.execute(update_sql, (binary_vec, workout_id))
        conn.commit()

    print("All embeddings updated.")

    # print("Rebuilding HNSW index...")
    #cursor.execute("ALTER INDEX idx_swim_embedding ON swim_workouts REBUILD;")
    #conn.commit()

    #print("Index rebuilt. Running test query...")
    # print("Running test query...")

    # # --- TEST QUERY ---
    # test_query = "steady aerobic swim with good technique"
    # qvec = embed_text(test_query)
    # binary_qvec = struct.pack(f"{len(qvec)}f", *qvec)

    # cursor.execute("""
    #     SELECT TOP 5
    #         swim_workout_id,
    #         notes,
    #         VECTOR_DISTANCE(embedding, ?) AS distance
    #     FROM swim_workouts
    #     ORDER BY distance ASC;
    # """, (binary_qvec,))

    # results = cursor.fetchall()
    # print("\nTop matches:")
    # for r in results:
    #     print(f"- ID {r.swim_workout_id}: {r.notes[:80]}... (distance={r.distance})")

    cursor.close()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    regenerate_embeddings()