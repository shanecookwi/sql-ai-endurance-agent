CREATE VECTOR INDEX ix_swim_embedding
ON swim_workouts(embedding)
WITH (METRIC = 'COSINE', TYPE = 'DISKANN');
GO


-- ----------------------------------------------------------------------------
-- SECTION 2b: Test Vector Index with a Similarity Search
-- ----------------------------------------------------------------------------
SELECT TOP 5
    swim_workout_id,
    workout_date,
    distance_yards,
    notes,
    VECTOR_DISTANCE(
        embedding,
        AI_GENERATE_EMBEDDINGS(
            'steady aerobic swim with good technique'
            USE MODEL embedding_text_embedding_3_small_1536
        ),
        'COSINE'
    ) AS similarity
FROM swim_workouts
ORDER BY similarity;


SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'swim_workouts'
  AND COLUMN_NAME = 'embedding';