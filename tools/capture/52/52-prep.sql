-- Scenario 52 preparation (capture-scenarios.md §3 "52"). Run by 52-server.ps1 prep with BOTH accounts at the login
-- screen (the WM reads the avatar list at the world login, the zone writes characters back while they are online).
--   $(DashChar)  (account "admin")        renamed to $(DashName) (has a '-': the client forces the plain rename, step 2),
--                                         GM 100 (step 3 &kickout), tutorial state 2, login point RouN 5874,6530
--   $(CharB)     (account "testaccountB") tutorial state 2, login point RouN 5950,6530 (zone 0, the zone of A, step 3)
--   S20 (§8.21): p_Char_Rename replaced by the 2016 text (plain UPDATE, nRet = @@ERROR); old text in dbo.X07_save_20
-- $(TutChar) is created in the client during step 1 and must not exist yet; $(FreeName) is the free name of step 2;
-- $(TakenName) the existing name of step 2. Old values in dbo.X52_save. Undo: 52-cleanup.sql.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);

IF OBJECT_ID('dbo.X52_save') IS NOT NULL
BEGIN RAISERROR('dbo.X52_save exists: prep already ran. Go on with the run, or run cleanup first.', 16, 1); RETURN; END
IF OBJECT_ID('dbo.X07_save_20') IS NOT NULL
BEGIN RAISERROR('dbo.X07_save_20 exists (S20 still installed from an earlier run): restore it first (52-server.ps1 cleanup)', 16, 1); RETURN; END

DECLARE @dash int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(DashChar)' AND bDeleted = 0);
DECLARE @b    int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(CharB)'    AND bDeleted = 0);
IF @dash IS NULL BEGIN RAISERROR('character $(DashChar) not found on admin (give -DashChar <a spare character of admin>)', 16, 1); RETURN; END
IF @b IS NULL    BEGIN RAISERROR('character $(CharB) not found: create it in the client on testaccountB (any class), or give -CharB <name>', 16, 1); RETURN; END
IF NOT EXISTS (SELECT 1 FROM tCharacter WHERE sID = N'$(TakenName)' AND bDeleted = 0 AND nCharNo NOT IN (@dash, @b))
BEGIN RAISERROR('the "name in use" $(TakenName) of step 2 is not an existing character (give -TakenName <another character>)', 16, 1); RETURN; END
IF EXISTS (SELECT 1 FROM tCharacter WHERE sID IN (N'$(DashName)', N'$(FreeName)', N'$(TutChar)'))
BEGIN RAISERROR('one of the names $(DashName) / $(FreeName) / $(TutChar) is already taken (also by a deleted row): pick others', 16, 1); RETURN; END
IF EXISTS (SELECT 1 FROM tCharacterChangeID WHERE bFlag = 0 AND nCharNo = @dash)
BEGIN RAISERROR('$(DashChar) has an open rename right (tCharacterChangeID bFlag 0): the client would take mode 3, not the plain rename', 16, 1); RETURN; END

-- the two characters must sit on the two named accounts (skipped when the account DB has another name)
IF DB_ID(N'$(AccountDb)') IS NOT NULL
BEGIN
    DECLARE @ua nvarchar(40), @ub nvarchar(40);
    DECLARE @ua_no int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @dash);
    DECLARE @ub_no int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @b);
    EXEC sp_executesql N'SELECT @x = sUserID FROM [$(AccountDb)].dbo.tUser WHERE nUserNo = @n',
         N'@n int, @x nvarchar(40) OUTPUT', @n = @ua_no, @x = @ua OUTPUT;
    EXEC sp_executesql N'SELECT @x = sUserID FROM [$(AccountDb)].dbo.tUser WHERE nUserNo = @n',
         N'@n int, @x nvarchar(40) OUTPUT', @n = @ub_no, @x = @ub OUTPUT;
    IF ISNULL(@ua, N'') <> N'admin' OR ISNULL(@ub, N'') <> N'testaccountB'
    BEGIN RAISERROR('$(DashChar) must be on account admin, $(CharB) on testaccountB', 16, 1); RETURN; END
    -- a free slot on admin for the step-1 character
    DECLARE @n_admin int = (SELECT COUNT(*) FROM tCharacter WHERE nUserNo = @ua_no AND bDeleted = 0);
    PRINT CONCAT('admin has ', @n_admin, ' character(s): one slot must be free for $(TutChar) (step 1)');
