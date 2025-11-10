# MCP Installation Files - Summary

This document explains all the files created for the MCP server installation and how they work together.

## Installation Scripts

### For macOS/Linux: `install_mcp.sh`
**What it does:**
1. Checks for Python 3.10+ installation
2. Verifies pip is available
3. Installs the package with `pip install -e ".[mcp]"`
4. Detects the operating system (macOS vs Linux)
5. Locates or creates the Claude Desktop config file
6. Backs up existing config if present
7. Adds/updates the inat-diff MCP server configuration
8. Provides clear success/error messages

**Usage:**
```bash
bash install_mcp.sh
```

**Features:**
- ✅ Color-coded output (green=success, red=error, yellow=info)
- ✅ Automatic config backup with timestamp
- ✅ Handles existing MCP server configurations
- ✅ Updates existing inat-diff config if already present
- ✅ Safe JSON manipulation using Python's json module

### For Windows: `install_mcp.ps1` + `install_mcp.bat`
**PowerShell Script (`install_mcp.ps1`):**
- Same functionality as the bash script
- Uses PowerShell cmdlets for file/JSON operations
- Includes pause at end so users can read output

**Batch Launcher (`install_mcp.bat`):**
- Simple wrapper that launches the PowerShell script
- Bypasses execution policy restrictions
- Checks for admin privileges (informational)
- Provides helpful error messages

**Usage:**
```batch
# Option 1: Double-click install_mcp.bat
# Option 2: Right-click install_mcp.ps1 → "Run with PowerShell"
# Option 3: Run in PowerShell: .\install_mcp.ps1
```

## What Gets Configured

The installation scripts modify/create this file:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Configuration added:**
```json
{
  "mcpServers": {
    "inat-diff": {
      "command": "python3",  // or "python" on Windows
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/inat-diff"  // detected automatically
    }
  }
}
```

## Documentation Hierarchy

### For End Users (Non-Technical)
1. **QUICKSTART.md** - Start here! Simple 3-step guide
   - Prerequisites (Python + Claude Desktop)
   - Run one command
   - Example questions to try

### For Users Who Need More Help
2. **INSTALL_MCP.md** - Detailed installation guide
   - Step-by-step with screenshots descriptions
   - Troubleshooting common issues
   - Platform-specific instructions

### For Power Users/Developers
3. **MCP_README.md** - Complete technical documentation
   - Tool reference with all parameters
   - API details
   - Development information
   - Smithery publishing guide

4. **Main README.md** - Full project documentation
   - MCP server overview (new section)
   - CLI usage
   - Python library API
   - Contributing guidelines

## File Locations

```
inat-diff/
├── mcp_server.py              # The actual MCP server implementation
├── install_mcp.sh             # macOS/Linux installer
├── install_mcp.ps1            # Windows PowerShell installer
├── install_mcp.bat            # Windows batch launcher
├── QUICKSTART.md              # Simple user guide
├── INSTALL_MCP.md             # Detailed installation guide
├── MCP_README.md              # Complete MCP documentation
├── pyproject.toml             # Modern Python packaging
├── requirements-mcp.txt       # MCP dependencies
├── smithery.json              # Smithery.ai metadata
├── claude_desktop_config.json # Example config file
└── README.md                  # Main project documentation
```

## Prerequisites

The **only** requirement for end users:
- Python 3.10 or higher
- Claude Desktop

The installation script handles everything else automatically.

## What Happens During Installation

### Step 1: Python Check
- Looks for `python3` or `python` command
- Verifies version is 3.10 or higher
- Checks that pip is available

### Step 2: Package Installation
- Runs `pip install -e ".[mcp]"`
- Installs base requirements (requests)
- Installs MCP requirements (mcp>=1.0.0)
- Installs in editable mode (for development)

### Step 3: Config File Management
- Detects OS and finds Claude config location
- Creates config directory if needed
- Backs up existing config with timestamp
- Reads existing config (if present)
- Adds/updates inat-diff server entry
- Preserves other MCP servers if present
- Writes updated config back

### Step 4: Verification
- Displays config file location
- Shows installation directory
- Provides next steps
- Asks user to restart Claude Desktop

## Error Handling

The scripts handle these common issues:

1. **Python not found**
   - Clear message to install Python
   - Link to python.org

2. **Python version too old**
   - Shows current version
   - Explains 3.10+ requirement

3. **Installation fails**
   - Saves output to log file
   - Displays error details
   - Suggests solutions

4. **Config file corruption**
   - Creates backup before modifying
   - Uses Python's json module (safe)
   - Catches JSON parse errors

5. **Permission issues**
   - Suggests running as administrator (Windows)
   - Provides alternative methods

## Testing

To test the installation scripts (without actually installing):

**macOS/Linux:**
```bash
# Check syntax
bash -n install_mcp.sh

# Dry run (would need modifications to script)
# Currently not supported - script will install
```

**Windows:**
```powershell
# Check for syntax errors
powershell -NoProfile -File install_mcp.ps1 -WhatIf
```

## Manual Installation Alternative

If the automated scripts don't work, users can follow INSTALL_MCP.md for manual installation:
1. Install Python
2. Run `pip install -e ".[mcp]"`
3. Manually edit claude_desktop_config.json
4. Restart Claude Desktop

## Future Improvements

Possible enhancements:
- [ ] Add `--test` flag to verify installation without modifying config
- [ ] Add `--uninstall` option to remove the server
- [ ] Check if Claude Desktop is running and offer to restart it
- [ ] Add desktop notifications when installation completes
- [ ] Create standalone executable (PyInstaller) to eliminate Python requirement
- [ ] Add automatic Python installation (via pyenv or similar)

## Support

If users encounter issues:
1. Check QUICKSTART.md troubleshooting section
2. Review INSTALL_MCP.md for detailed help
3. Check the main README.md
4. Open an issue on GitHub

## Summary

**For biologists:** Just run one command and restart Claude Desktop
**For developers:** Well-documented, safe scripts that handle edge cases
**For maintainers:** Clear structure with separation of concerns

The installation process reduces friction from "15 technical steps" to "1 simple command".
