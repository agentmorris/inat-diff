#!/usr/bin/env python3
"""Example usage of the inat-diff library."""

from inat_diff import SpeciesQuery, iNatAPIError

def main():
    """Run example queries."""
    print("iNaturalist Difference Detection - Example Usage")
    print("=" * 50)

    # Initialize query engine
    query = SpeciesQuery()

    try:
        # Example 1: Query specific species
        print("\n1. Querying observations of 'Canis lupus' in Montana (last 6 months)")
        results = query.query_species_in_period(
            taxon_name="Canis lupus",
            time_period="last 6 months",
            region="Montana"
        )
        print(f"Found {results['total_results']} observations")
        print(f"Region: {results['place_info'].get('name', 'Unknown')}")

        # Example 2: Check for new species
        print("\n2. Checking if 'Python bivittatus' is new to Florida this year")
        new_results = query.find_new_species_in_period(
            taxon_name="Python bivittatus",
            time_period="this year",
            region="Florida",
            lookback_years=10
        )
        print(f"New to region: {new_results['is_new_to_region']}")
        print(f"Current observations: {new_results['total_results']}")
        print(f"Historical observations: {new_results['historical_observations']['total_results']}")

        # Example 3: List species in a region
        print("\n3. Listing species observed in Oregon (last 30 days)")
        species_list = query.get_all_species_in_period(
            time_period="last 30 days",
            region="Oregon",
            page_limit=2
        )
        print(f"Found {species_list['species_count']} unique species")
        print(f"Total observations: {species_list['total_observations']}")

        print("\nTop 5 species:")
        for species in species_list['species'][:5]:
            name = species['name']
            common = species.get('preferred_common_name', '')
            count = species['observation_count']
            if common:
                print(f"  {name} ({common}): {count} observations")
            else:
                print(f"  {name}: {count} observations")

    except iNatAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\n" + "=" * 50)
    print("Example completed. Try the CLI: inat-diff --help")

if __name__ == "__main__":
    main()