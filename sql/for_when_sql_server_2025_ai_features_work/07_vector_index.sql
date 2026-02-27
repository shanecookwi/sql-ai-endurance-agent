CREATE VECTOR INDEX idx_swim_embedding
ON swim_workouts(embedding)
WITH (
    TYPE = 'HNSW',
    DIMENSION = 1536,
    METRIC = 'COSINE'
);

