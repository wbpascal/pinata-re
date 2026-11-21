<#
  Scenario 39 (docs/plan/capture-scenarios.md §3 "39"): combat extras: death penalty, PK, revive item, knock-back,
  rebirth, guild war kill, boss announcement. Everything that runs on the server, one action per call. Copy
  tools\capture\39 to the server (e.g. C:\FiestaServer\capture\39) and run it there in an ELEVATED PowerShell (dumpcap).
  Needs sqlcmd; Windows authentication to -Instance (default .\SQLExpress, insecure connection: sqlcmd -C).

  .\39-server.ps1 prep            [both accounts logged out]  X39A / X39B -> SharpShooter 40 / Guardian 40, GM 100,
                                  2 000 000 cen each (guild fee 1 000 000), A's exp in the middle of level 40, skills
                                  (A: Power Shot [09], Distant Shot [01]; B: Rebirth [01]), tutorial done, both next to
                                  the guild NPC in RouN; DB snapshot "after prep"
  .\39-server.ps1 capture-start   opens dumpcap in its own window (loopback + LAN, filter of capture-guide.md);
                                  stop it with Ctrl+C in THAT window. -NoLan when the clients run on the server PC
  .\39-server.ps1 snapshot -Label <text>   level, exp, PK count, HP, position of both + the two test guilds -> out\<Name>-db.txt
  .\39-server.ps1 status          client links, X39 guild leftovers
  .\39-server.ps1 cleanup         [both accounts logged out]  snapshot, then deletes the guilds X39GuildA / X39GuildB
                                  (rows only: the WM keeps them in memory until its next restart) and X39A / X39B
                                  (p_Char_Delete); with -Dest <folder> it ends with collect
  .\39-server.ps1 collect -Dest <folder>   copies out\<Name>.pcapng, -prep.txt and -db.txt into <folder> (the notes' folder)

  Defaults: -CharA X39A, -CharB X39B, -CharDb World00_Character, -AccountDb Account (only used for a check).
#>
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateSet('prep', 'capture-start', 'snapshot', 'status', 'cleanup', 'collect')]
    [string]$Action,
    [string]$Instance = '.\SQLExpress',
    [string]$CharDb = 'World00_Character',
    [string]$AccountDb = 'Account',
    [string]$CharA = 'X39A',
    [string]$CharB = 'X39B',
    [string]$GuildA = 'X39GuildA',
    [string]$GuildB = 'X39GuildB',
    [string]$Label = 'snapshot',
    [string]$Name = '26_11_16_39_death-pk-revive-knockback-guildwar',
    [string]$ServerRoot = 'C:\FiestaServer\2016',
    [string]$Dumpcap = 'C:\Program Files\Wireshark\dumpcap.exe',
    [string]$Dest,
    [switch]$NoLan
)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$out = Join-Path $here 'out'
New-Item -ItemType Directory -Force $out | Out-Null
$dbLog = Join-Path $out "$Name-db.txt"
foreach ($n in $CharA, $CharB, $GuildA, $GuildB) { if ($n -notmatch '^[A-Za-z0-9_]{1,16}$') { throw "bad name '$n'" } }

# WM / zone client ports from the install's ServerInfo.txt (type-20 rows), shipped values as the fallback
$WmClientPort = 9110; $ZonePorts = @(9210, 9212, 9214, 9216)
$si = Join-Path $ServerRoot '9Data\ServerInfo\ServerInfo.txt'
if (Test-Path -LiteralPath $si) {
    $rows = Get-Content -LiteralPath $si | Where-Object { $_ -match '^\s*SERVER_INFO\s' } | ForEach-Object {
        $f = ($_ -replace '^\s*SERVER_INFO\s+', '') -split ',' | ForEach-Object { $_.Trim().Trim('"') }
        if ($f.Count -ge 7) { [pscustomobject]@{ Name = $f[0]; Type = [int]$f[4]; Port = [int]$f[6] } }
    }
    $w20 = $rows | Where-Object { $_.Name -like 'PG_W*_WM' -and $_.Type -eq 20 } | Select-Object -First 1
    if ($w20) { $WmClientPort = $w20.Port }
    $zp = @($rows | Where-Object { $_.Name -like 'PG_W*_Z*' -and $_.Type -eq 20 } | ForEach-Object Port)
    if ($zp) { $ZonePorts = $zp }
} else { Write-Warning "$si not found (-ServerRoot): shipped ports used" }

