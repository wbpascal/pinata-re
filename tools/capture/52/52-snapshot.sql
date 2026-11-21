-- Scenario 52: what the DB holds for both accounts (52-server.ps1 snapshot / prep / cleanup). Step 2 reads it: the
-- '-' character's name after each rename answer, and whether two characters share a name (no unique sID index).
SET NOCOUNT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
SELECT N'$(Label)' AS snapshot, CONVERT(varchar(12), GETDATE(), 114) AS db_time;

CREATE TABLE #u (nUserNo int PRIMARY KEY);
IF OBJECT_ID('dbo.X52_save') IS NOT NULL INSERT #u SELECT DISTINCT nUserNo FROM dbo.X52_save;
ELSE INSERT #u SELECT DISTINCT nUserNo FROM tCharacter
            WHERE sID IN (N'$(DashChar)', N'$(DashName)', N'$(FreeName)', N'$(CharB)', N'$(TutChar)') AND bDeleted = 0;

SELECT c.nUserNo, c.nCharNo, c.nSlotNo, c.sID, c.bDeleted, c.nLevel, c.nAdminLevel, c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c JOIN #u ON #u.nUserNo = c.nUserNo
 ORDER BY c.nUserNo, c.bDeleted, c.nSlotNo;

-- names held by more than one live character (step 2 without a unique index)
SELECT sID AS duplicate_name, COUNT(*) AS n FROM tCharacter WHERE bDeleted = 0 GROUP BY sID HAVING COUNT(*) > 1;

-- tutorial state (step 1: 0 for the new character before the skip, 2 after it)
IF OBJECT_ID('dbo.tTutorialInfo') IS NOT NULL AND COL_LENGTH('dbo.tTutorialInfo', 'nCharNo') IS NOT NULL
    EXEC (N'SELECT t.* FROM dbo.tTutorialInfo t JOIN dbo.tCharacter c ON c.nCharNo = t.nCharNo
             WHERE c.nUserNo IN (SELECT nUserNo FROM #u) ORDER BY t.nCharNo');
ELSE PRINT 'no dbo.tTutorialInfo with nCharNo: tutorial state not shown';

SELECT 'p_Char_Rename' AS proc_name,
       CASE WHEN OBJECT_DEFINITION(OBJECT_ID('dbo.p_Char_Rename')) LIKE '%tCharacterChangeID%'
            THEN '2018 Fixes copy' ELSE '2016 plain UPDATE (S20)' END AS variant;
IF OBJECT_ID('dbo.X52_save') IS NOT NULL SELECT * FROM dbo.X52_save;
