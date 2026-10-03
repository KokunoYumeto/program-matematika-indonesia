param()
$ErrorActionPreference = 'Stop'
$editionRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$manifest = Get-Content -LiteralPath (Join-Path $editionRoot 'SOURCE_MANIFEST.json') -Raw | ConvertFrom-Json
foreach ($entry in $manifest.files) {
    $file = [IO.Path]::GetFullPath((Join-Path $editionRoot $entry.path))
    if (-not $file.StartsWith($editionRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside source package' }
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw ('Source hash differs: ' + $entry.path) }
}
$master = '01-b80-' + $manifest.language + '.tex'
$job = '00-b80-' + $manifest.language
$mutex = [Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$held = $false
$worker = $null
$savedEpoch = $env:SOURCE_DATE_EPOCH
$savedForce = $env:FORCE_SOURCE_DATE
$result = [ordered]@{schema='b80-source-replay/1';status='not_started';passes=@();abandoned_mutex_recovered=$false}
try {
    try { $held = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { $held=$true; $result.abandoned_mutex_recovered=$true }
    if (-not $held) { $result.status='slot_unavailable'; return }
    $env:SOURCE_DATE_EPOCH='1790985600'
    $env:FORCE_SOURCE_DATE='1'
    $engine = (Get-Command xelatex.exe -ErrorAction Stop).Source
    foreach ($pass in 1..3) {
        $arguments = @('--disable-installer','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error',('-jobname=' + $job),$master)
        $worker = Start-Process -FilePath $engine -ArgumentList $arguments -WorkingDirectory $editionRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $editionRoot "replay-$pass.stdout.log") -RedirectStandardError (Join-Path $editionRoot "replay-$pass.stderr.log")
        if (-not $worker.WaitForExit(180000)) { throw 'Captured replay pass exceeded three minutes' }
        $worker.Refresh()
        $result.passes += [ordered]@{pass=$pass;exit_code=$worker.ExitCode}
        if ($worker.ExitCode -ne 0) { throw 'XeLaTeX replay failed' }
        $worker = $null
        $log = Get-Content -LiteralPath (Join-Path $editionRoot ($job + '.log')) -Raw
        if ($log -match 'Undefined control sequence|LaTeX Error:|Emergency stop|Missing character:|Overfull \\[hv]box') { throw 'Replay build/content/layout error' }
        $pending = $log -match 'Rerun to get|Label\(s\) may have changed|There were undefined references'
        if ($pass -ge 2 -and -not $pending) { break }
        if ($pass -eq 3 -and $pending) { throw 'Unresolved references after three passes' }
    }
    $result.pdf_sha256=(Get-FileHash -LiteralPath (Join-Path $editionRoot ($job + '.pdf')) -Algorithm SHA256).Hash.ToLowerInvariant()
    $result.byte_identical=($result.pdf_sha256 -eq $manifest.expected_pdf_sha256)
    $result.status=if ($result.byte_identical) {'byte_identical'} else {'compiled_different_bytes'}
} catch {
    $result.status='failed'
    $result.error=$_.Exception.Message
    throw
} finally {
    if ($null -ne $worker -and -not $worker.HasExited) {
        & taskkill.exe /PID $worker.Id /T /F | Out-Null
        $worker.WaitForExit()
    }
    $env:SOURCE_DATE_EPOCH=$savedEpoch
    $env:FORCE_SOURCE_DATE=$savedForce
    if ($held) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $editionRoot 'REPLAY_RECEIPT.json') -Encoding utf8
    $result | ConvertTo-Json -Depth 6
}
