from inat_diff.client import iNatClient
from inat_diff.utils import parse_time_period

def main():
    client = iNatClient()

    # Check what "Montana" resolves to
    print("=== Place Resolution Debug ===")
    try:
        place_id, place_info = client.resolve_place_with_info("Montana")
        print(f"'Montana' resolved to:")
        print(f"  Place ID: {place_id}")
        print(f"  Name: {place_info['name']}")
        print(f"  Display Name: {place_info['display_name']}")
        print(f"  Place Type: {place_info['place_type']}")
        print(f"  Matched As: {place_info['matched_as']}")
        print()

        # Show what place ID 16 is
        print("=== Expected Montana (place_id=16) ===")
        montana_info = client.get_place(16)
        print(f"Place ID 16:")
        print(f"  Name: {montana_info.get('name')}")
        print(f"  Display Name: {montana_info.get('display_name')}")
        print(f"  Place Type: {montana_info.get('place_type')}")
        print()

        # Check taxon resolution
        print("=== Taxon Resolution Debug ===")
        taxon_id = client.resolve_taxon("Canis lupus")
        print(f"'Canis lupus' resolved to taxon ID: {taxon_id}")
        print(f"Expected taxon ID: 42048")
        print()

        # Check time period parsing
        print("=== Time Period Debug ===")
        start_date, end_date = parse_time_period("last 6 months")
        print(f"'last 6 months' parsed to: {start_date} to {end_date}")
        print()

        # Now let's test with the correct place ID
        print("=== Testing with place_id=16 directly ===")
        obs_correct = client.get_observations(
            place_id=16,
            taxon_id=42048,
            d1=start_date,
            d2=end_date,
            per_page=5
        )
        print(f"Observations with place_id=16: {obs_correct.get('total_results', 0)}")

        # Test with resolved place ID
        print(f"=== Testing with resolved place_id={place_id} ===")
        obs_resolved = client.get_observations(
            place_id=place_id,
            taxon_id=42048,
            d1=start_date,
            d2=end_date,
            per_page=5
        )
        print(f"Observations with place_id={place_id}: {obs_resolved.get('total_results', 0)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()