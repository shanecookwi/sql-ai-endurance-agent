-- =============================================================================
-- Create HTTP Credentials for GitHub Models
-- =============================================================================
-- Description:
--   Creates a database scoped credential for GitHub Models so SQL Server can
--   call AI_GENERATE_TEXT and AI_GENERATE_EMBEDDINGS.
--
-- Prerequisites:
--   - You have created a GitHub fine-grained PAT with "models:read" scope
--   - Replace <GITHUB_TOKEN> with your actual token (no angle brackets)
-- =============================================================================

USE SqlAiDatathon;
GO

-- ---------------------------------------------------------------------------
-- SECTION 1: Ensure Database Master Key Exists
-- ---------------------------------------------------------------------------
-- SQL Server requires a master key before storing encrypted credentials.
-- This block creates one only if it does not already exist.
-- The password is only used to encrypt the key and is not needed again.
-- ---------------------------------------------------------------------------
IF NOT EXISTS (
    SELECT * FROM sys.symmetric_keys 
    WHERE name = '##MS_DatabaseMasterKey##'
)
BEGIN
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'TemporaryPassword_ForEncryptionOnly_123!';
END
GO

-- ---------------------------------------------------------------------------
-- SECTION 2: Create HTTP Credential for GitHub Models
-- ---------------------------------------------------------------------------
-- Used by AI_GENERATE_EMBEDDINGS
-- ---------------------------------------------------------------------------
IF NOT EXISTS (
    SELECT * FROM sys.database_scoped_credentials
    WHERE [name] = 'https://models.github.ai/inference'
)
BEGIN
    CREATE DATABASE SCOPED CREDENTIAL [https://models.github.ai/inference]
    WITH IDENTITY = 'HTTPEndpointHeaders',
         SECRET = '{"Authorization":"Bearer <GITHUB_TOKEN>"}';
END
GO

-- ---------------------------------------------------------------------------
-- SECTION 3: Verify Credential
-- ---------------------------------------------------------------------------
SELECT *
FROM sys.database_scoped_credentials
WHERE [name] = 'https://models.github.ai/inference';
GO
