#!/usr/bin/env python3
"""
Test script to demonstrate the place resolution fix.
This shows how "Portland, Oregon" was being incorrectly resolved.
"""

from inat_diff import SpeciesQuery

def main():
    query = SpeciesQuery()

    print("Testing place resolution for 'Portland, Oregon':")
    print("=" * 60)

    # Use the new method to see what place was resolved
    place_id, place_info = query.client.resolve_place_with_info("Portland, Oregon")

    print(f"\nInput: 'Portland, Oregon'")
    print(f"Resolved to: {place_info['display_name']}")
    print(f"Place ID: {place_info['id']}")
    print(f"Match type: {place_info['matched_as']}")

    if place_info['matched_as'] == 'fallback (first result)':
        print("\n⚠️  WARNING: This is a fallback match!")
        print("   The place name you searched for doesn't exactly match what was found.")
        print("   Consider using a more specific place name like 'Multnomah County'")

    print("\n" + "=" * 60)
    print("\nFor better results searching Portland area, try:")
    print("  - 'Multnomah County' (the county containing Portland)")
    print("  - 'Oregon' (the entire state)")
    print("\nThe iNaturalist API returned a small botanical garden instead")
    print("of the city, which explains why many species appear 'new'.")

if __name__ == "__main__":
    main()
