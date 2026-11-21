-- Scenario 52 steps 3b / 4: puts $(CharB) on Forest of Mist (RouVal01, zone 1 = port 9212; TownPortal.shn row 1),
-- a map of ANOTHER zone process than A's RouN (zone 0). B must be at the login screen (kicked in step 3, or logged out).
SET NOCOUNT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
UPDATE tCharacter SET sLoginZone = 'RouVal01', nLoginZoneX = 13658, nLoginZoneY = 7812
 WHERE sID = N'$(CharB)' AND bDeleted = 0;
IF @@ROWCOUNT = 0 RAISERROR('character $(CharB) not found', 16, 1);
SELECT sID, sLoginZone, nLoginZoneX, nLoginZoneY FROM tCharacter WHERE sID = N'$(CharB)' AND bDeleted = 0;
