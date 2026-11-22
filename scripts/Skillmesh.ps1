[CmdletBinding()]
param(
    [ValidateSet('Scan', 'Apply', 'Doctor', 'Link', 'Init')][string]$Mode = 'Scan',
    [ValidateSet('claude', 'kiro')][string[]]$Agent = @('claude', 'kiro'),
    [ValidateSet('both', 'all', 'agents', 'claude', 'kiro')][string]$Target = 'both',
    [string[]]$Name,
    [switch]$NoHash,
    [switch]$Watch
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$cfgPath = Join-Path $repo 'skillmesh.config.json'
$examplePath = Join-Path $repo 'skillmesh.config.example.json'

if ($Mode -eq 'Init') {
    if (Test-Path -LiteralPath $cfgPath) { 'skillmesh.config.json already exists; left unchanged' }
    else {
        Copy-Item -LiteralPath $examplePath -Destination $cfgPath
        'created skillmesh.config.json from the example; edit roots, targets, ignore and known_foreign, then run -Mode Doctor'
    }
    exit 0
}
if (Test-Path -LiteralPath $cfgPath) {
    $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
    $cfg.roots = @($cfg.roots | ForEach-Object { [Environment]::ExpandEnvironmentVariables($_) })
    foreach ($tp in $cfg.targets.PSObject.Properties) { $tp.Value = [Environment]::ExpandEnvironmentVariables($tp.Value) }
}
elseif ($Mode -ne 'Link') {
    Write-Error 'skillmesh.config.json is missing. Run -Mode Init to create it from skillmesh.config.example.json, then edit it.'
    exit 1
}

function Get-FullPath([string]$p) {
    return [IO.Path]::GetFullPath($p).TrimEnd('\')
}

function Get-SkillName([string]$dir) {
    $line = Get-Content -LiteralPath (Join-Path $dir 'SKILL.md') -TotalCount 15 |
        Where-Object { $_ -match '^name:\s*\S' } | Select-Object -First 1
    if ($line) { return ($line -replace '^name:\s*', '').Trim().Trim('"', "'") }
    return $null
}

function Find-Skills {
    $found = New-Object System.Collections.ArrayList
    foreach ($root in $cfg.roots) {
        $rootN = Get-FullPath $root
        $stack = New-Object System.Collections.Stack
        $stack.Push($rootN)
        while ($stack.Count -gt 0) {
            $dir = $stack.Pop()
            foreach ($d in Get-ChildItem -LiteralPath $dir -Directory -Force) {
                if ($d.Name.StartsWith('.') -or $d.Name -eq 'node_modules') { continue }
                if ($d.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                $rel = $d.FullName.Substring($rootN.Length + 1)
                if ($cfg.ignore -contains $rel) { continue }
                if (Test-Path -LiteralPath (Join-Path $d.FullName 'SKILL.md')) {
                    [void]$found.Add([pscustomobject]@{
                            Name = $d.Name
                            Source = $d.FullName
                            Rel = $rel
                            Depth = ($rel -split '\\').Count
                            FrontName = Get-SkillName $d.FullName
                        })
                }
                else { $stack.Push($d.FullName) }
            }
        }
    }
    return $found
}

# One winner per name (shallowest wins, D2); equal depth without an override is a conflict.
function Resolve-Skills($skills) {
    $winners = @{}
    $conflicts = @{}
    $shadowed = New-Object System.Collections.ArrayList
    foreach ($g in ($skills | Group-Object Name)) {
        $cands = @($g.Group | Sort-Object Depth, Rel)
        $pick = $null
        $ov = $cfg.overrides.PSObject.Properties[$g.Name]
        if ($ov) { $pick = $cands | Where-Object { $_.Rel -eq $ov.Value } | Select-Object -First 1 }
        elseif ($cands.Count -eq 1) { $pick = $cands[0] }
        elseif ($cands[0].Depth -lt $cands[1].Depth) { $pick = $cands[0] }
        if ($pick) {
            $winners[$g.Name] = $pick
            foreach ($c in $cands) { if ($c.Source -ne $pick.Source) { [void]$shadowed.Add($c) } }
        }
        else { $conflicts[$g.Name] = $cands }
    }
    return @{ Winners = $winners; Conflicts = $conflicts; Shadowed = $shadowed }
}

function Get-TreeMap([string]$p) {
    $base = (Get-FullPath $p).Length + 1
    $map = @{}
    Get-ChildItem -LiteralPath $p -Recurse -File -Force |
        Where-Object { $_.FullName -notmatch '\\\.git\\' } |
        ForEach-Object { $map[$_.FullName.Substring($base)] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    return $map
}

function Compare-Trees([string]$src, [string]$copy) {
    $a = Get-TreeMap $src
    $b = Get-TreeMap $copy
    $onlySrc = @($a.Keys | Where-Object { -not $b.ContainsKey($_) }).Count
    $onlyCopy = @($b.Keys | Where-Object { -not $a.ContainsKey($_) }).Count
    $changed = @($a.Keys | Where-Object { $b.ContainsKey($_) -and $a[$_] -ne $b[$_] }).Count
    if (($onlySrc + $onlyCopy + $changed) -eq 0) { return 'identical' }
    return "src-only $onlySrc, copy-only $onlyCopy, changed $changed"
}

function Get-Row($skill, $state, $detail, $action) {
    return [pscustomobject]@{ Skill = $skill; Target = $script:curTarget; State = $state; Action = $action; Detail = $detail }
}

function Scan-Target([string]$tname, [string]$tpath, $res) {
    $script:curTarget = $tname
    $rows = New-Object System.Collections.ArrayList
    if (-not (Test-Path -LiteralPath $tpath)) { throw "target missing: $tpath" }
    foreach ($n in ($res.Winners.Keys | Sort-Object)) {
        if ($Name -and ($Name -notcontains $n)) { continue }
        $src = $res.Winners[$n].Source
        $p = Join-Path $tpath $n
        if (-not (Test-Path -LiteralPath $p)) { [void]$rows.Add((Get-Row $n 'MISSING' $src 'link')); continue }
        $item = Get-Item -LiteralPath $p -Force
        if ($item.LinkType -eq 'Junction') {
            $cur = $item.Target | Select-Object -First 1
            if ($cur -and ((Get-FullPath $cur) -ieq (Get-FullPath $src))) { [void]$rows.Add((Get-Row $n 'OK' $src '-')) }
            elseif (-not $cur -or -not (Test-Path -LiteralPath $cur)) { [void]$rows.Add((Get-Row $n 'BROKEN' "was $cur" 'relink')) }
            else { [void]$rows.Add((Get-Row $n 'WRONG-TARGET' "points to $cur" 'relink')) }
        }
        elseif ($item.LinkType) { [void]$rows.Add((Get-Row $n 'WRONG-TARGET' "$($item.LinkType) -> $($item.Target)" 'relink')) }
        else {
            $d = if ($NoHash) { 'not compared' } else { Compare-Trees $src $p }
            [void]$rows.Add((Get-Row $n 'COPY' $d 'trash+link'))
        }
    }
    foreach ($n in ($res.Conflicts.Keys | Sort-Object)) {
        if ($Name -and ($Name -notcontains $n)) { continue }
        [void]$rows.Add((Get-Row $n 'CONFLICT' (($res.Conflicts[$n] | ForEach-Object { $_.Rel }) -join ' | ') 'none'))
    }
    $known = @($cfg.known_foreign)
    foreach ($e in (Get-ChildItem -LiteralPath $tpath -Force)) {
        if ($res.Winners.ContainsKey($e.Name) -or $res.Conflicts.ContainsKey($e.Name)) { continue }
        if ($Name -and ($Name -notcontains $e.Name)) { continue }
        $k = if ($known -contains $e.Name) { 'known' } else { 'NEW' }
        [void]$rows.Add((Get-Row $e.Name 'FOREIGN' $k 'none'))
    }
    return $rows
}

function Invoke-Fix($row, [string]$tpath, $res) {
    $p = Join-Path $tpath $row.Skill
    $src = $res.Winners[$row.Skill].Source
    switch ($row.State) {
        'COPY' {
            $trash = Join-Path $tpath $cfg.trash_dir
            if (-not (Test-Path -LiteralPath $trash)) { New-Item -ItemType Directory -Path $trash | Out-Null }
            Move-Item -LiteralPath $p -Destination (Join-Path $trash ("{0}-{1}" -f $row.Skill, (Get-Date -Format 'yyyyMMdd-HHmmss')))
        }
        { $_ -in 'WRONG-TARGET', 'BROKEN' } { [IO.Directory]::Delete($p, $false) }
    }
    New-Item -ItemType Junction -Path $p -Target $src | Out-Null
}

function Test-Doctor {
    $issues = New-Object System.Collections.ArrayList
    foreach ($t in $cfg.targets.PSObject.Properties) {
        if (-not (Test-Path -LiteralPath $t.Value)) { [void]$issues.Add("target '$($t.Name)' missing: $($t.Value)") }
    }
    foreach ($r in $cfg.roots) {
        if (-not (Test-Path -LiteralPath $r)) { [void]$issues.Add("root missing: $r") }
    }
    foreach ($f in 'AGENTS.md', 'skills') {
        if (-not (Test-Path -LiteralPath (Join-Path $repo $f))) { [void]$issues.Add("repo file missing: $f") }
    }
    return $issues
}

function Invoke-Link {
    $src = Join-Path $repo 'skills'
    $skills = @(Get-ChildItem -LiteralPath $src -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') })
    foreach ($a in $Agent) {
        $dir = Join-Path $repo ".$a\skills"
        if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        foreach ($s in $skills) {
            $p = Join-Path $dir $s.Name
            if (-not (Test-Path -LiteralPath $p)) {
                New-Item -ItemType Junction -Path $p -Target $s.FullName | Out-Null
                "linked   $a $($s.Name)"
                continue
            }
            $item = Get-Item -LiteralPath $p -Force
            $cur = $item.Target | Select-Object -First 1
            if ($item.LinkType -eq 'Junction' -and $cur -and ((Get-FullPath $cur) -ieq (Get-FullPath $s.FullName))) { "ok       $a $($s.Name)" }
            elseif ($item.LinkType -eq 'Junction') {
                [IO.Directory]::Delete($p, $false)
                New-Item -ItemType Junction -Path $p -Target $s.FullName | Out-Null
                "relinked $a $($s.Name)"
            }
            else { "SKIPPED  $a $($s.Name) - a real directory is in the way, move it by hand" }
        }
    }
    $hook = Join-Path $repo '.claude\settings.json'
    if (($Agent -contains 'claude') -and -not (Test-Path -LiteralPath $hook)) {
        $cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "$CLAUDE_PROJECT_DIR/scripts/Skillmesh.ps1" -Mode Scan -Watch -Target all'
        $obj = @{ hooks = @{ SessionStart = @(@{ hooks = @(@{ type = 'command'; command = $cmd }) }) } }
        $obj | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $hook -Encoding UTF8
        'created  claude SessionStart hook'
    }
}

if ($Mode -eq 'Link') { Invoke-Link; exit 0 }

if ($Mode -eq 'Doctor') {
    $issues = Test-Doctor
    if ($issues.Count -eq 0) { 'Doctor: ok' } else { $issues | ForEach-Object { "Doctor: $_" } }
    exit $(if ($issues.Count -eq 0) { 0 } else { 1 })
}

if ($Watch) { $NoHash = $true }
$res = Resolve-Skills (Find-Skills)
$targets = @($cfg.targets.PSObject.Properties | Where-Object {
        $Target -eq 'all' -or $Target -eq $_.Name -or ($Target -eq 'both' -and $_.Name -in 'agents', 'claude')
    })
$all = New-Object System.Collections.ArrayList

foreach ($t in $targets) {
    $rows = Scan-Target $t.Name $t.Value $res
    if ($Mode -eq 'Apply') {
        $script:curTarget = $t.Name
        foreach ($r in @($rows | Where-Object { $_.State -in 'MISSING', 'COPY', 'WRONG-TARGET', 'BROKEN' })) {
            Invoke-Fix $r $t.Value $res
            Write-Output ("applied {0,-12} {1} {2}" -f $r.State, $t.Name, $r.Skill)
        }
        $rows = Scan-Target $t.Name $t.Value $res
    }
    foreach ($r in $rows) { [void]$all.Add($r) }
}

$stateDir = Join-Path $repo 'state'
if (-not (Test-Path -LiteralPath $stateDir)) { New-Item -ItemType Directory -Path $stateDir | Out-Null }
[pscustomobject]@{
    scanned_at = (Get-Date).ToString('s')
    mode = $Mode
    target = $Target
    rows = $all
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stateDir 'last-scan.json') -Encoding UTF8

$bad = @($all | Where-Object { $_.State -notin 'OK' -and -not ($_.State -eq 'FOREIGN' -and $_.Detail -eq 'known') })
if ($Watch) {
    if ($bad.Count -gt 0) {
        $sum = ($bad | Group-Object State | ForEach-Object { "$($_.Count) $($_.Name)" }) -join ', '
        "Skillmesh: $sum - see skillmesh-scan / skillmesh-sync"
    }
    exit 0
}

$all | Sort-Object Target, @{ Expression = { if ($_.State -eq 'OK') { 1 } else { 0 } } }, State, Skill |
    Format-Table Target, Skill, State, Action, Detail -AutoSize | Out-String -Width 220
"Summary: " + (($all | Group-Object State | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' ')
