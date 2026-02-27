CREATE PROCEDURE dbo.fn_ai_generate_text
    @prompt NVARCHAR(MAX),
    @model NVARCHAR(128) = 'textgen_gpt_4o_mini',
    @response_text NVARCHAR(MAX) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE 
        @url NVARCHAR(4000),
        @credential SYSNAME,
        @model_name NVARCHAR(200);

    -- Look up model metadata
    SELECT 
        @url = m.location,
        @credential = c.name,
        @model_name = m.model
    FROM sys.external_models AS m
    JOIN sys.database_scoped_credentials AS c
        ON m.credential_id = c.credential_id
    WHERE m.name = @model;

    IF @url IS NULL
    BEGIN
        SET @response_text = 'Error: Model not found in sys.external_models';
        RETURN;
    END

    -- Build OpenAI-style payload
    DECLARE @payload NVARCHAR(MAX) =
    (
        SELECT
            @model_name AS [model],
            (
                SELECT 'user' AS [role], @prompt AS [content]
                FOR JSON PATH
            ) AS [messages]
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    );

    DECLARE @raw_response NVARCHAR(MAX);
    DECLARE @ret INT;

    EXEC @ret = sys.sp_invoke_external_rest_endpoint
        @url = @url,
        @method = 'POST',
        @payload = @payload,
        @credential = @credential,
        @response = @raw_response OUTPUT;

    IF @ret = 0
        SET @response_text = JSON_VALUE(@raw_response, '$.choices[0].message.content');
    ELSE
        SET @response_text = CONCAT('Error: ', @raw_response);
END
GO