function Stamp { (Get-Date).ToString('HH:mm:ss.fff') }
function Sql([string]$file, [hashtable]$vars, [string]$log) {
    $a = @('-S', $Instance, '-E', '-C', '-b', '-W', '-s', '|', '-i', (Join-Path $here $file),
           '-v', "CharDb=$CharDb", '-v', "CharA=$CharA", '-v', "CharB=$CharB", '-v', "AccountDb=$AccountDb",
           '-v', "GuildA=$GuildA", '-v', "GuildB=$GuildB")
    foreach ($k in $vars.Keys) { $a += @('-v', "$k=$($vars[$k])") }
    $o = & sqlcmd @a
    $code = $LASTEXITCODE
    $o | ForEach-Object { Write-Host $_ }
    if ($log) { "---- $(Stamp) $file" | Add-Content -LiteralPath $log -Encoding UTF8; $o | Add-Content -LiteralPath $log -Encoding UTF8 }
    if ($code) { throw "$file failed (sqlcmd exit $code)" }
}
function Collect([string]$dest) {
    if (-not $dest) { throw "collect needs -Dest <folder>: the folder of the notes file (re-data\captures of a checkout, a share or a USB stick)" }
    New-Item -ItemType Directory -Force $dest | Out-Null
    $missing = @()
    $files = [ordered]@{ (Join-Path $out "$Name.pcapng") = "$Name.pcapng"; (Join-Path $out "$Name-prep.txt") = "$Name-prep.txt"; $dbLog = "$Name-db.txt" }
    foreach ($src in $files.Keys) {
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $dest $files[$src]) -Force
            Write-Host "copied $src -> $(Join-Path $dest $files[$src])"
        } else { $missing += $src }
    }
    if ($missing) { Write-Warning ("missing, copy by hand if it exists elsewhere: " + ($missing -join ', ')) }
    else { Write-Host "all files of $Name are in $dest" }
}
function Snapshot([string]$label) { Sql '39-snapshot.sql' @{ Label = ($label -replace '[^\w\-]+', '_') } $dbLog }
function Warn-Online {
    $n = @(Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @($WmClientPort) + $ZonePorts }).Count
    if ($n) {
        Write-Warning "$n client link(s) to the WM / a zone are open: log both accounts out to the login screen first,"
        Write-Warning 'or the zone writes its own copy of the characters back over what this changes.'
        if ((Read-Host 'Go on anyway? (y/N)') -ne 'y') { throw 'stopped' }
    }
}

switch ($Action) {
    'prep' {
        Warn-Online
        Sql '39-prep.sql' @{} (Join-Path $out "$Name-prep.txt")
        Snapshot 'after prep'
        Write-Host "Next: .\39-server.ps1 capture-start, then log in A ($CharA on admin) and B ($CharB on testaccountB)."
    }
    'capture-start' {
        if (-not (Test-Path -LiteralPath $Dumpcap)) { throw "dumpcap not found at $Dumpcap (-Dumpcap <path>)" }
        $ifs = @('\Device\NPF_Loopback')
        if (-not $NoLan) {
            $r = Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric, InterfaceMetric | Select-Object -First 1
            $ad = Get-NetAdapter -InterfaceIndex $r.ifIndex
            $ifs += "\Device\NPF_$($ad.InterfaceGuid)"
            Write-Host "LAN interface: $($ad.Name) ($($ad.InterfaceDescription))"
        }
        $filter = 'tcp portrange 9000-9011 or tcp portrange 9110-9111 or tcp portrange 9210-9221 or tcp port 9311 or tcp port 9411 or tcp port 9511'
        $file = Join-Path $out "$Name.pcapng"
        if (Test-Path -LiteralPath $file) { throw "$file exists: move it away first" }
        $argline = "-f `"$filter`" " + (($ifs | ForEach-Object { "-i `"$_`"" }) -join ' ') + " -w `"$file`""
        Start-Process -FilePath $Dumpcap -ArgumentList $argline
        Write-Host "$(Stamp) dumpcap started -> $file"
        Write-Host 'Check its window shows "Capturing on ..." for both interfaces. Stop it with Ctrl+C in that window.'
    }
    'snapshot' { Snapshot $Label }
    'status' {
        Write-Host 'client links:'
        Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
            Where-Object { $_.LocalPort -in @($WmClientPort) + $ZonePorts } |
            ForEach-Object { Write-Host ("  {0,-5} {1}:{2}" -f $_.LocalPort, $_.RemoteAddress, $_.RemotePort) }
        & sqlcmd -S $Instance -E -C -b -W -Q "SET NOCOUNT ON; USE $CharDb; SELECT nNo, sName, nType FROM tGuild WHERE sName IN (N'$GuildA', N'$GuildB'); SELECT nCharNo, sID, bDeleted FROM tCharacter WHERE sID IN (N'$CharA', N'$CharB');"
    }
    'cleanup' {
        Warn-Online
        Snapshot 'before cleanup'
        Sql '39-cleanup.sql' @{} $dbLog
        if ($Dest) { Collect $Dest } else { Write-Host "Next: .\39-server.ps1 collect -Dest <folder of $Name.md> (pcapng, -prep.txt and -db.txt)" }
    }
    'collect' { Collect $Dest }
}
