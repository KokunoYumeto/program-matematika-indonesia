param([string]$OutputDirectory = 'work/learner-guide-v06332')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$sourcePath = Join-Path $projectRoot 'docs/guides/start-v0.63.32.tex'
$outputPath = [IO.Path]::GetFullPath((Join-Path $projectRoot $OutputDirectory))
if (-not $outputPath.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) {
    throw 'Guide output must stay inside this checkout'
}
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$mutex = [Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$held = $false
$abandoned = $false
$previousEpoch = [Environment]::GetEnvironmentVariable('SOURCE_DATE_EPOCH', 'Process')
try {
    try { $held = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { $held = $true; $abandoned = $true }
    if (-not $held) { throw 'TeX slot occupied: guide compilation not started; continue non-TeX work' }
    [Environment]::SetEnvironmentVariable('SOURCE_DATE_EPOCH', '1790726400', 'Process')
    Push-Location $projectRoot
    try {
        for ($pass = 1; $pass -le 2; $pass++) {
            & pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape "-output-directory=$outputPath" $sourcePath
            if ($LASTEXITCODE -ne 0) { throw "Guide TeX pass $pass failed" }
        }
        $log = Get-Content -LiteralPath (Join-Path $outputPath 'start-v0.63.32.log') -Raw
        if ($log -match 'Overfull \\hbox|Overfull \\vbox|Undefined control sequence|undefined references') {
            throw 'Guide build has a layout or reference error'
        }
        $pdf = Get-Item -LiteralPath (Join-Path $outputPath 'start-v0.63.32.pdf')
        [pscustomobject]@{
            state='compiled'; passes=2; abandoned_mutex_recovered=$abandoned
            bytes=$pdf.Length
            sha256=(Get-FileHash -LiteralPath $pdf.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        } | ConvertTo-Json -Compress
    } finally { Pop-Location }
} finally {
    [Environment]::SetEnvironmentVariable('SOURCE_DATE_EPOCH', $previousEpoch, 'Process')
    if ($held) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
