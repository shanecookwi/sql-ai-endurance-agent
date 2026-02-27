UPDATE swim_workouts
SET embedding = AI_GENERATE_EMBEDDINGS(
        notes
        USE MODEL embedding_text_embedding_3_small_1536
    )
WHERE embedding IS NULL;
