-- Scenario 45: what the DB holds for the two characters (45-server.ps1 snapshot / prep / cleanup). Scenario 45 has
-- no DB claims; the snapshots only record the state the run started from and ended with. HP and position of an
-- online character lag behind the zone (saved at logout and on the save timer): take the last one at the login screen.
SET NOCOUNT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
SELECT N'$(Label)' AS snapshot, CONVERT(varchar(12), GETDATE(), 114) AS db_time;
SELECT c.nCharNo, c.sID, c.bDeleted, c.nLevel, c.nExp, s.nClass, c.nAdminLevel, c.nMoney,
       c.nHP, c.nSP, c.sLoginZone, c.nLoginZoneX, c.nLoginZoneY
  FROM tCharacter c JOIN tCharacterShape s ON s.nCharNo = c.nCharNo
 WHERE c.sID IN (N'$(CharA)', N'$(CharB)') AND c.bDeleted = 0;
SELECT c.sID, k.nSkillNo
  FROM tSkill k JOIN tCharacter c ON c.nCharNo = k.nCharNo
 WHERE c.sID IN (N'$(CharA)', N'$(CharB)') AND c.bDeleted = 0
 ORDER BY c.sID, k.nSkillNo;
