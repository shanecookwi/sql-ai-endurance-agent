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

import struct
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils import get_connection

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

model_endpoint_url=os.getenv("MODEL_ENDPOINT_URL") 
if not model_endpoint_url:
    raise RuntimeError("MODEL_ENDPOINT_URL is missing. Add it to your .env file.")

# GitHub Models client (uses your GITHUB_TOKEN environment variable)
# client = OpenAI(
#     api_key=openai_api_key,
#     base_url=model_endpoint_url
# )

# OpenAI official API client (uses OPENAI_API_KEY)
client = OpenAI(api_key=openai_api_key)


# Embedding model name
EMBED_MODEL = "text-embedding-3-small"


# ------------------------------------------------------------
# Embedding generation
# ------------------------------------------------------------

def embed(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding   # list of floats




# ------------------------------------------------------------
# SQL retrieval
# ------------------------------------------------------------

def search_similar_swims(query_text: str, top_n: int = 5):
    vec = embed(query_text)
    qv_bin = struct.pack(f"{len(vec)}f", *vec)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP (?)
            swim_workout_id,
            notes,
            VECTOR_DISTANCE(embedding, ?, 'cosine') AS distance
        FROM swim_workouts
        ORDER BY distance ASC;
    """, (top_n, qv_bin))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows




# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

def format_results(rows):
    """
    Convert SQL rows into a list of dictionaries for readability.
    """
    formatted = []
    for r in rows:
        formatted.append({
            "id": r.swim_workout_id,
            "date": str(r.workout_date),
            "distance_yards": r.distance_yards,
            "notes": r.notes,
            "similarity": float(r.similarity)
        })
    return formatted


def print_results(results):
    """
    Pretty-print the semantic search results.
    """
    print("\nTop Semantic Matches:\n")
    for item in results:
        print(f"- Workout ID: {item['id']}")
        print(f"  Date: {item['date']}")
        print(f"  Distance (yards): {item['distance_yards']}")
        print(f"  Notes: {item['notes']}")
        print(f"  Similarity: {item['similarity']:.4f}")
        print("")


# ------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Endurance Swim Workout Semantic Search")
    print("-----------------------------------")

    query = input("Enter your search text: ")

    rows = search_similar_swims(query)
    results = format_results(rows)

    print_results(results)