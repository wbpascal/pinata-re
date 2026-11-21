-- Scenario 39: what the DB holds for the two characters and the two test guilds (39-server.ps1 snapshot / prep / cleanup).
-- Exp, HP and position of an online character lag behind the zone (saved at logout and on the save timer); the PK count
-- is written by 0x4018 NC_CHARSAVE_PKCOUNT_CMD (p_Char_SavePKCount, D02). Take the last snapshot at the login screen.
-- Guilds: nType (must be non-zero for a war, W03 §3.2), the war result written at the war's end by 0x7468 (65 min after
-- the request: after this run unless the clients stay online that long).
SET NOCOUNT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
SELECT N'$(Label)' AS snapshot, CONVERT(varchar(12), GETDATE(), 114) AS db_time;
SELECT c.nCharNo, c.sID, c.bDeleted, c.nLevel, c.nExp, s.nClass, c.nAdminLevel, c.nMoney, c.nPKCount,
       c.nHP, c.nSP, c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c JOIN tCharacterShape s ON s.nCharNo = c.nCharNo
 WHERE c.sID IN (N'$(CharA)', N'$(CharB)') AND c.bDeleted = 0;

-- revive items left (JustRevival "Tear of Legel", item ID 30168) and the weapons
SELECT c.sID, i.nStorageType, i.nStorage, i.nItemKey, i.nItemID,
       (SELECT TOP 1 o.nOptionData FROM tItemOptions o
         WHERE o.nItemKey = i.nItemKey AND o.nOptionType IN (1, 2, 3) ORDER BY o.nOptionType) AS lot
  FROM tItem i JOIN tCharacter c ON c.nCharNo = i.nOwner
 WHERE c.sID IN (N'$(CharA)', N'$(CharB)') AND c.bDeleted = 0 AND i.nStorageType IN (8, 9)
 ORDER BY c.sID, i.nStorageType, i.nStorage;

SELECT g.nNo, g.sName, g.nType, g.nGrade, g.nFame, g.nMoney, g.nWarEnemy, g.dWarRequestDate, g.dWarStartDate, g.dWarEndDate,
       g.nWarWinCount, g.nWarLoseCount, g.nWarDrawCount, g.nDismissStatus
  FROM tGuild g WHERE g.sName IN (N'$(GuildA)', N'$(GuildB)');
SELECT m.nNo AS guildNo, c.sID, m.nGrade
  FROM tGuildMember m JOIN tCharacter c ON c.nCharNo = m.nCharNo
 WHERE m.nNo IN (SELECT nNo FROM tGuild WHERE sName IN (N'$(GuildA)', N'$(GuildB)'));
