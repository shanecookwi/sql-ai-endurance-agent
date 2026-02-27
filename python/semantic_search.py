"""
Semantic Search Tool for Endurance Swim Workouts
------------------------------------------------

This script implements a semantic search tool that:
1. Generates an embedding for a user query using GitHub Models.
2. Calls a SQL Server stored procedure (search_similar_swim_workouts)
   to retrieve the most semantically similar swim workouts.
3. Prints the results in a clean, readable format.

This matches the Datathon "Semantic Search Tool" category:
- SQL is the data source
- Embeddings power semantic retrieval
- No chatbot agent or multi-turn conversation
"""

import os
import pyodbc
import struct
import numpy as np
from openai import OpenAI
from utils import get_connection

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)



# ------------------------------------------------------------
# Embedding function (returns list of floats)
# ------------------------------------------------------------

def embed(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding  # list of floats

# ------------------------------------------------------------
# Unpack VARBINARY → list of floats
# ------------------------------------------------------------

def unpack_embedding(binary_vec):
    return struct.unpack("1536f", binary_vec)

# ------------------------------------------------------------
# Cosine similarity
# ------------------------------------------------------------

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ------------------------------------------------------------
# Main semantic search
# ------------------------------------------------------------

def search_similar_swims(query_text: str, top_n: int = 5):
    # 1. Embed the query
    query_vec = embed(query_text)

    # 2. Load all workouts + embeddings from SQL
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT swim_workout_id, notes, embedding FROM swim_workouts")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 3. Compute cosine similarity in Python
    results = []
    for workout_id, notes, binary_vec in rows:
        vec = unpack_embedding(binary_vec)
        sim = cosine_similarity(query_vec, vec)
        results.append((sim, workout_id, notes))

    # 4. Sort by similarity (descending)
    results.sort(key=lambda x: x[0], reverse=True)

    # 5. Return top N
    return results[:top_n]

# ------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    query = input("Enter your search text: ")
    results = search_similar_swims(query)

    print("\nTop matches:\n")
    for sim, workout_id, notes in results:
        print(f"Workout {workout_id} | similarity={sim:.4f}")
        print(f"Notes: {notes}\n")