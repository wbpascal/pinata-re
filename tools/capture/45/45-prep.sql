-- Scenario 45 preparation (capture-scenarios.md §3 "45"). Run by 45-server.ps1 prep, both accounts logged out
-- (clients at the login screen or closed). Turns two characters freshly created in the client into
--   $(CharA) (account "admin")        any class, level 40 (above ChrCommon.txt ShoutLevel 5), GM 100
--   $(CharB) (account "testaccountB") SharpShooter (class 14), level 40, GM 100 (for &mb / &fullpoint / &makeitem),
--                                     skill 4500 Distant01 "Distant Shot [01]" (bow, 1 399 ms cast: step 7)
-- puts both on RouN 400 apart (in sight, MapInfo.Sight 1600; A at the Slime / MushRoom group of s14, 6443,9850) and
-- marks their tutorial done. Values from the 2016 data as in 39-prep.sql (ChrCommon.txt NextExp, ActiveSkill.shn,
-- UseClassTypeInfo.shn: Distant01 UseClass 18 = SharpShooter only; SharpShooter 40 max SP 800 > cost 520).
-- Only these two characters are changed. Safe to run twice.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
DECLARE @a int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(CharA)' AND bDeleted = 0);
DECLARE @b int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(CharB)' AND bDeleted = 0);
IF @a IS NULL OR @b IS NULL
BEGIN RAISERROR('$(CharA) or $(CharB) not found: create them in the client first (A: any class on admin, B: Archer on testaccountB)', 16, 1); RETURN; END
DECLARE @cb tinyint = (SELECT nClass FROM tCharacterShape WHERE nCharNo = @b);
IF @cb NOT BETWEEN 11 AND 15
BEGIN RAISERROR('$(CharB) must be an Archer (class 11-15): delete and create again', 16, 1); RETURN; END

-- the two characters must sit on the two named accounts (skipped when the account DB has another name)
IF DB_ID(N'$(AccountDb)') IS NOT NULL
BEGIN
    DECLARE @ua nvarchar(40), @ub nvarchar(40);
    DECLARE @ua_no int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @a);
    DECLARE @ub_no int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @b);
    EXEC sp_executesql N'SELECT @x = sUserID FROM [$(AccountDb)].dbo.tUser WHERE nUserNo = @n',
         N'@n int, @x nvarchar(40) OUTPUT', @n = @ua_no, @x = @ua OUTPUT;
    EXEC sp_executesql N'SELECT @x = sUserID FROM [$(AccountDb)].dbo.tUser WHERE nUserNo = @n',
         N'@n int, @x nvarchar(40) OUTPUT', @n = @ub_no, @x = @ub OUTPUT;
    IF ISNULL(@ua, N'') <> N'admin' OR ISNULL(@ub, N'') <> N'testaccountB'
    BEGIN RAISERROR('$(CharA) must be on account admin, $(CharB) on testaccountB', 16, 1); RETURN; END
END
ELSE PRINT 'account DB $(AccountDb) not found: account check skipped (-AccountDb <name>)';

BEGIN TRAN;
UPDATE tCharacter
   SET nAdminLevel = 100, nLevel = 40, nExp = 1389279, nPKCount = 0,
       sLoginZone = 'RouN', nLoginZoneX = 6443, nLoginZoneY = 9850
 WHERE nCharNo = @a;
UPDATE tCharacter
   SET nAdminLevel = 100, nLevel = 40, nExp = 1389279, nPKCount = 0,
       sLoginZone = 'RouN', nLoginZoneX = 6843, nLoginZoneY = 9850
 WHERE nCharNo = @b;
UPDATE tCharacterShape SET nClass = 14 WHERE nCharNo = @b;

-- skill as the Character server writes it at character creation (p_Skill_Set, all values 0; D02 §3)
DECLARE @r int;
EXEC p_Skill_Set @b, 4500, 0, 0, 0, 0, 0, 0, 0, 0, @r OUTPUT;

-- tutorial done (nState 2, as the "skip" path of 0x1112 writes it): the WM does not ask at the first login
IF OBJECT_ID('dbo.usp_Tutorial_setCharInfo') IS NOT NULL
BEGIN
    DECLARE @na int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @a);
    DECLARE @nb int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @b);
    EXEC usp_Tutorial_setCharInfo @na, @a, 2, 0, @r OUTPUT;
    EXEC usp_Tutorial_setCharInfo @nb, @b, 2, 0, @r OUTPUT;
END
ELSE PRINT 'no usp_Tutorial_setCharInfo in this DB: answer the tutorial question at the first login with "skip"';
COMMIT;
PRINT 'prep done: $(CharA) level 40 GM at RouN 6443,9850; $(CharB) SharpShooter 40 GM with Distant Shot [01] at RouN 6843,9850';

SELECT c.nCharNo, c.nUserNo, c.sID, c.nLevel, c.nExp, s.nClass, c.nAdminLevel,
       c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c JOIN tCharacterShape s ON s.nCharNo = c.nCharNo
 WHERE c.nCharNo IN (@a, @b);
SELECT nCharNo, nSkillNo FROM tSkill WHERE nCharNo = @b AND nSkillNo = 4500;
