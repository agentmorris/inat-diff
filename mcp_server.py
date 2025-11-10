#!/usr/bin/env python3
"""
iNaturalist Difference Detection MCP Server

A Model Context Protocol server that provides tools for invasive species monitoring
and biodiversity research through iNaturalist data.
"""

import asyncio
import json
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from inat_diff import SpeciesQuery
from inat_diff.exceptions import iNatAPIError, PlaceNotFoundError, TaxonNotFoundError
from inat_diff.visualize import (
    generate_new_species_html,
    generate_list_species_html,
    generate_query_html,
    annotate_species_with_quality,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inat-mcp-server")

# Initialize the server
app = Server("inat-diff")

# Initialize the query engine
query_engine = SpeciesQuery()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for iNaturalist data querying."""
    return [
        Tool(
            name="find_new_species_in_region",
            description=(
                "Find all species that appear to be new to a region during a time period. "
                "This is the main tool for invasive species monitoring - it identifies species "
                "observed recently that have no prior observations in the lookback period. "
                "Perfect for questions like: 'What new species appeared in Oregon this month?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": (
                            "Geographic region name (e.g., 'Oregon', 'California', 'Kenya', "
                            "'Multnomah County'). Can be a country, state, county, or other place "
                            "recognized by iNaturalist."
                        ),
                    },
                    "time_period": {
                        "type": "string",
                        "description": (
                            "Time period to check for new observations. Examples: 'last 30 days', "
                            "'this month', 'last month', 'this year', 'last year', 'last week', 'past 6 months', "
                            "'2024-01-01 to 2024-12-31'"
                        ),
                    },
                    "lookback_years": {
                        "type": "integer",
                        "description": (
                            "Number of years to look back for historical data. Species with no "
                            "observations in this lookback period are considered 'new'. "
                            "Default: 20 years (recommended). Minimum: 1, Maximum: 50"
                        ),
                        "default": 20,
                        "minimum": 1,
                        "maximum": 50,
                    },
                    "rate_limit": {
                        "type": "number",
                        "description": (
                            "Seconds to wait between API calls to iNaturalist. "
                            "Default: 1.2 (50 requests/min). Range: 0.6-2.0. "
                            "Lower = faster but may hit rate limits."
                        ),
                        "default": 1.2,
                        "minimum": 0.6,
                        "maximum": 2.0,
                    },
                    "output_format": {
                        "type": "string",
                        "description": (
                            "Output format for the results. 'markdown' returns formatted text, "
                            "'html' returns a styled HTML report. Default: 'markdown'."
                        ),
                        "enum": ["markdown", "html"],
                        "default": "markdown",
                    },
                },
                "required": ["region", "time_period"],
            },
        ),
        Tool(
            name="check_if_species_is_new",
            description=(
                "Check if a specific species is new to a region. Returns whether the species "
                "was observed during the time period and if it has any prior historical observations. "
                "Use this when you want to check a specific species rather than finding all new species."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "species_name": {
                        "type": "string",
                        "description": (
                            "Latin (scientific) name of the species to check. "
                            "Examples: 'Python bivittatus' (Burmese Python), "
                            "'Canis lupus' (Gray Wolf), 'Panthera leo' (Lion)"
                        ),
                    },
                    "region": {
                        "type": "string",
                        "description": (
                            "Geographic region name (e.g., 'Florida', 'Oregon', 'Kenya'). "
                            "Can be a country, state, county, or other place recognized by iNaturalist."
                        ),
                    },
                    "time_period": {
                        "type": "string",
                        "description": (
                            "Time period to check for observations. Examples: 'this year', 'last year', "
                            "'last 6 months', 'this month', 'last month', '2024-01-01 to 2024-12-31'"
                        ),
                    },
                    "lookback_years": {
                        "type": "integer",
                        "description": (
                            "Number of years to look back for historical data. Default: 20 years."
                        ),
                        "default": 20,
                        "minimum": 1,
                        "maximum": 50,
                    },
                    "output_format": {
                        "type": "string",
                        "description": (
                            "Output format for the results. 'markdown' returns formatted text, "
                            "'html' returns a styled HTML report. Default: 'markdown'."
                        ),
                        "enum": ["markdown", "html"],
                        "default": "markdown",
                    },
                },
                "required": ["species_name", "region", "time_period"],
            },
        ),
        Tool(
            name="list_species_in_region",
            description=(
                "List all species observed in a region during a specific time period. "
                "Returns species counts and names. Useful for getting an overview of biodiversity "
                "in a region without filtering for 'new' species."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": (
                            "Geographic region name (e.g., 'Oregon', 'California', 'Kenya')."
                        ),
                    },
                    "time_period": {
                        "type": "string",
                        "description": (
                            "Time period to query. Examples: 'last month', 'this month', 'this year', 'last year', "
                            "'last 30 days', '2024-01-01 to 2024-06-30'"
                        ),
                    },
                    "output_format": {
                        "type": "string",
                        "description": (
                            "Output format for the results. 'markdown' returns formatted text, "
                            "'html' returns a styled HTML report. Default: 'markdown'."
                        ),
                        "enum": ["markdown", "html"],
                        "default": "markdown",
                    },
                },
                "required": ["region", "time_period"],
            },
        ),
        Tool(
            name="query_species_observations",
            description=(
                "Query detailed observations for a specific species in a region and time period. "
                "Returns individual observation records (up to 200 per page). "
                "Use this when you need detailed observation data rather than just counts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "species_name": {
                        "type": "string",
                        "description": (
                            "Latin (scientific) name of the species. "
                            "Examples: 'Canis lupus', 'Panthera leo'"
                        ),
                    },
                    "region": {
                        "type": "string",
                        "description": "Geographic region name.",
                    },
                    "time_period": {
                        "type": "string",
                        "description": (
                            "Time period to query. Examples: 'last 30 days', 'this month', 'last month', 'this year'"
                        ),
                    },
                },
                "required": ["species_name", "region", "time_period"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for iNaturalist queries."""
    try:
        if name == "find_new_species_in_region":
            return await find_new_species_in_region(arguments)
        elif name == "check_if_species_is_new":
            return await check_if_species_is_new(arguments)
        elif name == "list_species_in_region":
            return await list_species_in_region(arguments)
        elif name == "query_species_observations":
            return await query_species_observations(arguments)
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]
    except PlaceNotFoundError as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Place not found: {str(e)}\n\nTip: Try using more specific place names like 'Oregon' instead of 'OR', or check https://www.inaturalist.org/places",
            )
        ]
    except TaxonNotFoundError as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Species not found: {str(e)}\n\nTip: Use Latin scientific names (e.g., 'Canis lupus' instead of 'wolf')",
            )
        ]
    except iNatAPIError as e:
        return [
            TextContent(
                type="text",
                text=f"❌ iNaturalist API error: {str(e)}",
            )
        ]
    except Exception as e:
        logger.exception(f"Error processing tool call {name}")
        return [
            TextContent(
                type="text",
                text=f"❌ Unexpected error: {str(e)}",
            )
        ]


