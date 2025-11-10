################################################################################
# iNaturalist Difference Detection - Automated MCP Server Installer
# For Windows (PowerShell)
################################################################################

# Enable strict mode
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "iNaturalist MCP Server Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Function to print colored messages
function Print-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# Step 1: Check if Python is installed
Write-Host "Step 1: Checking Python installation..."

$pythonCmd = $null
$pythonVersion = $null

# Try python3 first, then python
try {
    $pythonVersion = & python3 --version 2>&1
    $pythonCmd = "python3"
} catch {
    try {
        $pythonVersion = & python --version 2>&1
        $pythonCmd = "python"
    } catch {
        Print-Error "Python not found!"
        Write-Host ""
        Write-Host "Please install Python 3.10 or higher from:"
        Write-Host "  https://www.python.org/downloads/"
        Write-Host ""
        Write-Host "During installation, make sure to check:"
        Write-Host "  [✓] Add Python to PATH"
        Write-Host ""
        pause
        exit 1
    }
}

Print-Success "Python found: $pythonVersion"

# Check Python version is 3.10+
$versionOutput = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$versionParts = $versionOutput -split '\.'
$majorVersion = [int]$versionParts[0]
$minorVersion = [int]$versionParts[1]

if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 10)) {
    Print-Error "Python 3.10 or higher is required"
    Write-Host "Current version: $pythonVersion"
    Write-Host "Please upgrade Python from: https://www.python.org/downloads/"
    pause
    exit 1
}

Print-Success "Python version is compatible (3.10+)"
Write-Host ""

# Step 2: Check if pip is installed
Write-Host "Step 2: Checking pip installation..."
try {
    & $pythonCmd -m pip --version | Out-Null
    Print-Success "pip is installed"
} catch {
    Print-Error "pip not found!"
    Write-Host "Installing pip..."
    & $pythonCmd -m ensurepip --upgrade
}
Write-Host ""

# Step 3: Get the installation directory
$InstallDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Print-Info "Installing from: $InstallDir"
Write-Host ""

# Step 4: Create virtual environment
Write-Host "Step 3: Setting up virtual environment..."
$VenvDir = Join-Path $InstallDir ".venv"

if (Test-Path $VenvDir) {
    Print-Info "Virtual environment already exists"
} else {
    Print-Info "Creating virtual environment..."
    try {
        & $pythonCmd -m venv $VenvDir
        Print-Success "Virtual environment created"
    } catch {
        Print-Error "Failed to create virtual environment: $_"
        pause
        exit 1
    }
}

# Determine path to venv Python
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Print-Error "Virtual environment Python not found at: $VenvPython"
    pause
    exit 1
}

Print-Success "Virtual environment ready"
Write-Host ""

# Step 5: Install the package in virtual environment
Write-Host "Step 4: Installing inat-diff with MCP support..."
Write-Host "This may take a minute..."

Push-Location $InstallDir
try {
    # Upgrade pip
    $output = & $VenvPython -m pip install --upgrade pip 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Info "pip upgraded"
    } else {
        Print-Info "pip upgrade skipped (not critical)"
    }

    # Install the package
    $output = & $VenvPython -m pip install -e ".[mcp]" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Installation failed"
        Write-Host $output
        pause
        exit 1
    }
    Print-Success "Package installed successfully"
} catch {
    Print-Error "Installation failed: $_"
    pause
    exit 1
} finally {
    Pop-Location
}
Write-Host ""

# Step 6: Configure Claude Desktop
Write-Host "Step 5: Configuring Claude Desktop..."

$ConfigDir = "$env:APPDATA\Claude"
$ConfigFile = "$ConfigDir\claude_desktop_config.json"
Print-Info "Config location: $ConfigFile"

# Create config directory if it doesn't exist
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    Print-Info "Created config directory"
}

# Prepare the server config
$serverConfig = @{
    command = $VenvPython
    args = @("-m", "mcp_server")
    cwd = $InstallDir
}

# Check if config file exists
if (Test-Path $ConfigFile) {
    Print-Info "Claude config file exists, backing up..."
    $backupFile = "$ConfigFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $ConfigFile $backupFile
    Print-Success "Backup created: $backupFile"

    # Read existing config
    try {
        $config = Get-Content $ConfigFile -Raw | ConvertFrom-Json

        # Ensure mcpServers exists
        if (-not $config.mcpServers) {
            $config | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value (New-Object PSObject)
        }

        # Add or update inat-diff server
        if ($config.mcpServers.PSObject.Properties.Name -contains "inat-diff") {
            Print-Info "Updating existing inat-diff configuration..."
        } else {
            Print-Info "Adding inat-diff server to configuration..."
        }

        $config.mcpServers | Add-Member -MemberType NoteProperty -Name "inat-diff" -Value $serverConfig -Force

        # Save config
        $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile
        Print-Success "Configuration updated"
    } catch {
        Print-Error "Failed to update config: $_"
        Print-Info "You may need to manually edit: $ConfigFile"
        pause
        exit 1
    }
} else {
    Print-Info "Creating new Claude config file..."

    $config = @{
        mcpServers = @{
            "inat-diff" = $serverConfig
        }
    }

    $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile
    Print-Success "Configuration created"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Claude Desktop"
Write-Host "  2. Look for the tools/hammer icon (MCP servers connected)"
Write-Host "  3. Try asking Claude:"
Write-Host "     'What new species appeared in Oregon this month?'"
Write-Host ""
Write-Host "For help and examples, see:"
Write-Host "  - QUICKSTART.md (quick start guide)"
Write-Host "  - MCP_README.md (detailed documentation)"
Write-Host ""
Write-Host "Configuration file: $ConfigFile"
Write-Host "Installation directory: $InstallDir"
Write-Host ""
pause
