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

-- =============================================================================
-- 05_generate_ai_content.sql
-- =============================================================================
-- Purpose:
--   Uses GitHub Models (GPT-4o-mini via fn_ai_generate_text) to generate:
--     - notes (AI summary of the workout)
--     - felt_rating (how the athlete felt)
--     - perceived_effort (RPE-style effort)
--
-- Requirements:
--   - 03_create_http_credentials.sql has been run
--   - 04_create_external_models.sql has been run (textgen_gpt_4o_mini exists)
--   - fn_ai_generate_text exists
--   - swim_workouts table uses distance_yards
-- =============================================================================

USE SqlAiDatathon;
GO

CREATE OR ALTER PROCEDURE dbo.generate_swim_ai_content
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE 
        @swim_workout_id INT,
        @prompt NVARCHAR(MAX),
        @json_output NVARCHAR(MAX);

    -------------------------------------------------------------------------
    -- Cursor over rows that are missing AI content
    -------------------------------------------------------------------------
    DECLARE swim_cur CURSOR FAST_FORWARD FOR
        SELECT 
            swim_workout_id,
            CONCAT(
                'You are an endurance swim coach. Using ONLY the metrics provided, return a JSON object with:',
                ' 1) "summary": a concise 2–3 sentence description of the swim,',
                ' 2) "felt_rating": how the athlete likely felt (one word),',
                ' 3) "perceived_effort": effort level (easy, moderate, hard). ',
                'Focus on pacing, efficiency, technique, and overall aerobic load. ',
                'Do NOT add metrics that were not provided. ',
                'Metrics: ',
                'Distance: ', distance_yards, ' yards; ',
                'Time: ', time, '; ',
                'Avg HR: ', avg_hr, '; ',
                'Max HR: ', max_hr, '; ',
                'Aerobic TE: ', aerobic_te, '; ',
                'Avg Pace: ', avg_pace, '; ',
                'Best Pace: ', best_pace, '; ',
                'Total Strokes: ', total_strokes, '; ',
                'Avg Swolf: ', avg_swolf, '; ',
                'Avg Stroke Rate: ', avg_stroke_rate, '; ',
                'Number of Laps: ', number_of_laps, '; ',
                'Moving Time: ', moving_time, '; ',
                'Elapsed Time: ', elapsed_time, '; ',
                'Best Lap Time: ', best_lap_time, '; ',
                'Calories: ', calories, '; ',
                'Training Stress Score: ', training_stress_score, '.'
            ) AS prompt
        FROM swim_workouts
        WHERE 
            notes IS NULL
            OR felt_rating IS NULL
            OR perceived_effort IS NULL;


    OPEN swim_cur;

    FETCH NEXT FROM swim_cur INTO @swim_workout_id, @prompt;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        ---------------------------------------------------------------------
        -- Call your custom AI procedure once per workout
        ---------------------------------------------------------------------
        SET @json_output = NULL;

        EXEC dbo.fn_ai_generate_text
            @prompt        = @prompt,
            @model         = 'textgen_gpt_4o_mini_v3',
            @response_text = @json_output OUTPUT;


PRINT 'RAW OUTPUT: ' + ISNULL(@json_output, '<NULL>');

        ---------------------------------------------------------------------
        -- Parse JSON and update the row
        ---------------------------------------------------------------------
        UPDATE swim_workouts
        SET 
            notes            = JSON_VALUE(@json_output, '$.summary'),
            felt_rating      = JSON_VALUE(@json_output, '$.felt_rating'),
            perceived_effort = JSON_VALUE(@json_output, '$.perceived_effort')
        WHERE swim_workout_id = @swim_workout_id;

        FETCH NEXT FROM swim_cur INTO @swim_workout_id, @prompt;
    END

    CLOSE swim_cur;
    DEALLOCATE swim_cur;
END;
GO