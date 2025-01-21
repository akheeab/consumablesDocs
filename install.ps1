# Define paths
$venvPath = "venv"  # Path for the virtual environment
$requirementsFile = "requirements.txt"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

# Function to run a command and check its success
function Run-Command {
    param (
        [string]$Command,
        [array]$Arguments
    )
    $process = Start-Process -FilePath $Command -ArgumentList $Arguments -NoNewWindow -PassThru -Wait
    if ($process.ExitCode -ne 0) {
        Write-Host "An error occurred while running: $Command $Arguments" -ForegroundColor Red
        exit $process.ExitCode
    }
}

# Step 1: Create a virtual environment if it doesn't exist
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating a Python virtual environment..." -ForegroundColor Cyan
    Run-Command -Command "python" -Arguments @("-m", "venv", $venvPath)
    Write-Host "Virtual environment created at $venvPath." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists at $venvPath." -ForegroundColor Yellow
}

# Step 2: Activate the virtual environment
if (Test-Path $activateScript) {
    Write-Host "Activating the virtual environment..." -ForegroundColor Cyan
    & $activateScript
    Write-Host "Virtual environment activated." -ForegroundColor Green
} else {
    Write-Host "Activation script not found. Please check the virtual environment path." -ForegroundColor Red
    exit 1
}

# Step 3: Install packages from requirements.txt inside the virtual environment
if (Test-Path $requirementsFile) {
    Write-Host "Installing packages from $requirementsFile..." -ForegroundColor Cyan
    Run-Command -Command "python" -Arguments @("-m", "pip", "install", "-r", $requirementsFile)
    Write-Host "Packages installed successfully." -ForegroundColor Green
} else {
    Write-Host "$requirementsFile not found. Skipping package installation." -ForegroundColor Yellow
}