END
ELSE PRINT 'account DB $(AccountDb) not found: account check skipped (-AccountDb <name>)';

CREATE TABLE dbo.X52_save (what varchar(8) NOT NULL, nCharNo int NOT NULL, nUserNo int NOT NULL, sID nvarchar(40) NOT NULL,
                           nAdminLevel int NOT NULL, sLoginZone nvarchar(40) NULL, nLoginZoneX int NULL, nLoginZoneY int NULL,
                           saved datetime NOT NULL DEFAULT GETDATE());
INSERT dbo.X52_save (what, nCharNo, nUserNo, sID, nAdminLevel, sLoginZone, nLoginZoneX, nLoginZoneY)
SELECT CASE nCharNo WHEN @dash THEN 'dash' ELSE 'b' END, nCharNo, nUserNo, sID, nAdminLevel, sLoginZone, nLoginZoneX, nLoginZoneY
  FROM tCharacter WHERE nCharNo IN (@dash, @b);

BEGIN TRAN;
UPDATE tCharacter SET sID = N'$(DashName)', nAdminLevel = 100, sLoginZone = 'RouN', nLoginZoneX = 5874, nLoginZoneY = 6530
 WHERE nCharNo = @dash;
UPDATE tCharacter SET sLoginZone = 'RouN', nLoginZoneX = 5950, nLoginZoneY = 6530 WHERE nCharNo = @b;
-- tutorial done (nState 2, as 37b-prep.sql): the '-' character must NOT be in state 0 (P02-B33 would answer first)
IF OBJECT_ID('dbo.usp_Tutorial_setCharInfo') IS NOT NULL
BEGIN
    DECLARE @r int;
    DECLARE @nd int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @dash);
    DECLARE @nb int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @b);
    EXEC usp_Tutorial_setCharInfo @nd, @dash, 2, 0, @r OUTPUT;
    EXEC usp_Tutorial_setCharInfo @nb, @b, 2, 0, @r OUTPUT;
END
ELSE PRINT 'no usp_Tutorial_setCharInfo: start $(DashName) and $(CharB) once and skip the tutorial before the run';
COMMIT;
PRINT 'characters done: $(DashChar) -> $(DashName) (GM 100, RouN), $(CharB) at RouN (old values in dbo.X52_save)';

-- S20: the 2016 p_Char_Rename. sp_helpindex first: a unique index on sID decides step 2's duplicate case.
PRINT '---- sp_helpindex tCharacter (step 2: is an index on sID unique?)';
EXEC sp_helpindex N'dbo.tCharacter';
SELECT 'unique index on tCharacter.sID' AS check_name, i.name AS index_name, i.is_unique, i.is_primary_key
  FROM sys.indexes i JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
  JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
 WHERE i.object_id = OBJECT_ID('dbo.tCharacter') AND c.name = 'sID';
SELECT 'p_Char_Rename before S20' AS proc_name,
       CASE WHEN OBJECT_DEFINITION(OBJECT_ID('dbo.p_Char_Rename')) LIKE '%tCharacterChangeID%'
            THEN '2018 Fixes copy (renames only with an open tCharacterChangeID row)' ELSE 'already the plain UPDATE' END AS variant;
SELECT OBJECT_DEFINITION(OBJECT_ID(N'dbo.p_Char_Rename')) AS def INTO dbo.X07_save_20;
EXEC (N'ALTER PROCEDURE dbo.p_Char_Rename @nCharNo int, @sID nvarchar(40), @nRet int OUTPUT AS
SET NOCOUNT ON
UPDATE tCharacter SET sID = @sID WHERE nCharNo = @nCharNo
SET @nRet = @@ERROR');
SELECT 'p_Char_Rename after S20' AS proc_name,
       CASE WHEN OBJECT_DEFINITION(OBJECT_ID('dbo.p_Char_Rename')) LIKE '%tCharacterChangeID%'
            THEN 'STILL the 2018 copy: S20 failed' ELSE '2016: plain UPDATE, nRet = @@ERROR' END AS variant;

SELECT c.nCharNo, c.nUserNo, c.nSlotNo, c.sID, c.nAdminLevel, c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c WHERE c.nCharNo IN (@dash, @b);
SELECT name AS open_x_object FROM sys.objects WHERE name LIKE 'X0[0-9][_]%' OR name LIKE 'X[1-9][0-9][_]%';
