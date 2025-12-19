--------------
-- SETTINGS --
--------------
EXEC sp_set_session_context 'NUM_ROWS_APPROX_TO_ADD', 3775000;  -- additionally to the initial 228265 rows
EXEC sp_set_session_context 'NUM_INT_COLS', 46;  -- number of INT columns added at the database creation
GO

----------
-- INIT --
----------
EXEC sp_set_session_context 'FAILED', 0;
GO

-----------------------
-- Step 2.1: SCALING --
-----------------------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'BEGIN: Scaling...');
END
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    DECLARE @rows_before_scaling INT;
    SELECT @rows_before_scaling = COUNT(1)
    FROM WideWorldImportersDW.Fact.Sale;
    PRINT(N'Rows before scaling: ' + CAST(@rows_before_scaling AS NVARCHAR(20)));

    -- Scale
    BEGIN TRY
        -- NOTE: This process will take a significant amount of time and disk space.
        DECLARE @num_rows_approx INT = CAST(SESSION_CONTEXT(N'NUM_ROWS_APPROX_TO_ADD') AS INT);
        EXEC WideWorldImportersDW.[Application].[Configuration_PopulateLargeSaleTable] @EstimatedRowsFor2012 = @num_rows_approx;
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during scaling. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @rows_after_scaling INT;
        SELECT @rows_after_scaling = COUNT(1)
        FROM WideWorldImportersDW.Fact.Sale;
        DECLARE @rows_added INT = @rows_after_scaling - @rows_before_scaling;
        PRINT(N'Rows after scaling: ' + CAST(@rows_after_scaling AS NVARCHAR(20)));
        PRINT(N'Rows added: ' + CAST(@rows_added AS NVARCHAR(20)));
        IF @rows_added <= 0
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Scaling failed.')
            RETURN;
        END
    END


    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Scaling successfully.');
    END
END
GO

------------------------------------
-- Step 2.2: POPULATE INT COLUMNS --
------------------------------------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'BEGIN: Populate INT columns...');
END
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    -- Populate
    BEGIN TRY
        DECLARE @sql_populate_int_cols NVARCHAR(MAX) = N'';
        DECLARE @num_int_cols_to_populate INT = CAST(SESSION_CONTEXT(N'NUM_INT_COLS') AS INT);
        DECLARE @counter_populate INT = 1;

        WHILE @counter_populate <= @num_int_cols_to_populate
        BEGIN
            -- Assign a pseudo-random integer value (using the row's Sale Key to ensure variation)
            -- We use ISNULL() to ensure we only update NULL values (which should be all the newly inserted rows)
            SET @sql_populate_int_cols += N'
                [DummyIntCol_' + CAST(@counter_populate AS NVARCHAR(5)) + '] = ISNULL([DummyIntCol_' + CAST(@counter_populate AS NVARCHAR(5)) + '], ABS(CHECKSUM(NEWID()) % 100000) + [Sale Key]),'

            SET @counter_populate = @counter_populate + 1;
        END

        SET @sql_populate_int_cols = N'
            UPDATE WideWorldImportersDW.Fact.Sale
            SET ' + RTRIM(RTRIM(@sql_populate_int_cols), ',') + '
            WHERE
                -- Only update the rows that are still NULL in one of the dummy columns
                [DummyIntCol_1] IS NULL
                OR [DummyIntCol_' + CAST(@num_int_cols_to_populate AS NVARCHAR(5)) + '] IS NULL;
        ';

        --PRINT(@sql_populate_int_cols);
        -- NOTE: This will take significant time as it updates a lot of rows,
        -- but it is necessary for a full stress test.
        EXEC(@sql_populate_int_cols);
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during Populate INT columns. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @RowCount INT;
        SELECT @RowCount = COUNT(1)
        FROM WideWorldImportersDW.Fact.Sale
        WHERE DummyIntCol_1 IS NULL;
        IF @RowCount > 0
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Populate INT columns failed.')
            RETURN;
        END
    END


    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Populate INT columns successfully.');
    END
END
GO

--------------------------------------
-- Step 2.3: POPULATE LARGE COLUMNS --
--------------------------------------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'BEGIN: Populate large columns...');
END
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    -- Populate
    BEGIN TRY
        -- NOTE: This will take significant time as it updates a lot of rows,
        -- but it is necessary for a full stress test.
        UPDATE WideWorldImportersDW.Fact.Sale
        SET
            -- Populate with 500 characters
            [LargeDataCol_VARCHAR] = LEFT(
                                            REPLICATE(
                                                CAST(NEWID() AS VARCHAR(36)) + CAST(NEWID() AS VARCHAR(36)),
                                                FLOOR(500 / (36 + 36)) + 1
                                            ),
                                        500),
            -- Populate with 4000 characters
            [LargeDataCol_NVARCHAR] = LEFT(
                                            REPLICATE(
                                                CAST(NEWID() AS NVARCHAR(36)) + CAST(NEWID() AS NVARCHAR(36)),
                                                FLOOR(4000 / (36 + 36)) + 1
                                            ),
                                        4000),
            -- Populate with 800 bytes of binary data
            [LargeDataCol_BINARY] = SUBSTRING(
                                        CAST(
                                            REPLICATE(
                                                CAST(NEWID() AS VARBINARY(16)) +
                                                CAST(NEWID() AS VARBINARY(16)) +
                                                CAST(NEWID() AS VARBINARY(16)) +
                                                CAST(NEWID() AS VARBINARY(16)),
                                                FLOOR(800 / 64)
                                            )
                                        AS VARBINARY(MAX)), 1, 800)
        WHERE
            [LargeDataCol_BINARY] IS NULL;
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during Populate large columns. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @RowCount INT;
        SELECT @RowCount = COUNT(1)
        FROM WideWorldImportersDW.Fact.Sale
        WHERE LargeDataCol_BINARY IS NULL;
        IF @RowCount > 0
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Populate large columns failed.')
            RETURN;
        END
    END


    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Populate large columns successfully.');
    END
END
GO

---------
-- END --
---------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'FINISHED successfully: The test database has been populated.');
END
ELSE
BEGIN
    PRINT(N'FINISHED with ERRORS: The test database population failed.');
END
GO
