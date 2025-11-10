# iNaturalist Difference Detection

A Python library and CLI tool for querying iNaturalist observations to detect species presence patterns across regions and time periods. Designed for invasive species monitoring and biodiversity research.

An example of the output of this system is available [here](http://dmorris.net/misc/tmp/last-30-days-oregon.html); that page shows taxa that were observed in Oregon for the first time in the 30 days prior to 2025.10.03.

## Features

- Query species observations by region and time period
- Detect potentially "new" species in regions (no previous observations)
- List all species observed in a region during a time period
- Support for flexible time period formats
- Command-line interface and Python library

## 🚀 MCP Server for Claude - Easy Installation!

**NEW:** Use this tool directly in Claude Desktop with **one simple command!** No technical knowledge required.

### For Non-Technical Users: One-Click Install

**macOS/Linux:**
```bash
bash install_mcp.sh
```

**Windows:**
Double-click `install_mcp.bat`

**Then restart Claude Desktop and start asking questions!**

👉 **See [QUICKSTART.md](QUICKSTART.md) for complete beginner-friendly setup** 👈

### What You Can Do

Ask Claude natural language questions like:
- *"What new species appeared in Oregon this month?"*
- *"Has the Burmese Python been observed in Florida this year?"*
- *"List all species in Yellowstone National Park this summer"*

The MCP server makes this tool accessible to invasive species biologists and researchers without any programming knowledge.

📚 **Documentation:**
- [QUICKSTART.md](QUICKSTART.md) - Simple installation guide
- [MCP_README.md](MCP_README.md) - Complete MCP documentation
- [INSTALL_MCP.md](INSTALL_MCP.md) - Manual installation & troubleshooting

## Installation

### Standard Installation (CLI & Python Library)

```bash
pip install -r requirements.txt
pip install -e .
```

### MCP Server Installation

```bash
pip install -e ".[mcp]"
```

See [MCP_README.md](MCP_README.md) for complete MCP server setup.

## Quick Start

### Command Line Interface

```bash
# Query specific species observations
inat-diff query "Panthera leo" "last 30 days" "Kenya"

# Find all new species in a region (i.e., species observed in a region for the first time recently)
inat-diff new-species "this month" "Oregon" --lookback-years 20

# Check if a specific species is new to a region
inat-diff new-species "this year" "Florida" "Python bivittatus" --lookback-years 20

# List all species in a region during time period
inat-diff list-species "last month" "Oregon"
```

### Python Library

```python
from inat_diff import SpeciesQuery

# Initialize query engine
query = SpeciesQuery()

# Find all new species in a region (main use case)
results = query.find_all_new_species_in_period(
    time_period="this month",
    region="Oregon",
    lookback_years=20,
    rate_limit=1.0,  # seconds between API calls
    verbose=True
)

print(f"Found {results['new_species_count']} new species:")
for species in results['new_species']:
    print(f"  {species['name']} ({species.get('preferred_common_name', 'no common name')})")

# Check if a specific species is new to a region
specific = query.find_new_species_in_period(
    taxon_name="Python bivittatus",
    time_period="this year",
    region="Florida",
    lookback_years=20
)

print(f"New to region: {specific['is_new_to_region']}")
print(f"Analysis: {specific['analysis']}")
```

## Supported Formats

### Time Periods
- `"last N days/weeks/months/years"`
- `"past N days/weeks/months/years"`
- `"this month/year"`
- `"YYYY-MM-DD to YYYY-MM-DD"` (explicit date ranges)

### Regions
iNaturalist supports various place types. The tool works with any place name recognized by iNaturalist:

**Standard Places (maintained by iNaturalist staff):**
- **Countries**: "United States", "Canada", "Kenya", "Mexico" (253 total)
- **States/Provinces**: "California", "Oregon", "British Columbia", "Ontario" (~3,000 total)
- **Counties/Level 2**: "Multnomah County", "King County" (~40,000 total)
- **Continents**: "North America", "Africa", "Europe"
- **US National Parks**: "Yellowstone National Park", "Yosemite National Park" (429 parks)

**Community Curated Places:**
- State parks, wildlife areas, watersheds, and other user-created boundaries
- Search by name: the tool will find the best match from iNaturalist's database

**Tips:**
- Use specific names: "Washington" (state) vs "Washington County"
- The tool prioritizes: countries → states → counties when multiple matches exist
- If unsure, check [iNaturalist Places](https://www.inaturalist.org/places) to verify the exact name

### Taxa
- Latin names in iNaturalist taxonomy: "Panthera leo", "Python bivittatus"
- Genus and species format recommended

## Commands

### `query`
Query for specific species observations in a region and time period.

```bash
inat-diff query "Canis lupus" "last 6 months" "Montana"
```

### `new-species` (Main Use Case)
Find all species that appear to be new to a region, or check a specific species.

**Find all new species in a region:**
```bash
inat-diff new-species "this month" "Oregon" --lookback-years 20 --rate-limit 1.0
```

**Options:**
- `--lookback-years N`: Years to look back for historical data (default: 5, recommended: 20)
- `--rate-limit N`: Seconds between API calls (default: 1.0 = 60 req/min, max safe: 0.6 = 100 req/min)

**Performance:** Performance notes for Oregon:
- Last week (~2,000 species): ~35 minutes at default rate
- Last month (~6,000 species): ~100 minutes at default rate
- Use `--rate-limit 0.6` to go faster (max iNaturalist allows)

### `list-species`

List all species observed in a region during a time period.

```bash
inat-diff list-species "this month" "Oregon"
```

## HTML Visualization

Generate interactive HTML reports from JSON output:

```bash
# Save query results to JSON
inat-diff new-species "this month" "Oregon" --output-file results.json

# Generate HTML visualization
inat-diff-visualize results.json report.html
```

The HTML report includes:
- Summary statistics with visual cards
- Sortable species lists with common and scientific names
- Direct links to iNaturalist observations for each species
- Badges showing taxonomic rank, iconic taxon, and "new" status
- Observation counts for current and historical periods
- Responsive design for mobile and desktop viewing

**Quality Grade Annotations (Optional):**
```bash
# Include observation quality grades (Research/Needs ID/Casual)
inat-diff-visualize results.json report.html --include-quality

# Customize API rate limiting (default: 1.2 seconds between calls)
inat-diff-visualize results.json report.html --include-quality --rate-limit 0.6
```

This fetches the highest available quality grade for each species from iNaturalist's API:
- Displays "Best quality: Research Grade", "Needs ID", or "Casual" for each species
- Requires O(N) API calls where N = number of species (can be slow for large datasets)
- Includes automatic retry logic (3 attempts with exponential backoff) for failed API calls
- Progress indication shows current species being processed
- Rate limiting respects iNaturalist API guidelines (default: 1.2s = 50 req/min, safe range: 0.6-1.2s)
- Useful for filtering to high-quality observations for scientific purposes
- Disabled by default to keep visualization fast and offline

**Example:**
```bash
# Complete workflow
inat-diff new-species "last month" "Delaware" -o delaware.json
inat-diff-visualize delaware.json delaware.html
open delaware.html  # or xdg-open on Linux

# With quality grades (slower but more informative)
inat-diff-visualize delaware.json delaware_with_quality.html --include-quality
```

## JSON Output Format

All commands support the `--output-file` (`-o`) option to save results as JSON. This is useful for creating visualizations, further analysis, or linking to iNaturalist observations.

### `new-species` Output

```json
{
  "query": {
    "region": "Oregon",
    "place_id": 10,
    "time_period": "this month",
    "start_date": "2025-10-01",
    "end_date": "2025-10-03"
  },
  "lookback_period": "2005-09-30 to 2025-09-30",
  "lookback_years": 20,
  "total_species_in_period": 1234,
  "new_species_count": 5,
  "established_species_count": 1229,
  "new_species": [
    {
      "id": 12345,
      "name": "Panthera leo",
      "preferred_common_name": "Lion",
      "rank": "species",
      "iconic_taxon": "Animalia",
      "observation_count": 3,
      "historical_count": 0
    }
  ],
  "established_species": [
    {
      "id": 67890,
      "name": "Canis lupus",
      "preferred_common_name": "Gray Wolf",
      "rank": "species",
      "iconic_taxon": "Animalia",
      "observation_count": 15,
      "historical_count": 142
    }
  ],
  "rate_limit_seconds": 1.2
}
```

**Field Descriptions:**
- **`query`**: Metadata about the search parameters
  - `region`: Region name as provided
  - `place_id`: iNaturalist place ID for the region
  - `time_period`: Time period string as provided
  - `start_date`/`end_date`: Parsed date range (YYYY-MM-DD)
- **`lookback_period`**: Historical date range used for comparison
- **`lookback_years`**: Years of lookback used
- **`total_species_in_period`**: Total unique species observed in the current period
- **`new_species_count`**: Number of species with no historical observations
- **`established_species_count`**: Number of species with historical observations
- **`new_species`**: Array of species objects with no prior observations
- **`established_species`**: Array of species objects with prior observations
- **`rate_limit_seconds`**: Rate limiting setting used

**Species Object Fields:**
- `id`: iNaturalist taxon ID (can be used to construct URLs: `https://www.inaturalist.org/taxa/{id}`)
- `name`: Scientific (Latin) name
- `preferred_common_name`: Common name in English (may be `null`)
- `rank`: Taxonomic rank (`"species"`, `"genus"`, `"subspecies"`, etc.)
- `iconic_taxon`: High-level taxonomic group (`"Animalia"`, `"Plantae"`, `"Insecta"`, `"Fungi"`, etc.)
- `observation_count`: Number of observations in the current period
- `historical_count`: Number of observations in the lookback period (0 for new species)

### `query` Output

```json
{
  "query": {
    "taxon_name": "Panthera leo",
    "taxon_id": 12345,
    "region": "Kenya",
    "place_id": 6986,
    "time_period": "last 30 days",
    "start_date": "2025-09-03",
    "end_date": "2025-10-03"
  },
  "place_info": {
    "id": 6986,
    "name": "Kenya",
    "display_name": "Kenya"
  },
  "observations": {
    "total_results": 42,
    "per_page": 30,
    "page": 1,
    "results": [...]
  },
  "total_results": 42,
  "per_page": 30,
  "page": 1
}
```

### `list-species` Output

```json
{
  "query": {
    "region": "Oregon",
    "place_id": 10,
    "time_period": "last month",
    "start_date": "2025-09-03",
    "end_date": "2025-10-03"
  },
  "species_count": 1234,
  "total_observations": 5678,
  "species": [
    {
      "id": 12345,
      "name": "Canis lupus",
      "preferred_common_name": "Gray Wolf",
      "rank": "species",
      "observation_count": 15
    }
  ]
}
```

## Library Components

- **`iNatClient`**: Core API client for iNaturalist
- **`SpeciesQuery`**: Main query interface
- **`parse_time_period()`**: Time period parsing utilities
- **CLI**: Command-line interface

## Use Cases

- **Invasive Species Monitoring**: Detect when non-native species first appear in new regions
- **Biodiversity Research**: Track species distribution changes over time
- **Citizen Science**: Analyze iNaturalist observation patterns
- **Conservation**: Monitor protected species presence

## Implementation Details

### Efficient API Usage
The system uses iNaturalist's `species_counts` endpoint for efficient querying:
1. Fetches all species in the current period (a few API calls with pagination)
2. For each species, checks historical presence (1 API call per species)
3. Respects rate limits: 60-100 requests/minute per [iNaturalist API guidelines](https://www.inaturalist.org/pages/api+recommended+practices)

### Rate Limiting
- Default: 1.0 second between requests (60 req/min)
- Recommended max: 0.6 seconds (100 req/min)
- Automatically adjusts on errors with exponential backoff

## Limitations

- "New" species detection is relative to available iNaturalist data, not actual species establishment
- Performance scales with number of unique species in the time period
- Subject to iNaturalist API rate limits (can take hours for large queries)
- Geographic boundaries depend on iNaturalist's place database
- Lookback period is limited to available historical data (iNaturalist started ~2008)

## Contributing

This is a prototype library. Future enhancements could include:
- Caching for place and taxon lookups
- Batch processing for multiple species
- Geographic boundary file support
- Web-based interface
- Advanced statistical analysis

