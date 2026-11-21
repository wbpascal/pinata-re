<#
  Scenario 52 (docs/plan/capture-scenarios.md §3 "52"): character select and session II: the stale tutorial copy
  (P02-B33), the 2016 p_Char_Rename (S20), &kickout with a real user number, the SHN checksum refusal.
  Everything that runs on the server, one action per call. Copy tools\capture\52 to the server (e.g.
  C:\FiestaServer\capture\52) and run it there in an ELEVATED PowerShell (dumpcap, killing / starting a zone).
  Needs sqlcmd; Windows authentication to -Instance (default .\SQLExpress, insecure connection: sqlcmd -C).

  .\52-server.ps1 prep            [both accounts at the login screen]  -DashChar -> -DashName (with '-', GM 100, RouN),
                                  -CharB to RouN, both tutorial done; S20 (2016 p_Char_Rename); DB snapshot "after prep";
                                  remembers the start time for the log copy of collect
  .\52-server.ps1 capture-start   opens dumpcap in its own window (loopback + LAN, filter of capture-guide.md, the
                                  zone ring ports 9211-9217 included); stop it with Ctrl+C in THAT window. -NoLan when
                                  the clients run on the server PC
  .\52-server.ps1 snapshot -Label <text>   both accounts' characters, duplicate names, tutorial rows -> out\<Name>-db.txt
  .\52-server.ps1 move-b          [B at the login screen]  B's login point -> RouVal01 (zone 1, port 9212)
  .\52-server.ps1 shn-break       [nobody on zone 1]  keeps a copy of 9Data\Shine\View\MapViewInfo.shn, flips its last
                                  byte in place (the file stays decodable), restarts the zone on -ShnZonePort.
                                  -Mode append (one byte added) makes the zone fail to start: the cipher key depends on
                                  the length
  .\52-server.ps1 shn-restore     puts the copy back (hash checked) and restarts that zone again; starts it when it is
                                  not running (out\shn-zone.json, else the w00_Zone<nn> folder of the port in ServerInfo)
  .\52-server.ps1 status          zone ports / WM links, client links, open X52 / X07 objects, the SHN copy
  .\52-server.ps1 cleanup         [both accounts at the login screen]  snapshot, S20 restored, names / GM / login points
                                  back, -TutChar (and -CharB when it starts with X52) deleted; with -Dest it ends with collect
  .\52-server.ps1 collect -Dest <folder>   copies out\<Name>.pcapng, -prep.txt, -db.txt and every server log written
                                  since prep (WM, zones: the "TutorialMap Search Fail" and "DataFail" lines) into <folder>

  Defaults: -DashChar X37Del (renamed -DashName X52-Dash), -FreeName X52Ren, -TakenName Test1235, -TutChar X52Tut,
  -CharB X52B, -ShnZonePort 9212 (zone 1, hosts RouVal01).
#>
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateSet('prep', 'capture-start', 'snapshot', 'move-b', 'shn-break', 'shn-restore', 'status', 'cleanup', 'collect')]
    [string]$Action,
    [string]$Instance = '.\SQLExpress',
    [string]$CharDb = 'World00_Character',
    [string]$AccountDb = 'Account',
    [string]$DashChar = 'X37Del',
    [string]$DashName = 'X52-Dash',
    [string]$FreeName = 'X52Ren',
    [string]$TakenName = 'Test1235',
    [string]$TutChar = 'X52Tut',
    [string]$CharB = 'X52B',
    [string]$Label = 'snapshot',
    [string]$Name = '26_11_21_52_stale-tutorial-rename-kickout-shn',
    [string]$ServerRoot = 'C:\FiestaServer\2016',
    [string]$ShnFile = '9Data\Shine\View\MapViewInfo.shn',
    [int]$ShnZonePort = 9212,
    [ValidateSet('append', 'row')]
    [string]$Mode = 'row',
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
$shnPath = Join-Path $ServerRoot $ShnFile
$shnCopy = Join-Path $out ((Split-Path $ShnFile -Leaf) + '.orig')
foreach ($n in $DashChar, $FreeName, $TakenName, $TutChar, $CharB) { if ($n -notmatch '^[A-Za-z0-9_]{1,16}$') { throw "bad character name '$n'" } }
if ($DashName -notmatch '^[A-Za-z0-9_\-]{1,16}$' -or $DashName -notmatch '-') { throw "-DashName must contain '-' (that is what makes the client ask for the rename)" }

