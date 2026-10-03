param([ValidateSet('id','en','all')][string]$Language='all')
$ErrorActionPreference = 'Stop'
$checkoutRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$batchRoot = [IO.Path]::GetFullPath((Join-Path $checkoutRoot 'outputs\b80-format-repair-v1'))
if (-not $batchRoot.StartsWith($checkoutRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Build outside checkout' }
$languages = if ($Language -eq 'all') { @('id','en') } else { @($Language) }
$mutex = [Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$held = $false
$worker = $null
$epochBefore = $env:SOURCE_DATE_EPOCH
$forceBefore = $env:FORCE_SOURCE_DATE
$batch = [ordered]@{schema='b80-frozen-pdf-batch/1';languages=$languages;status='not_started';abandoned_mutex_recovered=$false;editions=@()}
$receipt = $null
$buildRoot = $null
try {
    try { $held = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { $held=$true; $batch.abandoned_mutex_recovered=$true }
    if (-not $held) { $batch.status='slot_unavailable'; return }
    $env:SOURCE_DATE_EPOCH='1790985600'
    $env:FORCE_SOURCE_DATE='1'
    $engine = (Get-Command xelatex.exe -ErrorAction Stop).Source
  foreach ($edition in $languages) {
    $buildRoot = Join-Path $batchRoot $edition
    $masterName = '01-b80-' + $edition + '.tex'
    $jobName = '00-b80-' + $edition
    $masterPath = Join-Path $buildRoot $masterName
    if (-not (Test-Path -LiteralPath $masterPath -PathType Leaf)) { throw 'Missing cumulative source' }
    $sourceReceipt = Get-Content -LiteralPath (Join-Path $buildRoot 'SOURCE_EXPORT_RECEIPT.json') -Raw | ConvertFrom-Json
    if (@($sourceReceipt.semantic_roundtrip.PSObject.Properties | Where-Object Value -ne $true).Count) { throw 'Source comparison has not passed' }
    if ((Get-FileHash -LiteralPath $masterPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sourceReceipt.tex_sha256) { throw 'Source changed since verified export' }
    $receipt = [ordered]@{schema='b80-frozen-pdf-build/1';language=$edition;status='not_started';passes=@();source_sha256=$sourceReceipt.tex_sha256}
    $receipt.engine = 'XeLaTeX; no-shell-escape; MiKTeX package auto-install disabled'
    foreach ($pass in 1..3) {
        $arguments = @('--disable-installer','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',('-jobname=' + $jobName),$masterName)
        $worker = Start-Process -FilePath $engine -ArgumentList $arguments -WorkingDirectory $buildRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $buildRoot "pdf-pass-$pass.stdout.log") -RedirectStandardError (Join-Path $buildRoot "pdf-pass-$pass.stderr.log")
        if (-not $worker.WaitForExit(180000)) { throw 'Captured TeX pass exceeded three-minute limit' }
        $worker.Refresh()
        $receipt.passes += [ordered]@{pass=$pass;pid=$worker.Id;exit_code=$worker.ExitCode}
        if ($worker.ExitCode -ne 0) { throw 'TeX failed; inspect exact pass logs' }
        $worker = $null
        $log = Get-Content -LiteralPath (Join-Path $buildRoot ($jobName + '.log')) -Raw
        if ($log -match 'Undefined control sequence|LaTeX Error:|Emergency stop|Missing character:') { throw 'TeX content/glyph error' }
        $needsRerun = $log -match 'Rerun to get|Label\(s\) may have changed|There were undefined references'
        if ($pass -ge 2 -and -not $needsRerun) { break }
        if ($pass -eq 3 -and $needsRerun) { throw 'References remain unresolved after three passes' }
    }
    $pdf = Get-Item -LiteralPath (Join-Path $buildRoot ($jobName + '.pdf'))
    $receipt.status='compiled_pending_visual_review'
    $receipt.pdf=[ordered]@{bytes=$pdf.Length;sha256=(Get-FileHash -LiteralPath $pdf.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
    $receipt.overfull_hboxes=([regex]::Matches($log,'Overfull \\hbox')).Count
    $receipt.overfull_vboxes=([regex]::Matches($log,'Overfull \\vbox')).Count
    $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $buildRoot 'PDF_BUILD_RECEIPT.json') -Encoding utf8
    $batch.editions += $receipt
    $receipt = $null
  }
  $batch.status='compiled_pending_visual_review'
} catch {
    $batch.status='failed'
    $batch.error=$_.Exception.Message
    if ($null -ne $receipt) { $receipt.status='failed'; $receipt.error=$_.Exception.Message }
    throw
} finally {
    if ($null -ne $worker -and -not $worker.HasExited) {
        & taskkill.exe /PID $worker.Id /T /F | Out-Null
        $worker.WaitForExit()
        $batch.captured_tree_stopped=$true
    }
    $env:SOURCE_DATE_EPOCH=$epochBefore
    $env:FORCE_SOURCE_DATE=$forceBefore
    if ($null -ne $receipt -and $null -ne $buildRoot) {
        $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $buildRoot 'PDF_BUILD_RECEIPT.json') -Encoding utf8
        $batch.editions += $receipt
    }
    $batch | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $batchRoot 'PDF_BATCH_RECEIPT.json') -Encoding utf8
    if ($held) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
    $batch | ConvertTo-Json -Depth 8
}
