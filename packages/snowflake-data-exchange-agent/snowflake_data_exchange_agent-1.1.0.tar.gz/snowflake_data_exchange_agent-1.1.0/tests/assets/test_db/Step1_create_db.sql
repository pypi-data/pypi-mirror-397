--------------
-- SETTINGS --
--------------
EXEC sp_set_session_context 'DB_BACKUP_FILE_PATH', N'/tmp/WideWorldImportersDW-Full.bak';
EXEC sp_set_session_context 'NUM_INT_COLS', 46;  -- number of INT columns to add, additionally to the initial 21 columns
GO

----------
-- INIT --
----------
EXEC sp_set_session_context 'EXPECTED_MIN_INITIAL_ROWS', 228265;
EXEC sp_set_session_context 'FAILED', 0;
GO

--------------------------
-- Step 1.1: RESTORE DB --
--------------------------
PRINT(N'BEGIN: Restore DB...');
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    -- Prepare to restore
    BEGIN TRY
        USE master;
        ALTER DATABASE WideWorldImportersDW
        SET SINGLE_USER
        WITH ROLLBACK IMMEDIATE;
    END TRY
    BEGIN CATCH
        -- If the database does not exist yet, ignore the error
    END CATCH;

    -- Restore
    DECLARE @db_backup_file_path NVARCHAR(MAX) = CAST(SESSION_CONTEXT(N'DB_BACKUP_FILE_PATH') AS NVARCHAR(MAX));
    BEGIN TRY
        RESTORE DATABASE WideWorldImportersDW
        FROM DISK = @db_backup_file_path
        WITH
            MOVE N'WWI_Primary'
                TO N'/var/opt/mssql/data/WideWorldImportersDW.mdf',
            MOVE N'WWI_UserData'
                TO N'/var/opt/mssql/data/WideWorldImportersDW_UserData.ndf',
            MOVE N'WWI_Log'
                TO N'/var/opt/mssql/log/WideWorldImportersDW.ldf',
            MOVE N'WWIDW_InMemory_Data_1'
                TO N'/var/opt/mssql/data/WideWorldImportersDW_InMemory_Data_1',
        NOUNLOAD,
        STATS = 5;
        ALTER DATABASE WideWorldImportersDW
        SET MULTI_USER;
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during restore. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
        -- List backup files to check if they match the expected files
        PRINT(N'Listing backup files to check if they match the expected files...');
        RESTORE FILELISTONLY
        FROM DISK = @db_backup_file_path;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @RowCount INT;
        SELECT @RowCount = COUNT(1)
        FROM WideWorldImportersDW.Fact.Sale;
        IF @RowCount < CAST(SESSION_CONTEXT(N'EXPECTED_MIN_INITIAL_ROWS') AS INT)
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Restore DB failed.')
            RETURN;
        END
    END

    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Restore DB successfully.');
    END
END
GO

-------------------------------
-- Step 1.2: ADD INT COLUMNS --
-------------------------------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'BEGIN: Add INT columns...');
END
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    -- Add extra INT columns (4 bytes each)
    BEGIN TRY
        DECLARE @sql_add_int_cols NVARCHAR(MAX) = N'';

        DECLARE @num_int_cols_to_add INT = CAST(SESSION_CONTEXT(N'NUM_INT_COLS') AS INT);
        DECLARE @counter_add INT = 1;

        WHILE @counter_add <= @num_int_cols_to_add
        BEGIN
            SET @sql_add_int_cols += N'
                ALTER TABLE WideWorldImportersDW.Fact.Sale ADD [DummyIntCol_' + CAST(@counter_add AS NVARCHAR(5)) + '] INT NULL;' + CHAR(13);
            SET @counter_add = @counter_add + 1;
        END

        --PRINT(@sql_add_int_cols);
        EXEC(@sql_add_int_cols);
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during add INT columns. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @RowCount INT;
        SELECT @RowCount = COUNT(1)
        FROM WideWorldImportersDW.INFORMATION_SCHEMA.COLUMNS
        WHERE
            TABLE_CATALOG = 'WideWorldImportersDW'
            AND TABLE_SCHEMA = 'Fact'
            AND TABLE_NAME = 'Sale'
            AND COLUMN_NAME LIKE 'DummyIntCol_%';

        IF @RowCount < CAST(SESSION_CONTEXT(N'NUM_INT_COLS') AS INT)
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Add INT columns failed.')
            RETURN;
        END
    END


    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Add INT columns successfully.');
    END
END
GO

---------------------------------
-- Step 1.3: ADD LARGE COLUMNS --
---------------------------------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'BEGIN: Add large columns...');
END
GO

IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    -- Add three large variable-length columns to maximize row size and stress I/O
    BEGIN TRY
        ALTER TABLE WideWorldImportersDW.Fact.Sale ADD [LargeDataCol_VARCHAR] VARCHAR(500) NULL;
        ALTER TABLE WideWorldImportersDW.Fact.Sale ADD [LargeDataCol_NVARCHAR] NVARCHAR(4000) NULL;
        ALTER TABLE WideWorldImportersDW.Fact.Sale ADD [LargeDataCol_BINARY] VARBINARY(800) NULL;
    END TRY
    BEGIN CATCH
        PRINT(N'Error occurred during add large columns. Error: ' + ERROR_MESSAGE());
        EXEC sp_set_session_context 'FAILED', 1;
    END CATCH;

    -- Verify
    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        DECLARE @RowCount INT;
        SELECT @RowCount = COUNT(1)
        FROM WideWorldImportersDW.INFORMATION_SCHEMA.COLUMNS
        WHERE
            TABLE_CATALOG = 'WideWorldImportersDW'
            AND TABLE_SCHEMA = 'Fact'
            AND TABLE_NAME = 'Sale'
            AND COLUMN_NAME LIKE 'LargeDataCol_%';

        IF @RowCount < 3
        BEGIN
            EXEC sp_set_session_context 'FAILED', 1;
            PRINT(N'Add large columns failed.')
            RETURN;
        END
    END


    IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
    BEGIN
        PRINT(N'END: Add large columns successfully.');
    END
END
GO

---------
-- END --
---------
IF (CAST(SESSION_CONTEXT(N'FAILED') AS INT) = 0)
BEGIN
    PRINT(N'FINISHED successfully: The test database has been created.');
END
ELSE
BEGIN
    PRINT(N'FINISHED with ERRORS: The test database creation failed.');
END
GO
