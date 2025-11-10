# iNaturalist Difference Detection - MCP Server

An [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides invasive species monitoring and biodiversity research tools through iNaturalist data. This server allows non-technical biologists to easily query iNaturalist through Claude or any MCP-compatible AI assistant.

## Features

The MCP server provides four main tools:

1. **find_new_species_in_region** - Find all species that appear to be new to a region
2. **check_if_species_is_new** - Check if a specific species is new to a region
3. **list_species_in_region** - List all species observed in a region
4. **query_species_observations** - Query detailed observations for a specific species

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/agentmorris/inat-diff.git
cd inat-diff

# Install with MCP support
pip install -e ".[mcp]"
```

### Install from PyPI (when published)

```bash
pip install "inat-diff[mcp]"
```

## Configuration

### Using with Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "inat-diff": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/inat-diff"
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "inat-diff": {
      "command": "inat-diff-mcp"
    }
  }
}
```

### Using with Other MCP Clients

The server uses stdio for communication. Run it with:

```bash
python mcp_server.py
```

Or if installed:

```bash
inat-diff-mcp
```

## Usage Examples

Once configured, you can ask Claude (or your MCP client) natural language questions:

### Finding New Species

> "What new species have been observed in Oregon this month?"

> "Find all species that appeared in California in the last week that weren't seen in the past 10 years"

### Checking Specific Species

> "Has the Burmese Python (Python bivittatus) been observed in Florida this year? Is it new to the region?"

> "Check if Zebra Mussels have appeared in the Great Lakes recently"

### Listing Species

> "List all species observed in Yellowstone National Park this summer"

> "What species were seen in Kenya last month?"

### Querying Observations

> "Show me observations of Gray Wolves in Montana this year"

## Tool Reference

### find_new_species_in_region

Finds all species that appear to be new to a region during a time period.

**Parameters:**
- `region` (required): Geographic region name (e.g., "Oregon", "California", "Kenya")
- `time_period` (required): Time period (e.g., "last 30 days", "this month", "this year")
- `lookback_years` (optional): Years to look back for historical data (default: 20)
- `rate_limit` (optional): Seconds between API calls (default: 1.2)

**Example:**
```
Region: Oregon
Time period: this month
Lookback years: 20
```

### check_if_species_is_new

Checks if a specific species is new to a region.

**Parameters:**
- `species_name` (required): Latin scientific name (e.g., "Python bivittatus")
- `region` (required): Geographic region name
- `time_period` (required): Time period to check
- `lookback_years` (optional): Years to look back (default: 20)

**Example:**
```
Species: Python bivittatus
Region: Florida
Time period: this year
```

### list_species_in_region

Lists all species observed in a region during a time period.

**Parameters:**
- `region` (required): Geographic region name
- `time_period` (required): Time period to query

**Example:**
```
Region: Yellowstone National Park
Time period: last 6 months
```

### query_species_observations

Queries detailed observations for a specific species.

**Parameters:**
- `species_name` (required): Latin scientific name
- `region` (required): Geographic region name
- `time_period` (required): Time period to query

**Example:**
```
Species: Canis lupus
Region: Montana
Time period: last 30 days
```

## Supported Formats

### Time Periods
- `"last N days/weeks/months/years"` (e.g., "last 30 days")
- `"past N days/weeks/months/years"` (e.g., "past 6 months")
- `"this month/year"` (e.g., "this month")
- `"YYYY-MM-DD to YYYY-MM-DD"` (e.g., "2024-01-01 to 2024-12-31")

### Regions
The server works with any place name recognized by iNaturalist:

**Standard Places:**
- **Countries**: "United States", "Canada", "Kenya", "Mexico"
- **States/Provinces**: "California", "Oregon", "British Columbia", "Ontario"
- **Counties**: "Multnomah County", "King County"
- **Continents**: "North America", "Africa", "Europe"
- **US National Parks**: "Yellowstone National Park", "Yosemite National Park"

**Community Curated Places:**
- State parks, wildlife areas, watersheds, and other user-created boundaries

**Tips:**
- Use specific names: "Washington" (state) vs "Washington County"
- The tool prioritizes: countries → states → counties when multiple matches exist
- Check [iNaturalist Places](https://www.inaturalist.org/places) to verify exact names

### Species Names
- Use Latin scientific names (e.g., "Panthera leo", "Python bivittatus")
- Genus and species format recommended
- Common names are not supported (use scientific names instead)

## Use Cases

### Invasive Species Monitoring

Track when potentially invasive species first appear in new regions:

> "What new species appeared in Oregon this month that weren't seen in the past 20 years?"

> "Check if Burmese Pythons have been observed in Texas this year"

### Biodiversity Research

Study species distribution changes over time:

> "List all species observed in the Amazon rainforest this year"

> "What new bird species appeared in California in the last 6 months?"

### Conservation

Monitor protected species presence:

> "Has the Gray Wolf been observed in Yellowstone National Park this month?"

> "Find new amphibian species in Florida wetlands this year"

## Performance Notes

- **Small queries** (last week): ~5 minutes for regions with ~2,000 species
- **Medium queries** (last month): ~20-30 minutes for regions with ~6,000 species
- **Large queries** (last year): Can take several hours for biodiverse regions

The server respects iNaturalist's API rate limits (default: 50 requests/minute) to avoid throttling.

## Limitations

- "New" species detection is relative to available iNaturalist data, not actual species establishment
- Performance scales with the number of unique species in the time period
- Subject to iNaturalist API rate limits
- Geographic boundaries depend on iNaturalist's place database
- Lookback period is limited to available historical data (iNaturalist started ~2008)

## Publishing to Smithery

To publish this MCP server to [Smithery.ai](https://smithery.ai):

1. Ensure your GitHub repository is public
2. Create a release on GitHub
3. Submit to Smithery at https://smithery.ai/submit
4. Follow Smithery's submission guidelines

The server includes all necessary metadata in `pyproject.toml` for Smithery compatibility.

## Troubleshooting

### Place Not Found Error

If you get a "place not found" error:
- Use more specific place names (e.g., "Oregon" instead of "OR")
- Check the exact name on [iNaturalist Places](https://www.inaturalist.org/places)
- Try variations (e.g., "United States" vs "USA")

### Species Not Found Error

If you get a "species not found" error:
- Use Latin scientific names (e.g., "Canis lupus" not "wolf")
- Check the scientific name on [iNaturalist Taxa](https://www.inaturalist.org/taxa)
- Ensure correct spelling

### Rate Limit Errors

If you hit rate limits:
- Increase the `rate_limit` parameter (default: 1.2 seconds)
- Wait a few minutes before retrying
- Avoid running multiple queries simultaneously

### Slow Performance

For faster results:
- Use shorter time periods (e.g., "last week" instead of "last month")
- Reduce lookback years (though this may miss some historical data)
- Lower the rate_limit parameter to 0.6 (minimum safe value)

## Development

### Running Locally

```bash
# Install in development mode
pip install -e ".[mcp,dev]"

# Run the server
python mcp_server.py

# Run tests (when available)
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/agentmorris/inat-diff/issues)
- Check the main [README](../README.md) for CLI usage
- Review [iNaturalist API documentation](https://www.inaturalist.org/pages/api+reference)
