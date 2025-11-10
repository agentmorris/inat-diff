# Quick MCP Server Installation Guide

This guide will help you install and configure the iNaturalist Difference Detection MCP server for use with Claude Desktop or other MCP clients.

## Step 1: Install Python

Ensure you have Python 3.10 or higher installed:

```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

## Step 2: Install the Package

### Option A: Install from source (recommended for now)

```bash
# Clone the repository
git clone https://github.com/JasonWildMe/inat-diff.git
cd inat-diff

# Install with MCP support
pip install -e ".[mcp]"
```

### Option B: Install from PyPI (when published)

```bash
pip install "inat-diff[mcp]"
```

## Step 3: Configure Claude Desktop

### macOS

1. Open Claude Desktop configuration file:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Add the server configuration:
   ```json
   {
     "mcpServers": {
       "inat-diff": {
         "command": "python3",
         "args": ["-m", "mcp_server"],
         "cwd": "/path/to/inat-diff"
       }
     }
   }
   ```

3. Replace `/path/to/inat-diff` with the actual path where you cloned the repository

4. Save and close (Ctrl+O, Enter, Ctrl+X in nano)

5. Restart Claude Desktop

### Windows

1. Open Claude Desktop configuration file:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Add the server configuration:
   ```json
   {
     "mcpServers": {
       "inat-diff": {
         "command": "python",
         "args": ["-m", "mcp_server"],
         "cwd": "C:\\path\\to\\inat-diff"
       }
     }
   }
   ```

3. Replace `C:\path\to\inat-diff` with the actual path where you cloned the repository

4. Save and close

5. Restart Claude Desktop

### Linux

1. Open Claude Desktop configuration file:
   ```bash
   nano ~/.config/Claude/claude_desktop_config.json
   ```

2. Add the server configuration:
   ```json
   {
     "mcpServers": {
       "inat-diff": {
         "command": "python3",
         "args": ["-m", "mcp_server"],
         "cwd": "/path/to/inat-diff"
       }
     }
   }
   ```

3. Replace `/path/to/inat-diff` with the actual path where you cloned the repository

4. Save and close

5. Restart Claude Desktop

## Step 4: Test the Installation

1. Open Claude Desktop

2. Look for the hammer/tools icon indicating MCP servers are connected

3. Try asking Claude:
   > "What new species appeared in Oregon this month?"

4. Claude should use the `inat-diff` MCP server to answer your question

## Troubleshooting

### Python Not Found

If you get "python not found" or "python3 not found":
- Make sure Python 3.10+ is installed
- Try using the full path to Python in the config:
  - macOS/Linux: Find with `which python3`
  - Windows: Find with `where python`

### Module Not Found: mcp

If you get "No module named 'mcp'":
```bash
pip install mcp
```

### Module Not Found: inat_diff

If you get "No module named 'inat_diff'":
- Make sure you're in the correct directory
- Reinstall: `pip install -e ".[mcp]"`

### Server Not Appearing in Claude

- Check Claude Desktop logs (varies by OS)
- Ensure the `cwd` path in config is correct
- Try absolute paths instead of relative paths
- Restart Claude Desktop completely

### Permission Denied

On macOS/Linux, you may need to make the server executable:
```bash
chmod +x mcp_server.py
```

## Next Steps

Once installed, you can:

- **Find new species**: "What new species appeared in California this year?"
- **Check specific species**: "Has the Burmese Python been observed in Texas recently?"
- **List species**: "List all species in Yellowstone National Park this summer"
- **Query observations**: "Show me Gray Wolf observations in Montana"

See [MCP_README.md](MCP_README.md) for complete documentation and usage examples.

## Getting Help

- Check the [MCP_README.md](MCP_README.md) for detailed documentation
- Report issues on [GitHub](https://github.com/JasonWildMe/inat-diff/issues)
- Review the [main README](README.md) for CLI usage
