# iNaturalist Difference Detection

A Python library and CLI tool for querying iNaturalist observations to detect species presence patterns across regions and time periods. Designed for invasive species monitoring and biodiversity research.

## Features

- Query species observations by region and time period
- Detect potentially "new" species in regions (no previous observations)
- List all species observed in a region during a time period
- Support for flexible time period formats
- Command-line interface and Python library

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

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