async def find_new_species_in_region(arguments: dict) -> list[TextContent]:
    """Find all new species in a region during a time period."""
    region = arguments["region"]
    time_period = arguments["time_period"]
    lookback_years = arguments.get("lookback_years", 20)
    rate_limit = arguments.get("rate_limit", 1.2)
    output_format = arguments.get("output_format", "markdown")

    logger.info(
        f"Finding new species in {region} during {time_period} "
        f"(lookback: {lookback_years} years, rate limit: {rate_limit}s, format: {output_format})"
    )

    # Run the query in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: query_engine.find_all_new_species_in_period(
            time_period=time_period,
            region=region,
            lookback_years=lookback_years,
            rate_limit=rate_limit,
            verbose=True,
        ),
    )

    # Generate HTML if requested
    if output_format == "html":
        html_output = generate_new_species_html(results, include_quality=True, rate_limit=rate_limit)
        return [
            TextContent(
                type="text",
                text=html_output,
            )
        ]

    # Otherwise, format as markdown (default)
    new_count = results["new_species_count"]
    total_count = results["total_species_in_period"]
    established_count = results["established_species_count"]

    response_lines = [
        f"# New Species in {results['query']['place_display_name']}",
        f"",
        f"**Period:** {time_period} ({results['query']['start_date']} to {results['query']['end_date']})",
        f"**Lookback:** {lookback_years} years ({results['lookback_period']})",
        f"",
        f"## Summary",
        f"- **Total species observed:** {total_count}",
        f"- **New species (no prior observations):** {new_count}",
        f"- **Established species:** {established_count}",
        f"",
    ]

    if new_count > 0:
        response_lines.append(f"## New Species ({new_count})")
        response_lines.append("")

        new_species = results["new_species"]

        # Annotate species with quality grades
        place_id = results["query"].get("place_id")
        annotate_species_with_quality(new_species, place_id, rate_limit=rate_limit)

        # Show first 50 new species
        for i, species in enumerate(new_species[:50], 1):
            name = species.get("name", "Unknown")
            common = species.get("preferred_common_name")
            count = species.get("observation_count", 0)
            rank = species.get("rank", "")
            taxon_id = species.get("id")
            quality = species.get("highest_quality_grade_label", "Unknown")

            inat_url = f"https://www.inaturalist.org/taxa/{taxon_id}"

            if common:
                response_lines.append(
                    f"{i}. **{name}** ({common}) - {count} observations [{rank}] - Quality: {quality}"
                )
            else:
                response_lines.append(
                    f"{i}. **{name}** - {count} observations [{rank}] - Quality: {quality}"
                )
            response_lines.append(f"   - View on iNaturalist: {inat_url}")

        if len(new_species) > 50:
            response_lines.append(f"")
            response_lines.append(f"*... and {len(new_species) - 50} more species*")
    else:
        response_lines.append("✓ No new species found in this period.")

    response_lines.append("")
    response_lines.append("---")
    response_lines.append(
        f"*Note: 'New' means no observations in the {lookback_years}-year lookback period. "
        "This doesn't necessarily mean the species is truly invasive or newly arrived.*"
    )

    return [
        TextContent(
            type="text",
            text="\n".join(response_lines),
        )
    ]


