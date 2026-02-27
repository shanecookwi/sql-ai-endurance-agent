USE SqlAiDatathon;
GO

-- ---------------------------------------------------------------------------
-- SECTION 1a: Create External Model for Text Generation (GPT-4o-mini)
-- ---------------------------------------------------------------------------
/* IF NOT EXISTS (SELECT * FROM sys.external_models WHERE [name] = 'textgen_gpt_4o_mini')
BEGIN
    CREATE EXTERNAL MODEL textgen_gpt_4o_mini
    WITH (
          LOCATION = 'https://models.github.ai/inference/text',
          API_FORMAT = 'OpenAI',
          MODEL_TYPE = EMBEDDINGS,
          MODEL = 'gpt-4o-mini',
          CREDENTIAL = [https://models.github.ai/inference]
    );
END


IF NOT EXISTS (SELECT * FROM sys.external_models WHERE [name] = 'textgen_gpt_4o_mini_v3')
BEGIN
    CREATE EXTERNAL MODEL textgen_gpt_4o_mini_v3
    WITH (
          LOCATION = 'https://models.github.ai/v1/chat/completions',
          API_FORMAT = 'OpenAI',
          MODEL_TYPE = EMBEDDINGS,
          MODEL = 'gpt-4o-mini',
          CREDENTIAL = [https://models.github.ai/rest]
    );
END
GO


-- ---------------------------------------------------------------------------
-- SECTION 1b: Test External Model for Text Generation (GPT-4o-mini)
-- ---------------------------------------------------------------------------
SELECT AI_GENERATE_TEXT(
    'Write a one‑sentence motivational message for an endurance athlete.'
    USE MODEL textgen_gpt_4o_mini
) AS result;

*/


-- ---------------------------------------------------------------------------
-- SECTION 2a: Create External Model for Embeddings (text-embedding-3-small)
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.external_models WHERE [name] = 'embedding_text_embedding_3_small_1536')
BEGIN
    CREATE EXTERNAL MODEL embedding_text_embedding_3_small_1536
    WITH (
          LOCATION = 'https://models.github.ai/inference/embeddings',
          API_FORMAT = 'OpenAI',
          MODEL_TYPE = EMBEDDINGS,
          MODEL = 'text-embedding-3-small',
          CREDENTIAL = [https://models.github.ai/inference],
          PARAMETERS = '{"dimensions":1536}'
    );
END
GO

-- ---------------------------------------------------------------------------
-- SECTION 2b: Test External Model for Embeddings (text-embedding-3-small)
-- ---------------------------------------------------------------------------
SELECT AI_GENERATE_EMBEDDINGS('Test text' USE MODEL embedding_text_embedding_3_small_1536) AS test_embedding;