# Ports from the install's ServerInfo.txt: zone client ports = type-20 rows of PG_W*_Z*, WM <- zone = type-6 row of
# PG_W*_WM, WM client port = its type-20 row. Shipped values are the fallback.
$ZonePorts = @(9210, 9212, 9214, 9216); $WmZonePort = 9111; $WmClientPort = 9110
$si = Join-Path $ServerRoot '9Data\ServerInfo\ServerInfo.txt'
if (Test-Path -LiteralPath $si) {
    $rows = Get-Content -LiteralPath $si | Where-Object { $_ -match '^\s*SERVER_INFO\s' } | ForEach-Object {
        $f = ($_ -replace '^\s*SERVER_INFO\s+', '') -split ',' | ForEach-Object { $_.Trim().Trim('"') }
        if ($f.Count -ge 7) { [pscustomobject]@{ Name = $f[0]; Type = [int]$f[4]; Port = [int]$f[6] } }
    }
    $zp = @($rows | Where-Object { $_.Name -like 'PG_W*_Z*' -and $_.Type -eq 20 } | ForEach-Object Port)
    if ($zp) { $ZonePorts = $zp }
    $w6 = $rows | Where-Object { $_.Name -like 'PG_W*_WM' -and $_.Type -eq 6 } | Select-Object -First 1
    if ($w6) { $WmZonePort = $w6.Port }
    $w20 = $rows | Where-Object { $_.Name -like 'PG_W*_WM' -and $_.Type -eq 20 } | Select-Object -First 1
    if ($w20) { $WmClientPort = $w20.Port }
} else { Write-Warning "$si not found (-ServerRoot): shipped ports used" }

function Stamp { (Get-Date).ToString('HH:mm:ss.fff') }
function Sql([string]$file, [hashtable]$vars, [string]$log) {
    $a = @('-S', $Instance, '-E', '-C', '-b', '-W', '-s', '|', '-i', (Join-Path $here $file),
           '-v', "CharDb=$CharDb", '-v', "AccountDb=$AccountDb", '-v', "DashChar=$DashChar", '-v', "DashName=$DashName",
           '-v', "FreeName=$FreeName", '-v', "TakenName=$TakenName", '-v', "TutChar=$TutChar", '-v', "CharB=$CharB")
    foreach ($k in $vars.Keys) { $a += @('-v', "$k=$($vars[$k])") }
    $o = & sqlcmd @a
    $code = $LASTEXITCODE
    $o | ForEach-Object { Write-Host $_ }
    if ($log) { "---- $(Stamp) $file" | Add-Content -LiteralPath $log -Encoding UTF8; $o | Add-Content -LiteralPath $log -Encoding UTF8 }
    if ($code) { throw "$file failed (sqlcmd exit $code)" }
}
function Snapshot([string]$label) { Sql '52-snapshot.sql' @{ Label = ($label -replace '[^\w\-]+', '_') } $dbLog }

# collect: the run's files next to its notes, plus every server log written since prep (step 1 asks for the WM log,
# step 4 for the zone's DataFail line). Logs go to <Dest>\<Name>-logs\<path below -ServerRoot>.
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
        $hits = @($logs | ForEach-Object { Join-Path $ldir $_.FullName.Substring($ServerRoot.TrimEnd('\').Length + 1) } |
                  Where-Object { Test-Path -LiteralPath $_ } |
                  Select-String -Pattern 'TutorialMap|DataFail|Checksum' -SimpleMatch:$false -ErrorAction SilentlyContinue)
        if ($hits) { Write-Host 'log lines of interest:'; $hits | Select-Object -First 30 | ForEach-Object { Write-Host "  $($_.Filename):$($_.LineNumber): $($_.Line.Trim())" } }
    } else { Write-Warning "no $startFile (prep not run from this folder): server logs not copied" }
    if ($missing) { Write-Warning ("missing, copy by hand if it exists elsewhere: " + ($missing -join ', ')) }
    else { Write-Host "all files of $Name are in $dest" }
}
function Client-Links { @(Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @($WmClientPort) + $ZonePorts }) }
function Warn-Online([string]$what) {
    $n = @(Client-Links).Count
    if ($n) {
        Write-Warning "$n client link(s) to the WM / a zone are open: $what"
        if ((Read-Host 'Go on anyway? (y/N)') -ne 'y') { throw 'stopped' }
    }
}

