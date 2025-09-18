# Ensure script's directory (project root) is the app-dir for uvicorn.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
try {
    $port = $env:PORT
    if (-not $port) { $port = 8000 }
    Write-Host "Starting backend from $scriptDir on port $port"
    uvicorn app:app --reload --app-dir $scriptDir --host 0.0.0.0 --port $port
} finally {
    Pop-Location
}
