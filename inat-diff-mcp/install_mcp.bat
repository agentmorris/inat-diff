@echo off
REM iNaturalist Difference Detection - Windows Installer Launcher
REM This batch file launches the PowerShell installer

echo ==========================================
echo iNaturalist MCP Server Installer
echo ==========================================
echo.

REM Check if running as administrator (optional, but helpful)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo Note: Not running as administrator
    echo If installation fails, try right-click "Run as administrator"
)
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the PowerShell script
echo Launching PowerShell installer...
echo.
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install_mcp.ps1"

if %errorLevel% neq 0 (
    echo.
    echo Installation encountered an error.
    echo.
    echo If you see "script is not digitally signed" error:
    echo   1. Right-click install_mcp.ps1
    echo   2. Select "Run with PowerShell"
    echo.
    pause
    exit /b 1
)

echo.
echo Installation script completed.
pause
