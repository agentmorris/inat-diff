# Bug Fix: Place Resolution Validation

## Problem

When searching for "Portland, Oregon", the system reported golden digger wasps (Sphex ichneumoneus) as being new within the last 6 months, even though iNaturalist has many historical observations of this species in the Portland area.

## Root Cause

The bug was caused by incorrect place name resolution:

1. **User searched for:** "Portland, Oregon"
2. **System resolved to:** "Leach Botanical Garden, Portland, Oregon" (place_id: 128787)
   - This is a tiny community-curated botanical garden
   - Not the city of Portland itself
3. **Result:** Golden digger wasps have never been observed in this specific small garden historically (0 observations), even though they have 64+ observations in Multnomah County

### Why This Happened

- The iNaturalist API's `/places/autocomplete` endpoint only returned the botanical garden when querying "Portland, Oregon"
- The city of Portland doesn't exist as a separate place in iNaturalist's database
- The `resolve_place()` function fell back to using the first (and only) result
- **No validation was shown to users**, so they couldn't see that their search was resolved to the wrong place

## Solution Implemented

Added **place validation output** that shows users exactly what place was resolved:

### 1. New `resolve_place_with_info()` method
- Returns both place ID and detailed information about the match
- Includes match type (priority/exact/fallback)

### 2. Verbose output shows resolution details
When running queries, users now see:
```
Resolved 'Portland, Oregon' to:
  Place: Leach Botanical Garden, Portland, Oregon
  Place ID: 128787
  Match type: fallback (first result)
  ⚠️  WARNING: No exact match found, using first result
```

### 3. Console output includes warning
The final results now show:
```
Region searched: Portland, Oregon
Resolved to: Leach Botanical Garden, Portland, Oregon (ID: 128787)
⚠️  WARNING: No exact match found - using first search result
```

### 4. JSON output includes place info
The JSON results now include:
```json
{
  "query": {
    "region": "Portland, Oregon",
    "place_id": 128787,
    "place_name": "Leach Botanical Garden, Portland, Oregon",
    "place_display_name": "Leach Botanical Garden, Portland, Oregon",
    "place_matched_as": "fallback (first result)",
    ...
  }
}
```

## Verification

### Golden Digger Wasp Historical Counts:
- **Leach Botanical Garden** (128787): 0 observations (before last 6 months)
- **Multnomah County** (984): 64 observations (before last 6 months)

This explains why the species appeared as "new" to the botanical garden but not to the county.

## User Recommendations

For Portland, Oregon area searches, users should use:
- **"Multnomah County"** - the county containing Portland
- **"Oregon"** - the entire state

The city of Portland itself doesn't exist as a distinct administrative place in iNaturalist's database.

## Files Modified

1. `inat_diff/client.py`
   - Added `resolve_place_with_info()` method at lines 145-195

2. `inat_diff/query.py`
   - Updated `find_all_new_species_in_period()` to use new method at line 230
   - Added verbose place resolution output at lines 232-240
   - Included place info in return value at lines 378-380

3. `inat_diff/cli.py`
   - Updated `format_results()` to display place resolution info at lines 25-33
   - Added warning for fallback matches

## Testing

Run the test script to see the fix in action:
```bash
python3 test_place_resolution.py
```

Or run a real query:
```bash
inat-diff new-species "last 6 months" "Portland, Oregon" --lookback-years 20
```

The system will now warn you that "Portland, Oregon" was resolved to the botanical garden, allowing you to adjust your search accordingly.