async def check_if_species_is_new(arguments: dict) -> list[TextContent]:
    """Check if a specific species is new to a region."""
    species_name = arguments["species_name"]
    region = arguments["region"]
    time_period = arguments["time_period"]
    lookback_years = arguments.get("lookback_years", 20)
    output_format = arguments.get("output_format", "markdown")

    logger.info(
        f"Checking if {species_name} is new to {region} in {time_period} "
        f"(lookback: {lookback_years} years, format: {output_format})"
    )

    # Run the query in a thread pool
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: query_engine.find_new_species_in_period(
            taxon_name=species_name,
            time_period=time_period,
            region=region,
            lookback_years=lookback_years,
        ),
    )

    # Generate HTML if requested
    if output_format == "html":
        html_output = generate_query_html(results)
        return [
            TextContent(
                type="text",
                text=html_output,
            )
        ]

    # Otherwise, format as markdown (default)
    is_new = results.get("is_new_to_region", False)
    current_count = results.get("total_results", 0)
    historical_count = results.get("historical_observations", {}).get("total_results", 0)
    analysis = results.get("analysis", "")

    taxon_id = results["query"]["taxon_id"]
    place_id = results["query"]["place_id"]

    inat_taxon_url = f"https://www.inaturalist.org/taxa/{taxon_id}"
    inat_obs_url = f"https://www.inaturalist.org/observations?taxon_id={taxon_id}&place_id={place_id}"

    response_lines = [
        f"# Species Check: {species_name}",
        f"",
        f"**Region:** {region}",
        f"**Period:** {time_period} ({results['query']['start_date']} to {results['query']['end_date']})",
        f"**Lookback:** {lookback_years} years ({results['lookback_period']})",
        f"",
        f"## Results",
        f"",
    ]

    if current_count == 0:
        response_lines.append(f"❌ **No observations found** in the specified period.")
    elif is_new:
        response_lines.append(f"⚠️  **NEW TO REGION**")
        response_lines.append(f"")
        response_lines.append(f"- Current observations: **{current_count}**")
        response_lines.append(f"- Historical observations: **0** (no prior records)")
        response_lines.append(f"")
        response_lines.append(f"**Analysis:** {analysis}")
    else:
        response_lines.append(f"✓ **Previously Established**")
        response_lines.append(f"")
        response_lines.append(f"- Current observations: **{current_count}**")
        response_lines.append(f"- Historical observations: **{historical_count}**")
        response_lines.append(f"")
        response_lines.append(f"**Analysis:** {analysis}")

    response_lines.append(f"")
    response_lines.append(f"## Links")
    response_lines.append(f"- Species page: {inat_taxon_url}")
    response_lines.append(f"- Observations in region: {inat_obs_url}")

    return [
        TextContent(
            type="text",
            text="\n".join(response_lines),
        )
    ]


