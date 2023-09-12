# Check if Python 3.9 is installed
$pythonInstalled = $false
$appdata = [Environment]::GetFolderPath('LocalApplicationData')
$pythonPath = Join-Path -Path $appdata -ChildPath "Programs\Python\Python39\python.exe"

if (Test-Path -path $pythonPath) {
    Write-Host "Python 3.9 path found: $pythonPath"
    $versionOutput = & $pythonPath --version 2>&1
    Write-Host "Python 3.9 version: $versionOutput"
    if ($versionOutput -like "Python 3.9*") {
        $pythonInstalled = $true
    }
}

# Install Python 3.9 if not installed
if (-not $pythonInstalled) {
    Write-Host "Python 3.9 is not installed. Installing now..."
    winget install Python.Python.3.9
    if (-not (Test-Path -path $pythonPath)) {
        Write-Host "Failed to install Python 3.9. Exiting."
        exit
    }
} else {
    Write-Host "Python 3.9 is already installed."
}

# Check if venv exists in the current directory
$venvPath = Join-Path -Path (Get-Location) -ChildPath "venv"

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating a virtual environment in the current directory..."
    & $pythonPath -m venv venv
} else {
    Write-Host "Virtual environment already exists in the current directory."
}

# Upgrade pip and install required modules
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install 

& $pythonPath -m pip install --upgrade pip
& $pythonPath -m pip install pyserial

Write-Host "Please install the Pico extension for VSCode."
Start-Process "https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go"