#!/bin/bash

################################################################################
# iNaturalist Difference Detection - Automated MCP Server Installer
# For macOS and Linux
################################################################################

set -e  # Exit on error

echo "=========================================="
echo "iNaturalist MCP Server Installer"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Step 1: Check if Python is installed
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python not found!"
    echo ""
    echo "Please install Python 3.10 or higher from:"
    echo "  https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# Check Python version is 3.10+
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    echo "Please upgrade Python from: https://www.python.org/downloads/"
    exit 1
fi

print_success "Python version is compatible (3.10+)"
echo ""

# Step 2: Check if pip is installed
echo "Step 2: Checking pip installation..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_success "pip is installed"
else
    print_error "pip not found!"
    echo "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
fi
echo ""

# Step 3: Get the installation directory
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
print_info "Installing from: $INSTALL_DIR"
echo ""

# Step 4: Create and activate virtual environment
echo "Step 3: Setting up virtual environment..."
cd "$INSTALL_DIR"

VENV_DIR="$INSTALL_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
    print_info "Virtual environment already exists"
else
    print_info "Creating virtual environment..."
    if $PYTHON_CMD -m venv "$VENV_DIR" > /tmp/inat_install.log 2>&1; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        echo "Check /tmp/inat_install.log for details"
        cat /tmp/inat_install.log
        exit 1
    fi
fi

# Determine the path to the venv's Python
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
else
    VENV_PYTHON="$VENV_DIR/Scripts/python"
fi

print_success "Virtual environment ready"
echo ""

# Step 5: Install the package in virtual environment
echo "Step 4: Installing inat-diff with MCP support..."
echo "This may take a minute..."

if "$VENV_PYTHON" -m pip install --upgrade pip > /tmp/inat_install.log 2>&1; then
    print_info "pip upgraded"
else
    print_info "pip upgrade skipped (not critical)"
fi

if "$VENV_PYTHON" -m pip install -e ".[mcp]" >> /tmp/inat_install.log 2>&1; then
    print_success "Package installed successfully"
else
    print_error "Installation failed"
    echo "Check /tmp/inat_install.log for details"
    cat /tmp/inat_install.log
    exit 1
fi
echo ""

# Step 5: Detect OS and configure Claude Desktop
echo "Step 4: Configuring Claude Desktop..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    print_info "Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONFIG_DIR="$HOME/.config/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    print_info "Detected Linux"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Check if config file exists
if [ -f "$CONFIG_FILE" ]; then
    print_info "Claude config file exists, backing up..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backup created"

    # Check if the config already has mcpServers
    if grep -q '"mcpServers"' "$CONFIG_FILE"; then
        print_info "Existing MCP servers found"

        # Check if inat-diff is already configured
        if grep -q '"inat-diff"' "$CONFIG_FILE"; then
            print_info "inat-diff server already configured, updating..."

            # Use Python to update the JSON (safer than sed)
            "$VENV_PYTHON" << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
config['mcpServers']['inat-diff'] = {
    'command': '$VENV_PYTHON',
    'args': ['-m', 'mcp_server'],
    'cwd': '$INSTALL_DIR'
}
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF
            print_success "Configuration updated"
        else
            print_info "Adding inat-diff server to existing config..."

            "$VENV_PYTHON" << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['inat-diff'] = {
    'command': '$VENV_PYTHON',
    'args': ['-m', 'mcp_server'],
    'cwd': '$INSTALL_DIR'
}
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF
            print_success "Configuration added"
        fi
    else
        print_info "No MCP servers configured yet, adding..."

        "$VENV_PYTHON" << EOF
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
except:
    config = {}
config['mcpServers'] = {
    'inat-diff': {
        'command': '$VENV_PYTHON',
        'args': ['-m', 'mcp_server'],
        'cwd': '$INSTALL_DIR'
    }
}
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF
        print_success "Configuration created"
    fi
else
    print_info "Creating new Claude config file..."

    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "inat-diff": {
      "command": "$VENV_PYTHON",
      "args": ["-m", "mcp_server"],
      "cwd": "$INSTALL_DIR"
    }
  }
}
EOF
    print_success "Configuration created"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Restart Claude Desktop"
echo "  2. Look for the tools/hammer icon (MCP servers connected)"
echo "  3. Try asking Claude:"
echo "     \"What new species appeared in Oregon this month?\""
echo ""
echo "For help and examples, see:"
echo "  - MCP_README.md (detailed documentation)"
echo "  - INSTALL_MCP.md (troubleshooting)"
echo ""
echo "Configuration file: $CONFIG_FILE"
echo "Installation directory: $INSTALL_DIR"
echo ""
