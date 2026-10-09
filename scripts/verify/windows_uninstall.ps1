param(
    [string] $InstallDir = (Join-Path $env:LOCALAPPDATA '起飞'),
    [string] $VideoPath
)

$ErrorActionPreference = 'Stop'
$agentExe = [System.IO.Path]::GetFullPath((Join-Path $InstallDir 'wt-media-agent.exe'))
$paths = @(
    (Join-Path $env:LOCALAPPDATA 'WTMedia\Desktop'),
    (Join-Path $env:LOCALAPPDATA 'WTMedia\Agent'),
    (Join-Path $env:USERPROFILE 'Library\Application Support\WTMedia\Desktop'),
    (Join-Path $env:USERPROFILE 'Library\Application Support\WTMedia\Agent'),
    (Join-Path $env:USERPROFILE 'Library\Logs\WTMedia\Desktop'),
    (Join-Path $env:USERPROFILE 'Library\Logs\WTMedia\Agent'),
    (Join-Path $env:USERPROFILE 'Library\Caches\WTMedia\Desktop')
)
$failures = [System.Collections.Generic.List[string]]::new()

if (Test-Path -LiteralPath $agentExe) {
    $failures.Add("Agent executable remains: $agentExe")
}

$running = @(Get-CimInstance Win32_Process -Filter "Name = 'wt-media-agent.exe'" |
    Where-Object {
        $_.ExecutablePath -and
        [string]::Equals(
            [System.IO.Path]::GetFullPath($_.ExecutablePath),
            $agentExe,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    })
if ($running.Count -gt 0) {
    $failures.Add("$($running.Count) installed Agent process(es) remain.")
}

foreach ($path in $paths) {
    if (Test-Path -LiteralPath $path) {
        $failures.Add("Application data remains: $path")
    }
}

if ($VideoPath -and -not (Test-Path -LiteralPath $VideoPath -PathType Leaf)) {
    $failures.Add("The user-selected video was removed or cannot be read: $VideoPath")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { [Console]::Error.WriteLine($_) }
    exit 1
}

Write-Host 'PASS: installed Agent process, executable, and application data are absent.'
if ($VideoPath) { Write-Host "PASS: user-selected video remains: $VideoPath" }
