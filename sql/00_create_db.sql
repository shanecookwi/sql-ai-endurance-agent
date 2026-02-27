
CREATE DATABASE SqlAiDatathon;

ALTER DATABASE SqlAiDatathon 
SET COMPATIBILITY_LEVEL = 170;

SELECT name, compatibility_level
FROM sys.databases
WHERE name = 'SqlAiDatathon';