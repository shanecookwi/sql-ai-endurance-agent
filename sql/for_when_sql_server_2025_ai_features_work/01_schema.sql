-- =============================================================================
-- Mission 1: Create SqlAiDatathon Database and Tables
-- =============================================================================
-- ⚠️ BEFORE RUNNING: Verify you are connected to SqlAiDatathon (or create it first)
-- =============================================================================
-- Description: Creates the SqlAiDatathon database and the swim_workouts
--              table with vector embedding support for semantic search capabilities.
-- 
-- Prerequisites:
--   - SQL Server 2025 or Azure SQL Database with vector support enabled
--   - Appropriate permissions to create databases and tables
--
-- Usage:
--   Run this script first before loading data with 02-load-table.sql

-- -----------------------------------------------------------------------------
-- SECTION 1: Create Database
-- -----------------------------------------------------------------------------
USE SqlAiDatathon;
GO

-- -----------------------------------------------------------------------------
-- SECTION 2: Create swim_workouts Table
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS [dbo].[swim_workouts];


CREATE TABLE swim_workouts
(
    swim_workout_id       INT IDENTITY(1,1) PRIMARY KEY,

    -- Core workout metrics
    activity_type         NVARCHAR(100)     NULL,   -- e.g., "Pool Swim", "Open Water"
    workout_date          DATETIME2         NOT NULL,
    title                 NVARCHAR(200)     NULL,

    distance_yards        FLOAT             NULL,
    calories              INT               NULL,
    [time]                NVARCHAR(50)      NULL,   -- e.g., "0:40:29"
    avg_hr                INT               NULL,
    max_hr                INT               NULL,
    aerobic_te            FLOAT             NULL,
    avg_pace              NVARCHAR(50)      NULL,   -- e.g., "1:50"
    best_pace             NVARCHAR(50)      NULL,   -- e.g., "1:18"

    -- Technique & efficiency metrics
    total_strokes         INT               NULL,
    avg_swolf             FLOAT             NULL,
    avg_stroke_rate       FLOAT             NULL,

    -- Session structure
    best_lap_time         NVARCHAR(50)      NULL,
    number_of_laps        INT               NULL,
    moving_time           NVARCHAR(50)      NULL,
    elapsed_time          NVARCHAR(50)      NULL,

    -- Training load
    training_stress_score FLOAT             NULL,

    -- AI-generated summary
    notes                 NVARCHAR(MAX)     NULL,
    felt_rating           NVARCHAR(20)      NULL,
    perceived_effort      NVARCHAR(20)      NULL,

    -- Embedding vector (1536 dims for text-embedding-3-small models)
    embedding             VECTOR(1536)      NULL    -- this does not work in Sql Server 2025. it creates it as embdding (vector(varbindary(6152)), null) with my Microsoft SQL Server 2025 (RTM) - 17.0.1000.7 (X64) 
);

-- -----------------------------------------------------------------------------
-- SECTION 3: Enable Preview Features (Required for Vector Support)
-- -----------------------------------------------------------------------------
ALTER DATABASE SCOPED CONFIGURATION
SET PREVIEW_FEATURES = ON;
GO

--- -----------------------------------------------------------------------------
-- SECTION 4: Enable External REST Endpoint (Required for sp_invoke_external_rest_endpoint)
-- -----------------------------------------------------------------------------
EXECUTE sp_configure 'external rest endpoint enabled', 1;
RECONFIGURE WITH OVERRIDE;
