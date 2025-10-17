from inat_diff import SpeciesQuery, iNatAPIError

def main():

    # Initialize query engine
    query = SpeciesQuery()

    try:
        print("\n1. Querying observations of 'Canis lupus' in Montana (last 6 months)")
        results = query.query_species_in_period(
            taxon_name="Canis lupus",
            time_period="last 6 months",
            region="Montana"
        )
        print(f"Found {results['total_results']} observations")
        print(f"Region: {results['place_info'].get('name', 'Unknown')}")

    except iNatAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