# --- the zone of -ShnZonePort ----------------------------------------------------------------------------------
# The zone of -ShnZonePort: from its listener when it runs; else from out\shn-zone.json (written by shn-break before
# the restart); else from ServerInfo.txt: the PG_W00_Z<nn> row of that port -> <ServerRoot>\w00_Zone<nn>\*.exe.
# (A zone that failed to load a table never listens, so shn-restore must be able to start it from nothing.)
$zoneJson = Join-Path $out 'shn-zone.json'
function Zone-Proc {
    $l = Get-NetTCPConnection -State Listen -LocalPort $ShnZonePort -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($l) {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId=$($l.OwningProcess)"
        $a0 = ''; if ($p.CommandLine) { $a0 = ($p.CommandLine -replace '^\s*("[^"]*"|\S+)\s*', '') }
        $svc = Get-CimInstance Win32_Service | Where-Object { $_.ProcessId -eq $l.OwningProcess } | Select-Object -First 1
        $z = [pscustomobject]@{ Pid = $l.OwningProcess; Exe = $p.ExecutablePath; Dir = (Split-Path $p.ExecutablePath); Args = $a0
                                Service = $(if ($svc) { $svc.Name } else { '' }) }
        $z | ConvertTo-Json | Set-Content -LiteralPath $zoneJson -Encoding UTF8
        return $z
    }
    if (Test-Path -LiteralPath $zoneJson) {
        $z = Get-Content -LiteralPath $zoneJson -Raw | ConvertFrom-Json
        Write-Host "no zone listens on ${ShnZonePort}: using $zoneJson ($($z.Exe))"
    } else {
        $row = $rows | Where-Object { $_.Name -like 'PG_W*_Z*' -and $_.Type -eq 20 -and $_.Port -eq $ShnZonePort } | Select-Object -First 1
        if (-not $row -or $row.Name -notmatch '_Z(\d+)$') { throw "no zone listens on $ShnZonePort and ServerInfo.txt has no zone row for it: start the zone by hand" }
        $dir = Join-Path $ServerRoot ("w00_Zone{0}" -f $Matches[1])
        $exe = Get-ChildItem -LiteralPath $dir -Filter '*Zone*.exe' -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $exe) { throw "no zone listens on $ShnZonePort and no *Zone*.exe in ${dir}: start the zone by hand" }
        $svc = Get-CimInstance Win32_Service | Where-Object { $_.PathName -like "*$($exe.FullName)*" } | Select-Object -First 1
        $z = [pscustomobject]@{ Pid = 0; Exe = $exe.FullName; Dir = $dir; Args = ''; Service = $(if ($svc) { $svc.Name } else { '' }) }
        Write-Host "no zone listens on ${ShnZonePort}: found $($z.Exe) from ServerInfo ($($row.Name))$(if ($z.Service) { ", service $($z.Service)" })"
    }
    # a zone that failed at start may still sit there (error box, ShineExit): find it by its exe
    $left = @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $z.Exe })
    $z.Pid = $(if ($left) { [int]$left[0].ProcessId } else { 0 })
    $z
}
function Restart-Zone {
    $on = @(Get-NetTCPConnection -State Established -LocalPort $ShnZonePort -ErrorAction SilentlyContinue)
    if ($on) {
        Write-Warning "$($on.Count) client(s) on zone port ${ShnZonePort}: they lose the zone. Log B out first."
        if ((Read-Host 'Restart anyway? (y/N)') -ne 'y') { throw 'stopped' }
    }
    $z = Zone-Proc
    if ($z.Pid) {
        Write-Host ("{0} stopping zone pid {1} {2} (port {3})" -f (Stamp), $z.Pid, $z.Exe, $ShnZonePort)
        if ($z.Service) { Stop-Service -Name $z.Service -Force } else { Stop-Process -Id $z.Pid -Force }
        Wait-Process -Id $z.Pid -Timeout 30 -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5                            # let the WM see the link drop before the zone comes back
    } else { Write-Host "$(Stamp) zone not running: starting it" }
    if ($z.Service) { Start-Service -Name $z.Service; Write-Host ("{0} service {1} started" -f (Stamp), $z.Service) }
    else {
        $sp = @{ FilePath = $z.Exe; WorkingDirectory = $z.Dir }
        if ($z.Args) { $sp.ArgumentList = $z.Args }
        Start-Process @sp
        Write-Host ("{0} started {1} {2}" -f (Stamp), $z.Exe, $z.Args)
    }
    $deadline = (Get-Date).AddSeconds(300)
    while ((Get-Date) -lt $deadline) {
        $l = Get-NetTCPConnection -State Listen -LocalPort $ShnZonePort -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($l) {
            $wm = Get-NetTCPConnection -State Established -OwningProcess $l.OwningProcess -RemotePort $WmZonePort -ErrorAction SilentlyContinue
            if ($wm) { Write-Host ("{0} READY: zone pid {1} listens on {2} and is linked to the WM." -f (Stamp), $l.OwningProcess, $ShnZonePort); return }
        }
        Start-Sleep -Seconds 2
    }
    Write-Warning 'the zone did not come back within 300 s: check its console / log, start it by hand, then run status'
}
function Md5([string]$p) { (Get-FileHash -LiteralPath $p -Algorithm MD5).Hash }

