# Define paths
$venvPath = "venv"  # Path for the virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
$mainScript = "main.py"

# Check if the virtual environment exists
if (-Not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Please set it up first." -ForegroundColor Red
    exit 1
}

# Check if the activation script exists
if (Test-Path $activateScript) {
    Write-Host "Activating the virtual environment..." -ForegroundColor Cyan
    & $activateScript
    Write-Host "Virtual environment activated." -ForegroundColor Green

    # Run main.py
    Write-Host "Running $mainScript..." -ForegroundColor Cyan
    pythonw $mainScript
} else {
    Write-Host "Activation script not found. Cannot execute main.py." -ForegroundColor Red
    exit 1
}
