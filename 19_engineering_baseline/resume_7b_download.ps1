$ErrorActionPreference = 'Stop'

$modelRoot = 'D:\AFsim\Agent\ollama\models'
$ollama = 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe'
$requiredFreeGB = 8

if (-not (Test-Path -LiteralPath $ollama)) {
    throw "Ollama not found: $ollama"
}

$drive = Get-PSDrive -Name D
$freeGB = [math]::Round($drive.Free / 1GB, 2)
if ($freeGB -lt $requiredFreeGB) {
    throw "D drive free space is ${freeGB}GB; at least ${requiredFreeGB}GB is required."
}

$env:OLLAMA_MODELS = $modelRoot
Get-Process | Where-Object { $_.ProcessName -like 'ollama*' } | Stop-Process -Force
Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
Start-Sleep -Seconds 3

Write-Host "Model storage: $env:OLLAMA_MODELS"
Write-Host "D drive free: ${freeGB}GB"
& $ollama pull qwen2.5:7b
if ($LASTEXITCODE -ne 0) {
    throw "ollama pull failed with exit code $LASTEXITCODE"
}
& $ollama list
