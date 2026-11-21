-- Scenario 39 preparation (capture-scenarios.md §3 "39"). Run by 39-server.ps1 prep, both accounts logged out
-- (clients at the login screen or closed). Turns two characters freshly created in the client into
--   $(CharA) (account "admin")        SharpShooter (class 14), level 40, exp 1 509 279 (level 40 starts at 1 389 279,
--                                     level 41 at 1 628 577: room for every death of the run), GM 100, 2 000 000 cen,
--                                     skills 4028 PowerShot09 "Power Shot [09]" (sets StaKnockBack, any weapon, step 5)
--                                     and 4500 Distant01 "Distant Shot [01]" (bow, 1 399 ms cast, 60 s cool-time, step 7)
--   $(CharB) (account "testaccountB") Guardian (class 10), level 40, GM 100, 2 000 000 cen,
--                                     skill 2030 Rebirth01 "Rebirth [01]" (sets StaRebirth on a friend, hammer, step 9)
-- puts both next to the guild NPC RouGuildBrom (RouN 6713,5495; World/NPC.txt) and marks their tutorial done.
-- Values from the 2016 data: ChrCommon.txt StatTable NextExp (level n starts at NextExp of n-1), ClassName.shn,
-- ActiveSkill.shn, UseClassTypeInfo.shn (PowerShot09 / Distant01: UseClass 18 = SharpShooter only; Rebirth01: 11 =
-- Guardian only). The guild fee is 1 000 000 cen (p_Guild_Make2 nMakerPay, D04 §6). Level 40: SharpShooter max SP 800,
-- Guardian 922, above every skill cost used (261 / 520 / 490).
-- Only these two characters are changed; the guilds are founded in the client during the run. Safe to run twice.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
DECLARE @a int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(CharA)' AND bDeleted = 0);
DECLARE @b int = (SELECT nCharNo FROM tCharacter WHERE sID = N'$(CharB)' AND bDeleted = 0);
IF @a IS NULL OR @b IS NULL
BEGIN RAISERROR('$(CharA) or $(CharB) not found: create them in the client first (A: Archer on admin, B: Cleric on testaccountB)', 16, 1); RETURN; END
DECLARE @ca tinyint = (SELECT nClass FROM tCharacterShape WHERE nCharNo = @a);
DECLARE @cb tinyint = (SELECT nClass FROM tCharacterShape WHERE nCharNo = @b);
IF @ca NOT BETWEEN 11 AND 15 OR @cb NOT BETWEEN 6 AND 10
BEGIN RAISERROR('$(CharA) must be an Archer (class 11-15) and $(CharB) a Cleric (class 6-10): delete and create again', 16, 1); RETURN; END

-- leftovers of an earlier run: the guild names must be free (0xC99 otherwise) and neither character in a guild
IF EXISTS (SELECT 1 FROM tGuild WHERE sName IN (N'$(GuildA)', N'$(GuildB)'))
BEGIN RAISERROR('guild $(GuildA) or $(GuildB) exists from an earlier run: run 39-server.ps1 cleanup first', 16, 1); RETURN; END
IF EXISTS (SELECT 1 FROM tGuildMember WHERE nCharNo IN (@a, @b))
BEGIN RAISERROR('$(CharA) or $(CharB) is in a guild already: delete and create them again', 16, 1); RETURN; END

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
   SET nAdminLevel = 100, nLevel = 40, nExp = 1509279, nMoney = 2000000, nPKCount = 0,
       sLoginZone = 'RouN', nLoginZoneX = 6650, nLoginZoneY = 5450
 WHERE nCharNo = @a;
UPDATE tCharacterShape SET nClass = 14 WHERE nCharNo = @a;
UPDATE tCharacter
   SET nAdminLevel = 100, nLevel = 40, nExp = 1389279, nMoney = 2000000, nPKCount = 0,
       sLoginZone = 'RouN', nLoginZoneX = 6700, nLoginZoneY = 5420
 WHERE nCharNo = @b;
UPDATE tCharacterShape SET nClass = 10 WHERE nCharNo = @b;

-- skills as the Character server writes them at character creation (p_Skill_Set, all values 0; D02 §3)
DECLARE @r int;
EXEC p_Skill_Set @a, 4028, 0, 0, 0, 0, 0, 0, 0, 0, @r OUTPUT;
EXEC p_Skill_Set @a, 4500, 0, 0, 0, 0, 0, 0, 0, 0, @r OUTPUT;
EXEC p_Skill_Set @b, 2030, 0, 0, 0, 0, 0, 0, 0, 0, @r OUTPUT;

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
PRINT 'prep done: $(CharA) SharpShooter 40 GM, $(CharB) Guardian 40 GM, 2 000 000 cen each, both at the guild NPC in RouN';

SELECT c.nCharNo, c.nUserNo, c.sID, c.nLevel, c.nExp, s.nClass, c.nAdminLevel, c.nMoney, c.nPKCount,
       c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c JOIN tCharacterShape s ON s.nCharNo = c.nCharNo
 WHERE c.nCharNo IN (@a, @b);
SELECT nCharNo, nSkillNo FROM tSkill WHERE nCharNo IN (@a, @b) AND nSkillNo IN (4028, 4500, 2030) ORDER BY nCharNo, nSkillNo;
