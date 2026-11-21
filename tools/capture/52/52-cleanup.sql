-- Scenario 52 clean-up: undo 52-prep.sql and what the run changed. Both accounts at the login screen.
--   1. S20: p_Char_Rename back to the text saved in dbo.X07_save_20 (the 2018 Fixes copy of the test DB)
--   2. $(DashChar) gets its name, admin level and login point back; $(CharB) its login point (52-move-b.sql moved it)
--   3. $(TutChar) (created in step 1) is deleted the way the Character server does it (p_Char_Delete); $(CharB) too
--      when its name starts with X52 (created for this run)
-- The tutorial state 2 written for $(DashChar) / $(CharB) stays (as 37b). The &kickout of step 3 bans nobody in the DB.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);

-- 1. S20
IF OBJECT_ID('dbo.X07_save_20') IS NULL PRINT 'no dbo.X07_save_20: p_Char_Rename not touched';
ELSE
BEGIN
    DECLARE @d nvarchar(max) = (SELECT def FROM dbo.X07_save_20);
    DECLARE @p int = PATINDEX(N'%CREATE%PROC%p_Char_Rename%', @d);
    IF @d IS NULL OR @p = 0
    BEGIN RAISERROR('dbo.X07_save_20 holds no CREATE PROCEDURE text: restore p_Char_Rename by hand (_Database/Fixes/Free Name Change/p_Char_Rename.sql)', 16, 1); RETURN; END
    SET @d = STUFF(@d, @p, 6, N'ALTER');
    EXEC (@d);
    SELECT 'p_Char_Rename restored' AS proc_name,
           CASE WHEN OBJECT_DEFINITION(OBJECT_ID('dbo.p_Char_Rename')) LIKE '%tCharacterChangeID%'
                THEN '2018 Fixes copy (as before the run)' ELSE 'plain UPDATE (the saved text was this too)' END AS variant;
    DROP TABLE dbo.X07_save_20;
END

-- 2. the two characters
IF OBJECT_ID('dbo.X52_save') IS NULL PRINT 'no dbo.X52_save: no character to restore';
ELSE
BEGIN
    IF EXISTS (SELECT 1 FROM tCharacter c JOIN dbo.X52_save s ON c.sID = s.sID AND c.nCharNo <> s.nCharNo WHERE c.bDeleted = 0)
    BEGIN RAISERROR('an old name is held by another character: rename or delete that one first', 16, 1); RETURN; END
    BEGIN TRAN;
    UPDATE c SET sID = s.sID, nAdminLevel = s.nAdminLevel,
                 sLoginZone = s.sLoginZone, nLoginZoneX = s.nLoginZoneX, nLoginZoneY = s.nLoginZoneY
      FROM tCharacter c JOIN dbo.X52_save s ON s.nCharNo = c.nCharNo;
    PRINT CONCAT('characters restored: ', @@ROWCOUNT);
    COMMIT;
END

-- 3. the characters created for the run
DECLARE @c int, @s nvarchar(40), @r int;
DECLARE cc CURSOR LOCAL FAST_FORWARD FOR
    SELECT nCharNo, sID FROM tCharacter
     WHERE bDeleted = 0 AND (sID = N'$(TutChar)' OR (sID = N'$(CharB)' AND N'$(CharB)' LIKE N'X52%'));
OPEN cc;
FETCH NEXT FROM cc INTO @c, @s;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @r = 4;
    EXEC p_Char_Delete @c, @r OUTPUT;
    PRINT CONCAT(@s, ' (', @c, '): p_Char_Delete returned ', @r, ' (0 = deleted)');
    FETCH NEXT FROM cc INTO @c, @s;
END
CLOSE cc; DEALLOCATE cc;

IF OBJECT_ID('dbo.X52_save') IS NOT NULL
BEGIN
    SELECT c.nUserNo, c.nCharNo, c.nSlotNo, c.sID, c.bDeleted, c.nAdminLevel, c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
      FROM tCharacter c WHERE c.nUserNo IN (SELECT nUserNo FROM dbo.X52_save) ORDER BY c.nUserNo, c.bDeleted, c.nSlotNo;
    DROP TABLE dbo.X52_save;
END
SELECT sID AS duplicate_name, COUNT(*) AS n FROM tCharacter WHERE bDeleted = 0 GROUP BY sID HAVING COUNT(*) > 1;
SELECT name AS open_x_object FROM sys.objects WHERE name LIKE 'X0[0-9][_]%' OR name LIKE 'X[1-9][0-9][_]%';
