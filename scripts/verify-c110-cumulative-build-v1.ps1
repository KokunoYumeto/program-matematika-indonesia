param([Parameter(Mandatory=$true)][string]$BuildDirectory)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$work = [IO.Path]::GetFullPath($BuildDirectory)
if (-not $work.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Build must stay within this checkout' }
$master = Join-Path $work 'TeaTimeNumericalAnalysis-id-ID.tex'
if (-not (Test-Path -LiteralPath $master -PathType Leaf)) { throw 'Missing assembled master' }
$mutex = [Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$held = $false
$abandoned = $false
$epoch = $env:SOURCE_DATE_EPOCH
$forceDate = $env:FORCE_SOURCE_DATE
$receipt = [ordered]@{ schema='c110-assembled-build/1'; status='not_started'; abandoned_mutex_recovered=$false }
try {
    try { $held = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { $held=$true; $abandoned=$true }
    if (-not $held) { $receipt.status='slot_unavailable'; return }
    $receipt.abandoned_mutex_recovered=$abandoned
    $env:SOURCE_DATE_EPOCH='1787356800'
    $env:FORCE_SOURCE_DATE='1'
    $exe = (Get-Command latexmk.exe -ErrorAction Stop).Source
    $args = '-pdf -interaction=nonstopmode -file-line-error -halt-on-error "-pdflatex=pdflatex -no-shell-escape %O %S" TeaTimeNumericalAnalysis-id-ID.tex'
    $worker = Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory $work -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $work 'build.stdout.log') -RedirectStandardError (Join-Path $work 'build.stderr.log')
    $receipt.worker_pid=$worker.Id
    if (-not $worker.WaitForExit(300000)) {
        & taskkill.exe /PID $worker.Id /T /F | Out-Null
        $worker.WaitForExit()
        throw 'Captured build tree exceeded five-minute bound'
    }
    $worker.Refresh()
    $receipt.exit_code=$worker.ExitCode
    if ($worker.ExitCode -ne 0) { throw 'LaTeX build failed; inspect captured logs' }
    $log=Get-Content -LiteralPath (Join-Path $work 'TeaTimeNumericalAnalysis-id-ID.log') -Raw
    if ($log -match 'Undefined control sequence|There were undefined references|Citation .* undefined|LaTeX Error:|Emergency stop') { throw 'LaTeX reference or build error' }
    $pdf=Get-Item -LiteralPath (Join-Path $work 'TeaTimeNumericalAnalysis-id-ID.pdf')
    $receipt.status='compiled_pending_equivalence_check'
    $receipt.pdf=[ordered]@{bytes=$pdf.Length;sha256=(Get-FileHash -LiteralPath $pdf.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
    $receipt.source_sha256=(Get-FileHash -LiteralPath $master -Algorithm SHA256).Hash.ToLowerInvariant()
} catch {
    $receipt.status='failed'
    $receipt.error=$_.Exception.Message
    throw
} finally {
    $env:SOURCE_DATE_EPOCH=$epoch
    $env:FORCE_SOURCE_DATE=$forceDate
    $receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $work 'BUILD_RECEIPT.json') -Encoding utf8
    if ($held) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
    $receipt | ConvertTo-Json -Depth 5
}
