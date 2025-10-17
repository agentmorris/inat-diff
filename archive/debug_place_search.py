from inat_diff.client import iNatClient

def main():
    client = iNatClient()

    print("=== All places found for 'Montana' ===")
    places = client.search_places("Montana")

    for i, place in enumerate(places):
        print(f"{i+1}. ID: {place.get('id')}, Name: '{place.get('name')}', "
              f"Display: '{place.get('display_name')}', Type: {place.get('place_type')}")

    print(f"\nTotal places found: {len(places)}")

if __name__ == "__main__":
    main()