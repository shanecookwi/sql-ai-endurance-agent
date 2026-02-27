-- =============================================================================
-- 05_generate_ai_content.sql
-- =============================================================================
-- Purpose:
--   Uses GitHub Models (GPT-4o-mini) to generate:
--     - notes (AI summary of the workout)
--     - felt_rating (how the athlete felt)
--     - perceived_effort (RPE-style effort)
--
-- Requirements:
--   - 03_create_http_credentials.sql has been run
--   - External model "textgen_gpt_4o_mini" exists (created below if missing)
--   - Workout table contains raw metrics (distance, duration, pace, etc.)
--
-- Output:
--   Updates each workout row with AI-generated fields.
-- =============================================================================

USE SqlAiDatathon;
GO

-- ---------------------------------------------------------------------------
-- SECTION 2: Generate AI Notes + Ratings for Each Workout
-- ---------------------------------------------------------------------------
-- This uses CROSS APPLY to call the model once per row.

UPDATE W
SET 
    notes = J.summary,
    felt_rating = J.felt_rating,
    perceived_effort = J.perceived_effort
FROM dbo.Workouts AS W
CROSS APPLY (
    SELECT AI_GENERATE_TEXT(
        CONCAT(
            'You are an endurance training assistant. ',
            'Given the workout metrics below, generate a JSON object with: ',
            '1) "summary": a concise workout summary, ',
            '2) "felt_rating": how the athlete likely felt (e.g., "strong", "steady", "fatigued"), ',
            '3) "perceived_effort": effort level (e.g., "easy", "moderate", "hard"). ',
            'Keep responses short and practical. ',
            'Workout metrics: ',
            'distance_km=', W.distance_km, ', ',
            'duration_min=', W.duration_min, ', ',
            'avg_pace=', W.avg_pace, ', ',
            'avg_hr=', W.avg_hr, ', ',
            'max_hr=', W.max_hr
        )
        USE MODEL textgen_gpt_4o_mini
    ) AS RawJson
) AS R
CROSS APPLY (
    SELECT
        JSON_VALUE(R.RawJson, '$.summary') AS summary,
        JSON_VALUE(R.RawJson, '$.felt_rating') AS felt_rating,
        JSON_VALUE(R.RawJson, '$.perceived_effort') AS perceived_effort
) AS J
WHERE 
    W.notes IS NULL
    OR W.felt_rating IS NULL
    OR W.perceived_effort IS NULL;

PRINT 'AI content generation complete.';
GO