async def list_species_in_region(arguments: dict) -> list[TextContent]:
    """List all species in a region during a time period."""
    region = arguments["region"]
    time_period = arguments["time_period"]
    output_format = arguments.get("output_format", "markdown")

    logger.info(f"Listing species in {region} during {time_period} (format: {output_format})")

    # Run the query in a thread pool
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: query_engine.get_all_species_in_period(
            time_period=time_period,
            region=region,
            page_limit=None,  # Fetch all
        ),
    )

    # Generate HTML if requested
    if output_format == "html":
        html_output = generate_list_species_html(results, include_quality=True, rate_limit=1.2)
        return [
            TextContent(
                type="text",
                text=html_output,
            )
        ]

    # Otherwise, format as markdown (default)
    species_count = results["species_count"]
    total_obs = results["total_observations"]
    species_list = results["species"]

    response_lines = [
        f"# Species in {region}",
        f"",
        f"**Period:** {time_period} ({results['query']['start_date']} to {results['query']['end_date']})",
        f"",
        f"## Summary",
        f"- **Unique species:** {species_count}",
        f"- **Total observations:** {total_obs}",
        f"",
    ]

    if species_count > 0:
        response_lines.append(f"## Species List")
        response_lines.append("")

        # Annotate species with quality grades
        place_id = results["query"].get("place_id")
        annotate_species_with_quality(species_list, place_id, rate_limit=1.2)

        # Show first 100 species
        for i, species in enumerate(species_list[:100], 1):
            name = species.get("name", "Unknown")
            common = species.get("preferred_common_name")
            count = species.get("observation_count", 0)
            rank = species.get("rank", "")
            quality = species.get("highest_quality_grade_label", "Unknown")

            if common:
                response_lines.append(
                    f"{i}. **{name}** ({common}) - {count} obs. [{rank}] - Quality: {quality}"
                )
            else:
                response_lines.append(f"{i}. **{name}** - {count} obs. [{rank}] - Quality: {quality}")

        if species_count > 100:
            response_lines.append(f"")
            response_lines.append(f"*... and {species_count - 100} more species*")
    else:
        response_lines.append("No species found in this period.")

    return [
        TextContent(
            type="text",
            text="\n".join(response_lines),
        )
    ]


async def query_species_observations(arguments: dict) -> list[TextContent]:
    """Query observations for a specific species."""
    species_name = arguments["species_name"]
    region = arguments["region"]
    time_period = arguments["time_period"]

    logger.info(
        f"Querying observations for {species_name} in {region} during {time_period}"
    )

    # Run the query in a thread pool
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: query_engine.query_species_in_period(
            taxon_name=species_name,
            time_period=time_period,
            region=region,
        ),
    )

    total = results["total_results"]
    taxon_id = results["query"]["taxon_id"]
    place_id = results["query"]["place_id"]

    inat_url = f"https://www.inaturalist.org/observations?taxon_id={taxon_id}&place_id={place_id}"

    response_lines = [
        f"# Observations: {species_name}",
        f"",
        f"**Region:** {region}",
        f"**Period:** {time_period} ({results['query']['start_date']} to {results['query']['end_date']})",
        f"",
        f"**Total observations:** {total}",
        f"",
        f"View all observations on iNaturalist: {inat_url}",
    ]

    return [
        TextContent(
            type="text",
            text="\n".join(response_lines),
        )
    ]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting iNaturalist Difference Detection MCP Server")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
