from inat_diff.client import iNatClient

def main():
    client = iNatClient()

    print("=== Place types for Montana results ===")
    places = client.search_places("Montana")

    for place in places:
        if place.get('name') == 'Montana':
            place_id = place.get('id')
            detailed = client.get_place(place_id)
            print(f"Place ID {place_id}: {place.get('display_name')}")
            print(f"  place_type: {place.get('place_type')} (from search)")
            print(f"  place_type_name: {detailed.get('place_type_name')} (from detailed)")
            print(f"  admin_level: {detailed.get('admin_level')}")
            print()

if __name__ == "__main__":
    main()