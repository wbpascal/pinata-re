-- Scenario 45 clean-up, run by 45-server.ps1 cleanup with both accounts logged out.
-- Deletes $(CharA) and $(CharB) the way the Character server does (p_Char_Delete: bDeleted 1, name
-- "<name>~<date>#<n>", rows stay); their items (the Heavy Bow) and the skill go with them.
-- Nothing else needs undoing: prep changed only these two characters, the run changes no file. The mobs spawned
-- with &mb live in the zone's memory only. The game log rows (GameLog DB) are kept.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);
DECLARE @c int, @s nvarchar(40), @r int;
DECLARE cc CURSOR LOCAL FAST_FORWARD FOR
    SELECT nCharNo, sID FROM tCharacter WHERE sID IN (N'$(CharA)', N'$(CharB)') AND bDeleted = 0;
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

SELECT nCharNo, sID, bDeleted, dDeletedDate
  FROM tCharacter WHERE sID LIKE N'$(CharA)~%' OR sID LIKE N'$(CharB)~%' OR sID IN (N'$(CharA)', N'$(CharB)');
