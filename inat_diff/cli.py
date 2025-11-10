"""Command-line interface for iNaturalist difference detection."""

import argparse
import json
import sys
from typing import Dict, Any
from .query import SpeciesQuery
from .exceptions import iNatAPIError


def save_json_output(results: Dict[str, Any], output_file: str):
    """Save results to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


def format_results(results: Dict[str, Any]) -> str:
    """Format query results for text display."""
    # Text formatting
    output = []
    query = results.get("query", {})

    # Handle "find all new species" results
    if "new_species_count" in results:
        # Show place resolution info
        if query.get('place_display_name'):
            output.append(f"Region searched: {query.get('region', 'Unknown')}")
            output.append(f"Resolved to: {query.get('place_display_name', 'Unknown')} (ID: {query.get('place_id', 'Unknown')})")
            if query.get('place_matched_as') == 'fallback (first result)':
                output.append(f"⚠️  WARNING: No exact match found - using first search result")
            output.append("")
        else:
            output.append(f"Region: {query.get('region', 'Unknown')}")

        output.append(f"Period: {query.get('time_period', 'Unknown')} ({query.get('start_date')} to {query.get('end_date')})")
        output.append(f"Lookback: {results.get('lookback_years', 0)} years ({results.get('lookback_period', 'Unknown')})")
        output.append(f"\nTotal species in period: {results.get('total_species_in_period', 0)}")
        output.append(f"New species (no prior observations): {results.get('new_species_count', 0)}")
        output.append(f"Established species: {results.get('established_species_count', 0)}")

        new_species = results.get("new_species", [])
        if new_species:
            output.append(f"\n=== NEW SPECIES ({len(new_species)}) ===")
            for species in new_species[:20]:  # Show first 20
                name = species.get("name", "Unknown")
                common = species.get("preferred_common_name", "")
                count = species.get("observation_count", 0)
                rank = species.get("rank", "")
                if common:
                    output.append(f"  {name} ({common}) [{rank}]: {count} observations")
                else:
                    output.append(f"  {name} [{rank}]: {count} observations")
            if len(new_species) > 20:
                output.append(f"  ... and {len(new_species) - 20} more")
        return "\n".join(output)

    # Standard query output
    output.append(f"Query: {query.get('taxon_name', 'Unknown')} in {query.get('region', 'Unknown')}")
    output.append(f"Period: {query.get('time_period', 'Unknown')} ({query.get('start_date')} to {query.get('end_date')})")
    output.append(f"Total observations: {results.get('total_results', 0)}")

    if "is_new_to_region" in results:
        output.append(f"New to region: {'YES' if results['is_new_to_region'] else 'NO'}")
        output.append(f"Analysis: {results.get('analysis', 'No analysis available')}")

    if "species" in results:
        output.append(f"\nUnique species found: {results.get('species_count', 0)}")
        for species in results.get("species", [])[:10]:  # Show first 10
            name = species.get("name", "Unknown")
            common = species.get("preferred_common_name", "")
            count = species.get("observation_count", 0)
            if common:
                output.append(f"  {name} ({common}): {count} observations")
            else:
                output.append(f"  {name}: {count} observations")

    return "\n".join(output)


def cmd_query(args):
    """Handle the query command."""
    try:
        query = SpeciesQuery()
        results = query.query_species_in_period(
            taxon_name=args.taxon,
            time_period=args.period,
            region=args.region
        )

        # Save JSON if requested
        if args.output_file:
            save_json_output(results, args.output_file)
            print(f"Results saved to {args.output_file}", file=sys.stderr)

        # Always print text output to console
        print(format_results(results))
    except iNatAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_new_species(args):
    """Handle the new-species command."""
    try:
        query = SpeciesQuery()

        # If taxon is provided, check that specific species
        if args.taxon:
            results = query.find_new_species_in_period(
                taxon_name=args.taxon,
                time_period=args.period,
                region=args.region,
                lookback_years=args.lookback
            )
        else:
            # Otherwise, find all new species in the period
            results = query.find_all_new_species_in_period(
                time_period=args.period,
                region=args.region,
                lookback_years=args.lookback,
                rate_limit=args.rate_limit,
                verbose=True
            )

        # Save JSON if requested
        if args.output_file:
            save_json_output(results, args.output_file)
            print(f"Results saved to {args.output_file}", file=sys.stderr)

        # Always print text output to console
        print(format_results(results))
    except iNatAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_species(args):
    """Handle the list-species command."""
    try:
        query = SpeciesQuery()
        results = query.get_all_species_in_period(
            time_period=args.period,
            region=args.region,
            page_limit=None  # Fetch all pages
        )

        # Save JSON if requested
        if args.output_file:
            save_json_output(results, args.output_file)
            print(f"Results saved to {args.output_file}", file=sys.stderr)

        # Always print text output to console
        print(format_results(results))
    except iNatAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Query iNaturalist for species observation patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query specific species in region and time period
  inat-diff query "Panthera leo" "last 30 days" "Kenya"

  # Find ALL new species in a region during a time period
  inat-diff new-species "this month" "Oregon"

  # Check if a SPECIFIC species is new to a region
  inat-diff new-species "this year" "Florida" "Python bivittatus"

  # Customize lookback period and rate limiting
  inat-diff new-species "this month" "Oregon" --lookback-years 10 --rate-limit 0.6

  # List all species in a region during time period
  inat-diff list-species "last month" "Oregon"

Supported time periods:
  - "last N days/weeks/months/years"
  - "past N days/weeks/months/years"
  - "this month/year"
  - "last month/year"
  - "YYYY-MM-DD to YYYY-MM-DD"

Supported regions:
  - Countries: "United States", "Canada", "Kenya"
  - US States: "California", "Oregon", "Florida"
  - Other political boundaries as recognized by iNaturalist
        """
    )

    parser.add_argument("--output-file", "-o", type=str,
                       help="Save results to JSON file (console output remains in text format)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query for specific species observations")
    query_parser.add_argument("taxon", help="Taxon name (Latin name)")
    query_parser.add_argument("period", help="Time period")
    query_parser.add_argument("region", help="Geographic region")
    query_parser.add_argument("--output-file", "-o", type=str,
                             help="Save results to JSON file")
    query_parser.set_defaults(func=cmd_query)

    # New species command
    new_parser = subparsers.add_parser("new-species", help="Find new species in region (or check specific species)")
    new_parser.add_argument("period", help="Time period")
    new_parser.add_argument("region", help="Geographic region")
    new_parser.add_argument("taxon", nargs="?", help="Optional: specific taxon name (Latin name) to check")
    new_parser.add_argument("--lookback-years", type=int, default=20, dest="lookback",
                           help="Years to look back for historical data (default: 20)")
    new_parser.add_argument("--rate-limit", type=float, default=1.2, dest="rate_limit",
                           help="Seconds to wait between API calls (default: 1.2 = 50/min, iNat limit is 60-100/min)")
    new_parser.add_argument("--output-file", "-o", type=str,
                           help="Save results to JSON file")
    new_parser.set_defaults(func=cmd_new_species)

    # List species command
    list_parser = subparsers.add_parser("list-species", help="List all species in region/period")
    list_parser.add_argument("period", help="Time period")
    list_parser.add_argument("region", help="Geographic region")
    list_parser.add_argument("--output-file", "-o", type=str,
                            help="Save results to JSON file")
    list_parser.set_defaults(func=cmd_list_species)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()