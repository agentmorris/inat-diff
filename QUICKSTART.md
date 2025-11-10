# Quick Start Guide - iNaturalist MCP Server

Get the iNaturalist species monitoring tools working with Claude Desktop in 3 simple steps!

## What You'll Be Able to Do

Ask Claude natural language questions like:
- *"What new species appeared in Oregon this month?"*
- *"Has the Burmese Python been observed in Florida this year?"*
- *"List all species in Yellowstone National Park this summer"*

## Prerequisites

**You only need:**
- Python 3.10 or higher ([Download here](https://www.python.org/downloads/))
- Claude Desktop ([Download here](https://claude.ai/download))

**That's it!** The installation script does everything else.

## Installation

### For macOS/Linux Users

1. **Download this repository** or navigate to where you have it
2. **Open Terminal** in the inat-diff folder
3. **Run the installer:**
   ```bash
   bash install_mcp.sh
   ```
4. **Restart Claude Desktop**

### For Windows Users

1. **Download this repository** or navigate to where you have it
2. **Double-click** `install_mcp.bat`
   - Or right-click → "Run as administrator" if needed
3. **Follow the on-screen instructions**
4. **Restart Claude Desktop**

## Verify Installation

1. Open Claude Desktop
2. Look for a 🔨 hammer/tools icon indicating MCP servers are connected
3. Ask Claude: *"What new species appeared in California this week?"*
4. Claude should use the inat-diff tools to answer!

## Example Questions to Try

### Find New Species
- "What species were observed in Oregon this month that weren't seen in the past 20 years?"
- "Find new species in Texas this year"
- "What new birds appeared in California in the last 6 months?"

### Check Specific Species
- "Has Python bivittatus (Burmese Python) been observed in Georgia this year?"
- "Check if Zebra Mussels have been seen in Lake Michigan recently"
- "Is the Gray Wolf new to Colorado?"

### List All Species
- "List all species observed in Yellowstone National Park this summer"
- "What species were seen in Kenya last month?"
- "Show me all amphibian species in Florida wetlands this year"

### Get Observation Details
- "Show me Gray Wolf observations in Montana this year"
- "Query observations of Panthera leo in Kenya last month"

## Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/downloads/
- **During installation, check "Add Python to PATH"**
- Restart your terminal/command prompt
- Run the installer again

### "Claude Desktop config not found"
- Make sure Claude Desktop is installed first
- Run the installer again after installing Claude Desktop

### Server not showing in Claude
- Make sure you **restarted Claude Desktop** after installation
- Check that the installation completed without errors
- See INSTALL_MCP.md for detailed troubleshooting

## What the Installer Does

The installation script automatically:
1. ✅ Checks your Python version (needs 3.10+)
2. ✅ Creates an isolated virtual environment (`.venv` folder)
3. ✅ Installs the inat-diff package and dependencies in the virtual environment
4. ✅ Finds your Claude Desktop configuration
5. ✅ Adds the MCP server configuration
6. ✅ Creates backups of any existing configuration

**You don't need to do any of this manually!**

**Note:** The installer creates a virtual environment to avoid conflicts with your system Python. This is handled automatically and you don't need to activate it manually - Claude Desktop will use it automatically.

## Need More Help?

- **Detailed documentation:** See [MCP_README.md](MCP_README.md)
- **Manual installation:** See [INSTALL_MCP.md](INSTALL_MCP.md)
- **CLI usage:** See [README.md](README.md)
- **Report issues:** [GitHub Issues](https://github.com/JasonWildMe/inat-diff/issues)

## What is iNaturalist?

[iNaturalist](https://www.inaturalist.org) is a citizen science platform where people worldwide record biodiversity observations. This tool helps you:
- **Monitor invasive species** - Detect when non-native species appear in new regions
- **Track biodiversity** - See what species are present in an area
- **Research patterns** - Analyze species distribution changes over time

## Understanding the Results

When the tool says a species is "new to a region":
- ✅ It means: No iNaturalist observations in the specified lookback period
- ⚠️ It does NOT mean: The species is definitely invasive or just arrived
- 📊 Use as: A starting point for further investigation

The lookback period (default: 20 years) can be adjusted for your needs.

---

**Ready to start?** Run the installer and begin exploring biodiversity data with Claude!
