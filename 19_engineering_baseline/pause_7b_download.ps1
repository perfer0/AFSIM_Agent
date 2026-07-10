$pullProcesses = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'ollama.exe' -and $_.CommandLine -match '\bpull\s+qwen2\.5:7b'
}

foreach ($process in $pullProcesses) {
    Stop-Process -Id $process.ProcessId -Force
    Write-Host "Stopped qwen2.5:7b pull process $($process.ProcessId)."
}

if (-not $pullProcesses) {
    Write-Host 'No qwen2.5:7b pull process is running.'
}

Write-Host 'The Ollama serve process was not stopped.'
