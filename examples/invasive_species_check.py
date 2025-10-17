#!/usr/bin/env python3
"""
Example: Checking for potentially invasive species in Oregon.
This demonstrates the core use case of detecting species that appear
to be new to a region.
"""

from inat_diff import SpeciesQuery

def main():
    """Check for species that might be new invasives."""
    query = SpeciesQuery()

    # Example invasive species to monitor
    species_to_check = [
        ("Python bivittatus", "Burmese Python"),
        ("Myocastor coypus", "Nutria"),
        ("Linepithema humile", "Argentine Ant"),
        ("Dreissena polymorpha", "Zebra Mussel"),
    ]

    print("Invasive Species Monitoring - Oregon")
    print("=" * 60)
    print("Checking for species observed this month with no prior history\n")

    for latin_name, common_name in species_to_check:
        print(f"\n{common_name} ({latin_name}):")
        print("-" * 40)

        try:
            results = query.find_new_species_in_period(
                taxon_name=latin_name,
                time_period="this month",
                region="Oregon",
                lookback_years=10
            )

            print(f"  Current observations: {results['total_results']}")

            if results['is_new_to_region']:
                print(f"  ⚠️  NEW TO REGION - First observations this month!")
                print(f"  No observations in previous 10 years")
            else:
                historical_count = results['historical_observations']['total_results']
                print(f"  Historical observations (last 10 years): {historical_count}")
                print(f"  Status: Previously established")

        except Exception as e:
            print(f"  Error checking species: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()