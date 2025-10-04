"""Main query functionality for species detection."""

from typing import List, Dict, Any, Optional
from .client import iNatClient
from .utils import parse_time_period, normalize_taxon_name
from .exceptions import iNatAPIError


class SpeciesQuery:
    """Main class for querying species observations and detecting patterns."""

    def __init__(self, client: Optional[iNatClient] = None):
        """Initialize with an optional client instance."""
        self.client = client or iNatClient()

    def query_species_in_period(self,
                               taxon_name: str,
                               time_period: str,
                               region: str,
                               include_subspecies: bool = True) -> Dict[str, Any]:
        """
        Query for species observations in a specific time period and region.

        Args:
            taxon_name: Latin name of the taxon to search for
            time_period: Time period string (e.g., "last 30 days", "this month")
            region: Name of the region (country, state, county)
            include_subspecies: Whether to include subspecies in results

        Returns:
            Dictionary containing query results and metadata
        """
        # Parse inputs
        normalized_taxon = normalize_taxon_name(taxon_name)
        start_date, end_date = parse_time_period(time_period)

        # Resolve place and taxon IDs
        place_id = self.client.resolve_place(region)
        taxon_id = self.client.resolve_taxon(normalized_taxon)

        # Get observations for the specified period
        observations = self.client.get_observations(
            place_id=place_id,
            taxon_id=taxon_id,
            d1=start_date,
            d2=end_date
        )

        # Get species information
        place_info = self.client.get_place(place_id)

        return {
            "query": {
                "taxon_name": normalized_taxon,
                "taxon_id": taxon_id,
                "region": region,
                "place_id": place_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date
            },
            "place_info": place_info,
            "observations": observations,
            "total_results": observations.get("total_results", 0),
            "per_page": observations.get("per_page", 0),
            "page": observations.get("page", 1)
        }

    def find_new_species_in_period(self,
                                  taxon_name: str,
                                  time_period: str,
                                  region: str,
                                  lookback_years: int = 20) -> Dict[str, Any]:
        """
        Find if a species has appeared in a region during a time period
        when it was not previously observed.

        Args:
            taxon_name: Latin name of the taxon to search for
            time_period: Recent time period to check
            region: Name of the region
            lookback_years: How many years to look back for historical data

        Returns:
            Dictionary with results and analysis
        """
        from datetime import datetime, timedelta

        # Get current period observations
        current_results = self.query_species_in_period(taxon_name, time_period, region)

        if current_results["total_results"] == 0:
            return {
                **current_results,
                "historical_observations": {"total_results": 0},
                "is_new_to_region": False,
                "lookback_period": "N/A",
                "analysis": "No observations found in the specified period"
            }

        # Check historical presence
        start_date, end_date = parse_time_period(time_period)
        historical_end = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
        historical_start = historical_end - timedelta(days=365 * lookback_years)

        historical_observations = self.client.get_observations(
            place_id=current_results["query"]["place_id"],
            taxon_id=current_results["query"]["taxon_id"],
            d1=historical_start.strftime("%Y-%m-%d"),
            d2=historical_end.strftime("%Y-%m-%d")
        )

        is_new = historical_observations.get("total_results", 0) == 0

        return {
            **current_results,
            "historical_observations": historical_observations,
            "is_new_to_region": is_new,
            "lookback_period": f"{historical_start.strftime('%Y-%m-%d')} to {historical_end.strftime('%Y-%m-%d')}",
            "analysis": (
                f"Species appears to be NEW to {region} in the specified period. "
                f"No observations found in the previous {lookback_years} years."
                if is_new else
                f"Species was previously observed in {region}. "
                f"Found {historical_observations.get('total_results', 0)} historical observations."
            )
        }

    def get_all_species_in_period(self,
                                 time_period: str,
                                 region: str,
                                 page_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all species observed in a region during a time period.

        Args:
            time_period: Time period string
            region: Name of the region
            page_limit: Maximum number of pages to fetch (None = fetch all pages)

        Returns:
            Dictionary with all species found
        """
        start_date, end_date = parse_time_period(time_period)
        place_id = self.client.resolve_place(region)

        all_observations = []
        page = 1

        while page_limit is None or page <= page_limit:
            observations = self.client.get_observations(
                place_id=place_id,
                d1=start_date,
                d2=end_date,
                page=page,
                per_page=200
            )

            results = observations.get("results", [])
            if not results:
                break

            all_observations.extend(results)
            page += 1

        # Extract unique species
        unique_species = {}
        for obs in all_observations:
            taxon = obs.get("taxon")
            if taxon and taxon.get("id"):
                species_id = taxon["id"]
                if species_id not in unique_species:
                    unique_species[species_id] = {
                        "id": species_id,
                        "name": taxon.get("name"),
                        "preferred_common_name": taxon.get("preferred_common_name"),
                        "rank": taxon.get("rank"),
                        "observation_count": 0
                    }
                unique_species[species_id]["observation_count"] += 1

        return {
            "query": {
                "region": region,
                "place_id": place_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date
            },
            "species_count": len(unique_species),
            "total_observations": len(all_observations),
            "species": list(unique_species.values())
        }

    def find_all_new_species_in_period(self,
                                       time_period: str,
                                       region: str,
                                       lookback_years: int = 20,
                                       rate_limit: float = 1.2,  # iNaturalist API limit: 60-100 req/min (https://www.inaturalist.org/pages/api+recommended+practices)
                                                                 # 1.2 seconds = 50 req/min, conservative to avoid throttling
                                       verbose: bool = False) -> Dict[str, Any]:
        """
        Find all species that appear to be new to a region during a time period.

        This is the main use case: "what new species have been seen this month
        in Oregon that have not previously been observed in Oregon?"

        Uses the efficient species_counts endpoint to minimize API calls.

        Args:
            time_period: Recent time period to check
            region: Name of the region
            lookback_years: How many years to look back for historical data
            rate_limit: Seconds to wait between API calls (default: 1.0 = 60 req/min)
            verbose: Print progress information

        Returns:
            Dictionary with new species found and analysis
        """
        from datetime import datetime, timedelta
        import time
        import sys

        # Parse dates
        start_date, end_date = parse_time_period(time_period)
        historical_end = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
        historical_start = historical_end - timedelta(days=365 * lookback_years)

        place_id = self.client.resolve_place(region)

        if verbose:
            print(f"Fetching species observed in {region} during {time_period}...", file=sys.stderr)

        # Step 1: Get all species in the current period using species_counts
        current_species_map = {}
        page = 1
        no_more_results = False

        while not no_more_results:
            max_retries = 5
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    counts = self.client.get_species_counts(
                        place_id=place_id,
                        d1=start_date,
                        d2=end_date,
                        per_page=500,
                        page=page
                    )

                    results = counts.get("results", [])
                    if not results:
                        # No more results, exit pagination loop
                        no_more_results = True
                        success = True
                        break

                    for taxon in results:
                        taxon_id = taxon.get("taxon", {}).get("id")
                        if taxon_id:
                            current_species_map[taxon_id] = {
                                "id": taxon_id,
                                "name": taxon.get("taxon", {}).get("name"),
                                "preferred_common_name": taxon.get("taxon", {}).get("preferred_common_name"),
                                "rank": taxon.get("taxon", {}).get("rank"),
                                "iconic_taxon": taxon.get("taxon", {}).get("iconic_taxon_name"),
                                "observation_count": taxon.get("count", 0)
                            }

                    success = True
                    page += 1
                    time.sleep(rate_limit)

                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        backoff_time = rate_limit * (2 ** retry_count)
                        if verbose:
                            print(f"  Error fetching current species (page {page}): {e}", file=sys.stderr)
                            print(f"  Retrying in {backoff_time:.1f}s (attempt {retry_count}/{max_retries})...", file=sys.stderr)
                        time.sleep(backoff_time)
                    else:
                        error_msg = f"Failed to fetch current species (page {page}) after {max_retries} retries: {e}"
                        if verbose:
                            print(f"  {error_msg}", file=sys.stderr)
                        raise iNatAPIError(error_msg)

        total_species = len(current_species_map)
        if verbose:
            print(f"Found {total_species} species in current period", file=sys.stderr)
            print(f"Checking each for historical presence (this may take a while)...", file=sys.stderr)
            est_time = total_species * rate_limit / 60
            print(f"Estimated time: {est_time:.1f} minutes at {rate_limit}s per request", file=sys.stderr)

        # Step 2: Check each species for historical presence
        new_species = []
        established_species = []

        for idx, (taxon_id, species) in enumerate(current_species_map.items(), 1):
            if verbose and idx % 25 == 0:
                print(f"  Progress: {idx}/{total_species} ({100*idx/total_species:.1f}%)", file=sys.stderr)

            # Retry logic with exponential backoff
            max_retries = 5
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    # Use species_counts to check historical presence (more efficient than observations)
                    historical_counts = self.client.get_species_counts(
                        place_id=place_id,
                        taxon_id=taxon_id,
                        d1=historical_start.strftime("%Y-%m-%d"),
                        d2=historical_end.strftime("%Y-%m-%d"),
                        per_page=1
                    )

                    # Check if this taxon has any historical observations
                    historical_results = historical_counts.get("results", [])
                    has_history = len(historical_results) > 0 and historical_results[0].get("count", 0) > 0

                    species_info = {
                        **species,
                        "historical_count": historical_results[0].get("count", 0) if historical_results else 0
                    }

                    if not has_history:
                        new_species.append(species_info)
                    else:
                        established_species.append(species_info)

                    success = True
                    # Rate limiting
                    time.sleep(rate_limit)

                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        # Exponential backoff: 2, 4, 8, 16 seconds
                        backoff_time = rate_limit * (2 ** retry_count)
                        if verbose:
                            print(f"  Error checking {species.get('name', 'Unknown')}: {e}", file=sys.stderr)
                            print(f"  Retrying in {backoff_time:.1f}s (attempt {retry_count}/{max_retries})...", file=sys.stderr)
                        time.sleep(backoff_time)
                    else:
                        # Max retries exceeded - fail the entire operation
                        error_msg = f"Failed to check species '{species.get('name', 'Unknown')}' after {max_retries} retries: {e}"
                        if verbose:
                            print(f"  {error_msg}", file=sys.stderr)
                        raise iNatAPIError(error_msg)

        if verbose:
            print(f"Complete! Found {len(new_species)} new species", file=sys.stderr)

        return {
            "query": {
                "region": region,
                "place_id": place_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date
            },
            "lookback_period": f"{historical_start.strftime('%Y-%m-%d')} to {historical_end.strftime('%Y-%m-%d')}",
            "lookback_years": lookback_years,
            "total_species_in_period": total_species,
            "new_species_count": len(new_species),
            "established_species_count": len(established_species),
            "new_species": new_species,
            "established_species": established_species,
            "rate_limit_seconds": rate_limit
        }