-- Scenario 39 clean-up, run by 39-server.ps1 cleanup with both accounts logged out.
--   1. removes the two test guilds $(GuildA) / $(GuildB) founded during the run: every row keyed by their guild number
--      in the tGuild* tables (tGuild and tGuildMember by nNo, the others by nGuildNo / nGuildID / nGuildNum when the
--      table has such a column; tGuildTournament* left alone). Log tables (tLog_*, GameLog DB) are kept.
--      The WM keeps both guilds (and a running war) in memory until its next restart; nothing reads them once their
--      masters are deleted. Restart the WM before running scenario 39 again or 18 / 19 with the same guild names.
--   2. deletes $(CharA) and $(CharB) the way the Character server does (p_Char_Delete: bDeleted 1, name "<name>~<date>#<n>").
-- Nothing else needs undoing: prep changed only these two characters. The &pvp flags the run set live in the zone's
-- memory only: the run's last steps turn them off in the client (39-end.txt), a zone restart clears them too.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 10000;
USE $(CharDb);

-- 1. the guilds
CREATE TABLE #g (nNo int PRIMARY KEY);
INSERT #g SELECT nNo FROM tGuild WHERE sName IN (N'$(GuildA)', N'$(GuildB)');
SELECT g.nNo, g.sName, g.nType, g.nWarEnemy, g.nWarWinCount, g.nWarLoseCount, g.nWarDrawCount AS removed_guild
  FROM tGuild g JOIN #g ON #g.nNo = g.nNo;

DECLARE @t sysname, @col sysname, @sql nvarchar(max), @n int;
DECLARE tc CURSOR LOCAL FAST_FORWARD FOR
    SELECT t.name,
           CASE WHEN t.name IN ('tGuild', 'tGuildMember') THEN 'nNo'
                ELSE (SELECT TOP 1 c.name FROM sys.columns c
                       WHERE c.object_id = t.object_id AND c.name IN ('nGuildNo', 'nGuildID', 'nGuildNum')
                       ORDER BY CASE c.name WHEN 'nGuildNo' THEN 1 WHEN 'nGuildID' THEN 2 ELSE 3 END) END
      FROM sys.tables t
     WHERE t.name LIKE 'tGuild%' AND t.name NOT LIKE 'tGuildTournament%'
     ORDER BY CASE t.name WHEN 'tGuild' THEN 2 ELSE 1 END, t.name;      -- tGuild last
BEGIN TRAN;
OPEN tc;
FETCH NEXT FROM tc INTO @t, @col;
WHILE @@FETCH_STATUS = 0
BEGIN
    IF @col IS NOT NULL
    BEGIN
        SET @sql = N'DELETE FROM ' + QUOTENAME(@t) + N' WHERE ' + QUOTENAME(@col) + N' IN (SELECT nNo FROM #g); SET @n = @@ROWCOUNT;';
        EXEC sp_executesql @sql, N'@n int OUTPUT', @n = @n OUTPUT;
        IF @n > 0 PRINT CONCAT(@t, '.', @col, ': ', @n, ' row(s) deleted');
    END
    ELSE PRINT CONCAT(@t, ': no guild-number column, skipped');
    FETCH NEXT FROM tc INTO @t, @col;
END
CLOSE tc; DEALLOCATE tc;
COMMIT;

-- 2. the test characters
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
SELECT nNo, sName AS guild_still_there FROM tGuild WHERE sName IN (N'$(GuildA)', N'$(GuildB)');
