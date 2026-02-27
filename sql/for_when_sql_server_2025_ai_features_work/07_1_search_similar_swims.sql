-- -----------------------------------------------------------------------------
-- SECTION 3: Stored Procedure Alternative (Recommended)
-- -----------------------------------------------------------------------------
-- This stored procedure encapsulates the search logic, avoiding batch issues
-- Run this once to create the procedure, then call it anytime

CREATE OR ALTER PROCEDURE dbo.search_similar_swim_workouts
    @search_text NVARCHAR(MAX),
    @top_n INT = 10,
    @min_similarity DECIMAL(19,16) = 0.3
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @qv VECTOR(1536) = AI_GENERATE_EMBEDDINGS(@search_text USE MODEL embedding_text_embedding_3_small_1536);

    PRINT 'Embedding bytes: ' + COALESCE(CAST(DATALENGTH(@qv) AS NVARCHAR(20)), 'NULL');

    DROP TABLE IF EXISTS similar_swims;

    SELECT TOP (@top_n)
        w.swim_workout_id,
        w.workout_date,
        w.distance_yards,
        w.notes,
        r.distance,
        1 - r.distance AS similarity
    INTO similar_swims
    FROM VECTOR_SEARCH(
            TABLE = dbo.swim_workouts AS w,
            COLUMN = embedding,
            SIMILAR_TO = @qv,
            METRIC = 'cosine',
            TOP_N = @top_n
        ) AS r
    WHERE r.distance <= 1 - @min_similarity
    ORDER BY r.distance;

    SELECT * FROM similar_swims;
END;
GO

-- -----------------------------------------------------------------------------
-- SECTION 4: Example Usage of Stored Procedure
-- -----------------------------------------------------------------------------
-- After creating the procedure, you can run searches easily:

EXEC dbo.search_similar_swim_workouts 
    @search_text = 'steady aerobic swim with good technique',
    @top_n = 5,
    @min_similarity = 0.5;
GO