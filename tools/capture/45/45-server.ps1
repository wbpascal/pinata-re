<#
  Scenario 45 (docs/plan/capture-scenarios.md §3 "45"): second client in sight II: walk relay, sit, emote stop, shout
  out of sight, whisper to an unknown receiver, a mob's hits on a bystander's neighbour, cast abort, leaving sight.
  Everything that runs on the server, one action per call. Copy tools\capture\45 to the server (e.g.
  C:\FiestaServer\capture\45) and run it there in an ELEVATED PowerShell (dumpcap).
  Needs sqlcmd; Windows authentication to -Instance (default .\SQLExpress, insecure connection: sqlcmd -C).

  .\45-server.ps1 prep            [both accounts logged out]  X45A -> level 40 GM 100; X45B -> SharpShooter 40 GM 100
                                  with Distant Shot [01]; both tutorial done, both on RouN 400 apart (in sight);
                                  DB snapshot "after prep"; remembers the start time for the log copy of collect
  .\45-server.ps1 capture-start   opens dumpcap in its own window (loopback + LAN, filter of capture-guide.md);
                                  stop it with Ctrl+C in THAT window. -NoLan when the clients run on the server PC
  .\45-server.ps1 snapshot -Label <text>   level, class, HP, position of both -> out\<Name>-db.txt
  .\45-server.ps1 status          client links, the two characters
  .\45-server.ps1 cleanup         [both accounts logged out]  snapshot, then deletes X45A / X45B (p_Char_Delete);
                                  with -Dest <folder> it ends with collect
  .\45-server.ps1 collect -Dest <folder>   copies out\<Name>.pcapng, -prep.txt, -db.txt and every server log written
                                  since prep into <folder> (the notes' folder)

  Defaults: -CharA X45A, -CharB X45B, -CharDb World00_Character, -AccountDb Account (only used for a check).
#>
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateSet('prep', 'capture-start', 'snapshot', 'status', 'cleanup', 'collect')]
    [string]$Action,
    [string]$Instance = '.\SQLExpress',
    [string]$CharDb = 'World00_Character',
    [string]$AccountDb = 'Account',
    [string]$CharA = 'X45A',
    [string]$CharB = 'X45B',
    [string]$Label = 'snapshot',
    [string]$Name = '26_11_21_45_walk-sit-emote-stop-shout-whisper-cast-abort',
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
$startFile = Join-Path $out 'run-start.txt'
foreach ($n in $CharA, $CharB) { if ($n -notmatch '^[A-Za-z0-9_]{1,16}$') { throw "bad name '$n'" } }

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
           '-v', "CharDb=$CharDb", '-v', "CharA=$CharA", '-v', "CharB=$CharB", '-v', "AccountDb=$AccountDb")
    foreach ($k in $vars.Keys) { $a += @('-v', "$k=$($vars[$k])") }
    $o = & sqlcmd @a
    $code = $LASTEXITCODE
    $o | ForEach-Object { Write-Host $_ }
    if ($log) { "---- $(Stamp) $file" | Add-Content -LiteralPath $log -Encoding UTF8; $o | Add-Content -LiteralPath $log -Encoding UTF8 }
    if ($code) { throw "$file failed (sqlcmd exit $code)" }
}
function Snapshot([string]$label) { Sql '45-snapshot.sql' @{ Label = ($label -replace '[^\w\-]+', '_') } $dbLog }

# collect: the run's files next to its notes, plus every server log written since prep (as 52-server.ps1).
# Logs go to <Dest>\<Name>-logs\<path below -ServerRoot>.
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
    if (Test-Path -LiteralPath $startFile) {
        $since = [datetime]::Parse((Get-Content -LiteralPath $startFile -Raw).Trim())
        $skip = '\.(exe|dll|pdb|shn|mdf|ldf|ndf|bak|pcapng)$'
        $logs = @(Get-ChildItem -LiteralPath $ServerRoot -Recurse -File -ErrorAction SilentlyContinue |
                  Where-Object { $_.LastWriteTime -ge $since -and $_.Name -notmatch $skip -and $_.Length -le 200MB -and
                                 $_.FullName -notlike (Join-Path $ServerRoot '9Data') + '\*' })
        $ldir = Join-Path $dest "$Name-logs"
        foreach ($l in $logs) {
            $rel = $l.FullName.Substring($ServerRoot.TrimEnd('\').Length + 1)
            $to = Join-Path $ldir $rel
            New-Item -ItemType Directory -Force (Split-Path $to) | Out-Null
            try { Copy-Item -LiteralPath $l.FullName -Destination $to -Force; Write-Host "log  $rel" }
            catch { Write-Warning "could not copy $($l.FullName) (locked?): copy it by hand" }
        }
        if (-not $logs) { Write-Warning "no file under $ServerRoot was written since ${since}: find the WM / zone logs by hand" }
    } else { Write-Warning "no $startFile (prep not run from this folder): server logs not copied" }
    if ($missing) { Write-Warning ("missing, copy by hand if it exists elsewhere: " + ($missing -join ', ')) }
    else { Write-Host "all files of $Name are in $dest" }
}
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
        (Get-Date).ToString('o') | Set-Content -LiteralPath $startFile -Encoding UTF8
        Sql '45-prep.sql' @{} (Join-Path $out "$Name-prep.txt")
        Snapshot 'after prep'
        Write-Host "Next: .\45-server.ps1 capture-start, then log in A ($CharA on admin) and B ($CharB on testaccountB)."
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
        & sqlcmd -S $Instance -E -C -b -W -Q "SET NOCOUNT ON; USE $CharDb; SELECT nCharNo, sID, bDeleted, nLevel, nAdminLevel, sLoginZone FROM tCharacter WHERE sID IN (N'$CharA', N'$CharB');"
    }
    'cleanup' {
        Warn-Online
        Snapshot 'before cleanup'
        Sql '45-cleanup.sql' @{} $dbLog
        if ($Dest) { Collect $Dest } else { Write-Host "Next: .\45-server.ps1 collect -Dest <folder of $Name.md> (pcapng, -prep.txt, -db.txt, server logs)" }
    }
    'collect' { Collect $Dest }
}