switch ($Action) {
    'prep' {
        Warn-Online 'log both accounts out to the login screen first (the WM keeps the avatar list, the zone writes characters back).'
        (Get-Date).ToString('o') | Set-Content -LiteralPath $startFile -Encoding UTF8
        Sql '52-prep.sql' @{} (Join-Path $out "$Name-prep.txt")
        Snapshot 'after prep'
        Write-Host "Next: .\52-server.ps1 capture-start, then step 1 on admin (create $TutChar in the client)."
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
        # 9210-9221 holds the zone client ports, the zone ring ports (type 8: 9211/9213/9215/9217) and the WM links
        $filter = 'tcp portrange 9000-9011 or tcp portrange 9110-9111 or tcp portrange 9210-9221 or tcp port 9311 or tcp port 9411 or tcp port 9511'
        $file = Join-Path $out "$Name.pcapng"
        if (Test-Path -LiteralPath $file) { throw "$file exists: move it away first" }
        $argline = "-f `"$filter`" " + (($ifs | ForEach-Object { "-i `"$_`"" }) -join ' ') + " -w `"$file`""
        Start-Process -FilePath $Dumpcap -ArgumentList $argline
        Write-Host "$(Stamp) dumpcap started -> $file"
        Write-Host 'Check its window shows "Capturing on ..." for both interfaces. Stop it with Ctrl+C in that window.'
    }
    'snapshot' { Snapshot $Label }
    'move-b' {
        Sql '52-move-b.sql' @{} $dbLog
        Write-Host "$(Stamp) $CharB now logs in on RouVal01 (zone port $ShnZonePort). Log B in."
    }
    'shn-break' {
        if (-not (Test-Path -LiteralPath $shnPath)) { throw "$shnPath not found (-ServerRoot / -ShnFile)" }
        if (Test-Path -LiteralPath $shnCopy) { throw "${shnCopy} exists: the table is already changed. Run shn-restore first." }
        Copy-Item -LiteralPath $shnPath -Destination $shnCopy
        $h0 = Md5 $shnPath
        # row (default): flip the file's last byte in place. The SHN cipher (shn.py) seeds its key with the body
        # length and rolls it from the end, so the byte decodes to a changed value and every other byte stays as it
        # was. In MapViewInfo it is the high byte of the last row's MWP_IsMove (KDCake: 1 -> 0x01000001); the zone
        # only hashes the View tables (Z01 §1 "checksum only"). append changes the length, hence the key of EVERY
        # byte: the zone cannot load the table and does not start (seen in the first run).
        if ($Mode -eq 'append') {
            $fs = [IO.File]::Open($shnPath, 'Append', 'Write')
            try { $fs.WriteByte(0) } finally { $fs.Close() }
        } else {
            $b = [IO.File]::ReadAllBytes($shnPath)
            $b[$b.Length - 1] = $b[$b.Length - 1] -bxor 1
            [IO.File]::WriteAllBytes($shnPath, $b)
        }
        $h1 = Md5 $shnPath
        "---- $(Stamp) shn-break $Mode $shnPath  md5 $h0 -> $h1" | Add-Content -LiteralPath $dbLog -Encoding UTF8
        Write-Host "$(Stamp) $ShnFile changed ($Mode): md5 $h0 -> $h1 (copy: $shnCopy)"
        Restart-Zone
        Write-Host "Now log B in (lands on RouVal01, zone port $ShnZonePort). Afterwards: .\52-server.ps1 shn-restore"
    }
    'shn-restore' {
        if (-not (Test-Path -LiteralPath $shnCopy)) { throw "no ${shnCopy}: nothing to restore" }
        Copy-Item -LiteralPath $shnCopy -Destination $shnPath -Force
        if ((Md5 $shnPath) -ne (Md5 $shnCopy)) { throw "restore failed: $shnPath differs from $shnCopy (copy it by hand)" }
        Remove-Item -LiteralPath $shnCopy
        "---- $(Stamp) shn-restore $shnPath  md5 $(Md5 $shnPath)" | Add-Content -LiteralPath $dbLog -Encoding UTF8
        Write-Host "$(Stamp) $ShnFile restored (md5 $(Md5 $shnPath))"
        Restart-Zone
    }
    'status' {
        foreach ($port in $ZonePorts) {
            $l = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $l) { Write-Host ("zone port {0}: NOT LISTENING" -f $port); continue }
            $wm = Get-NetTCPConnection -State Established -OwningProcess $l.OwningProcess -RemotePort $WmZonePort -ErrorAction SilentlyContinue
            Write-Host ("zone port {0}: pid {1}, WM link {2}" -f $port, $l.OwningProcess, $(if ($wm) { 'up' } else { 'DOWN' }))
        }
        Write-Host 'client links:'
        Client-Links | ForEach-Object { Write-Host ("  {0,-5} {1}:{2}  ({3})" -f $_.LocalPort, $_.RemoteAddress, $_.RemotePort, $(if ($_.LocalPort -eq $WmClientPort) { 'WM' } else { 'zone' })) }
        Write-Host ("SHN copy {0} -> {1}" -f $shnCopy, $(if (Test-Path -LiteralPath $shnCopy) { 'PRESENT (table still changed: run shn-restore)' } else { 'none' }))
        & sqlcmd -S $Instance -E -C -b -W -Q "SET NOCOUNT ON; USE $CharDb; SELECT name AS open_x_object FROM sys.objects WHERE name LIKE 'X52[_]%' OR name LIKE 'X07[_]%';"
    }
    'cleanup' {
        Warn-Online 'log both accounts out to the login screen first, or the WM keeps the run''s names.'
        if (Test-Path -LiteralPath $shnCopy) { Write-Warning "${shnCopy} still there: run shn-restore (the zone runs on a changed table)" }
        Snapshot 'before cleanup'
        Sql '52-cleanup.sql' @{} $dbLog
        if ($Dest) { Collect $Dest } else { Write-Host "Next: .\52-server.ps1 collect -Dest <folder of $Name.md>" }
    }
    'collect' { Collect $Dest }
}
