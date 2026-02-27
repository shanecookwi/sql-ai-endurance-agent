-- =============================================================================
-- Mission 1: Load swim_workouts Data
-- =============================================================================
-- Description:
--   Loads the swim_workouts.csv file into the swim_workouts table.
--
-- Prerequisites:
--   - 01_schema.sql has been executed
--   - swim_workouts.csv is available locally
--   - Update @FilePath to the full path on your machine
--
-- Usage:
--   Run this script after creating the table in 01_schema.sql
-- =============================================================================

USE SqlAiDatathon;
GO

-- ---------------------------------------------------------------------------
-- SECTION 1: Set CSV File Path
-- ---------------------------------------------------------------------------
-- ⚠️ IMPORTANT:
-- SQL Server requires an absolute path on the local machine.
-- Update BULK path to point to your local copy of swim_workouts.csv.
-- Example:
--   C:\repos\sql-ai-endurance-agent\data\swim_workouts.csv
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- SECTION 2: Load Data Using BULK INSERT + Staging Table
-- ---------------------------------------------------------------------------
DECLARE @FilePath NVARCHAR(4000) =
    'C:\Users\shane\source\repos\sql-ai-endurance-agent\data\swim_workouts.csv'; -- <-- UPDATE THIS

CREATE TABLE #swim_workouts_raw
(
    [Activity Type]          NVARCHAR(50),
    [Date]                   NVARCHAR(50),
    [Favorite]               NVARCHAR(10),
    [Title]                  NVARCHAR(200),
    [Distance]               NVARCHAR(50),
    [Calories]               NVARCHAR(50),
    [Time]                   NVARCHAR(50),
    [Avg HR]                 NVARCHAR(50),
    [Max HR]                 NVARCHAR(50),
    [Aerobic TE]             NVARCHAR(50),
    [Avg Pace]               NVARCHAR(50),
    [Best Pace]              NVARCHAR(50),
    [Training Stress Score®] NVARCHAR(50),
    [Total Strokes]          NVARCHAR(50),
    [Avg. Swolf]             NVARCHAR(50),
    [Avg Stroke Rate]        NVARCHAR(50),
    [Decompression]          NVARCHAR(50),
    [Best Lap Time]          NVARCHAR(50),
    [Number of Laps]         NVARCHAR(50),
    [Moving Time]            NVARCHAR(50),
    [Elapsed Time]           NVARCHAR(50)
);

DECLARE @BulkSql NVARCHAR(MAX) =
    N'BULK INSERT #swim_workouts_raw
      FROM ''' + REPLACE(@FilePath, '''', '''''') + N'''
      WITH (
          FORMAT = ''CSV'',
          FIRSTROW = 2,
          FIELDQUOTE = ''"'',
          CODEPAGE = ''65001''
      );';

EXEC sys.sp_executesql @BulkSql;

INSERT INTO dbo.swim_workouts
(
    activity_type,
    workout_date,
    title,
    distance_yards,
    calories,
    time,
    avg_hr,
    max_hr,
    aerobic_te,
    avg_pace,
    best_pace,
    total_strokes,
    avg_swolf,
    avg_stroke_rate,
    best_lap_time,
    number_of_laps,
    moving_time,
    elapsed_time,
    training_stress_score
)
SELECT
    [Activity Type] AS activity_type,
    TRY_CONVERT(DATETIME2, [Date]) AS workout_date,
    [Title] AS title,
    TRY_CONVERT(FLOAT, REPLACE([Distance], ',', '')) AS distance,
    TRY_CONVERT(INT, [Calories]) AS calories,
    [Time] AS time,
    TRY_CONVERT(INT, [Avg HR]) AS avg_hr,
    TRY_CONVERT(INT, [Max HR]) AS max_hr,
    TRY_CONVERT(FLOAT, [Aerobic TE]) AS aerobic_te,
    [Avg Pace] AS avg_pace,
    [Best Pace] AS best_pace,
    TRY_CONVERT(INT, [Total Strokes]) AS total_strokes,
    TRY_CONVERT(FLOAT, [Avg. Swolf]) AS avg_swolf,
    TRY_CONVERT(FLOAT, [Avg Stroke Rate]) AS avg_stroke_rate,
    [Best Lap Time] AS best_lap_time,
    TRY_CONVERT(INT, [Number of Laps]) AS number_of_laps,
    [Moving Time] AS moving_time,
    [Elapsed Time] AS elapsed_time,
    TRY_CONVERT(FLOAT, [Training Stress Score®]) AS training_stress_score
FROM #swim_workouts_raw;

DROP TABLE #swim_workouts_raw;
GO


-- ---------------------------------------------------------------------------
-- SECTION 3: Verify Load
-- ---------------------------------------------------------------------------

SELECT TOP 10 *
FROM dbo.swim_workouts;
GO