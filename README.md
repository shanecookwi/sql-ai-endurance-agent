# SQL AI Endurance Agent

**Microsoft SQL + AI Datathon Submission**  
By Shane Cook

## Overview
SQL AI Endurance Agent is a SQL Server 2025–powered semantic search and summarization system built for the Microsoft SQL + AI Datathon.
It uses real endurance training data (swim, bike, run, and marathon workouts) to demonstrate:

- AI‑generated workout summaries
- AI‑generated embeddings
- Vector search
- SQL‑grounded RAG
- A clean, reproducible SQL pipeline

This project shows how SQL Server 2025 can act as the core intelligence layer for athlete insights.

## Features
- AI_GENERATE_TEXT for natural‑language workout summaries
- AI_GENERATE_EMBEDDINGS for vector representations
- Semantic search across endurance training logs
- RAG queries grounded in SQL tables
- Sport‑specific summary procedures
- Judge‑friendly, reproducible SQL scripts


## Repository Structure
```
sql-ai-endurance-agent/
│
├── sql/                 # All SQL scripts
├── docs/                # Architecture, narrative, setup
└── data/                # Optional CSVs
```

## How to Run
- Install SQL Server 2025
- Enable AI features
- Run scripts in order:
    01_schema.sql
    02_load_data.sql
    03_create_http_credentials.sql
    04_create_external_models.sql
    05_generate_ai_content.sql
    06_generate_embeddings.sql
    07_vector_index.sql
    08_summary_procedures.sql
    09_semantic_search.sql
    10_rag_queries.sql

- Test semantic search:
```sql
SELECT *
FROM dbo.SearchWorkouts('long run with fatigue');
```

## Datathon Narrative
This project frames SQL Server as an endurance athlete’s intelligence engine — capable of turning raw Garmin‑style metrics into meaningful insights, summaries, and semantic search results.

See /docs/narrative.md for the full story.



## License
MIT
