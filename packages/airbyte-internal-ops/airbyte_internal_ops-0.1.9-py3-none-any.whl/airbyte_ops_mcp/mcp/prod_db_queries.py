# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for querying the Airbyte Cloud Prod DB Replica.

This module provides MCP tools that wrap the query functions from
airbyte_ops_mcp.prod_db_access.queries for use by AI agents.
"""

from __future__ import annotations

from typing import Annotated, Any

import requests
from airbyte.exceptions import PyAirbyteInputError
from fastmcp import FastMCP
from pydantic import Field

from airbyte_ops_mcp.mcp._mcp_utils import mcp_tool, register_mcp_tools
from airbyte_ops_mcp.prod_db_access.queries import (
    query_actors_pinned_to_version,
    query_connections_by_connector,
    query_connector_versions,
    query_dataplanes_list,
    query_failed_sync_attempts_for_version,
    query_new_connector_releases,
    query_sync_results_for_version,
    query_workspace_info,
)

# Cloud UI base URL for building connection URLs
CLOUD_UI_BASE_URL = "https://cloud.airbyte.com"

# Cloud registry URL for resolving canonical names
CLOUD_REGISTRY_URL = (
    "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
)


def _resolve_canonical_name_to_definition_id(canonical_name: str) -> str:
    """Resolve a canonical source name to a definition ID.

    Args:
        canonical_name: Canonical source name (e.g., 'source-youtube-analytics').

    Returns:
        The source definition ID (UUID).

    Raises:
        PyAirbyteInputError: If the canonical name cannot be resolved.
    """
    response = requests.get(CLOUD_REGISTRY_URL, timeout=60)

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to fetch connector registry: {response.status_code}",
            context={"response": response.text},
        )

    data = response.json()
    sources = data.get("sources", [])

    # Normalize the canonical name for matching
    normalized_input = canonical_name.lower().strip()

    # Try exact match on name field
    for source in sources:
        source_name = source.get("name", "").lower()
        # The registry returns names like "YouTube Analytics"
        # So we need to handle both formats
        if source_name == normalized_input:
            return source["sourceDefinitionId"]

        # Also try matching against a slugified version
        # e.g., "YouTube Analytics" -> "youtube-analytics"
        slugified = source_name.replace(" ", "-")
        if slugified == normalized_input or f"source-{slugified}" == normalized_input:
            return source["sourceDefinitionId"]

    raise PyAirbyteInputError(
        message=f"Could not find source definition for canonical name: {canonical_name}",
        context={
            "hint": "Use the exact canonical name (e.g., 'source-youtube-analytics') "
            "or display name (e.g., 'YouTube Analytics'). "
            "You can list available sources using the connector registry tools.",
            "searched_for": canonical_name,
        },
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_dataplanes() -> list[dict[str, Any]]:
    """List all dataplane groups with workspace counts.

    Returns information about all active dataplane groups in Airbyte Cloud,
    including the number of workspaces in each. Useful for understanding
    the distribution of workspaces across regions (US, US-Central, EU).

    Returns list of dicts with keys: dataplane_group_id, dataplane_name,
    organization_id, enabled, tombstone, created_at, workspace_count
    """
    return query_dataplanes_list()


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_workspace_info(
    workspace_id: Annotated[
        str,
        Field(description="Workspace UUID to look up"),
    ],
) -> dict[str, Any] | None:
    """Get workspace information including dataplane group.

    Returns details about a specific workspace, including which dataplane
    (region) it belongs to. Useful for determining if a workspace is in
    the EU region for filtering purposes.

    Returns dict with keys: workspace_id, workspace_name, slug, organization_id,
    dataplane_group_id, dataplane_name, created_at, tombstone
    Or None if workspace not found.
    """
    return query_workspace_info(workspace_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_connector_versions(
    connector_definition_id: Annotated[
        str,
        Field(description="Connector definition UUID to list versions for"),
    ],
) -> list[dict[str, Any]]:
    """List all versions for a connector definition.

    Returns all published versions of a connector, ordered by last_published
    date descending. Useful for understanding version history and finding
    specific version IDs for pinning or rollout monitoring.

    Returns list of dicts with keys: version_id, docker_image_tag, docker_repository,
    release_stage, support_level, cdk_version, language, last_published, release_date
    """
    return query_connector_versions(connector_definition_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_new_connector_releases(
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
) -> list[dict[str, Any]]:
    """List recently published connector versions.

    Returns connector versions published within the specified number of days.
    Uses last_published timestamp which reflects when the version was actually
    deployed to the registry (not the changelog date).

    Returns list of dicts with keys: version_id, connector_definition_id, docker_repository,
    docker_image_tag, last_published, release_date, release_stage, support_level,
    cdk_version, language, created_at
    """
    return query_new_connector_releases(days=days, limit=limit)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_actors_by_connector_version(
    connector_version_id: Annotated[
        str,
        Field(description="Connector version UUID to find pinned instances for"),
    ],
) -> list[dict[str, Any]]:
    """List actors (sources/destinations) pinned to a specific connector version.

    Returns all actors that have been explicitly pinned to a specific
    connector version via scoped_configuration. Useful for monitoring
    rollouts and understanding which customers are affected by version pins.

    The actor_id field is the actor ID (superset of source_id/destination_id).

    Returns list of dicts with keys: actor_id, connector_definition_id, origin_type,
    origin, description, created_at, expires_at, actor_name, workspace_id,
    workspace_name, organization_id, dataplane_group_id, dataplane_name
    """
    return query_actors_pinned_to_version(connector_version_id)


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_connector_version_sync_results(
    connector_version_id: Annotated[
        str,
        Field(description="Connector version UUID to find sync results for"),
    ],
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
    successful_only: Annotated[
        bool,
        Field(
            description="If True, only return successful syncs (default: False)",
            default=False,
        ),
    ] = False,
) -> list[dict[str, Any]]:
    """List sync job results for actors pinned to a specific connector version.

    Returns sync job results for connections using actors that are pinned
    to the specified version. Useful for monitoring rollout health and
    identifying issues with specific connector versions.

    The actor_id field is the actor ID (superset of source_id/destination_id).

    Returns list of dicts with keys: job_id, connection_id, job_status, started_at,
    job_updated_at, connection_name, actor_id, actor_name, connector_definition_id,
    pin_origin_type, pin_origin, workspace_id, workspace_name, organization_id,
    dataplane_group_id, dataplane_name
    """
    return query_sync_results_for_version(
        connector_version_id,
        days=days,
        limit=limit,
        successful_only=successful_only,
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
)
def query_prod_failed_sync_attempts_for_version(
    connector_version_id: Annotated[
        str,
        Field(description="Connector version UUID to find failed sync attempts for"),
    ],
    days: Annotated[
        int,
        Field(description="Number of days to look back (default: 7)", default=7),
    ] = 7,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 100)", default=100),
    ] = 100,
) -> list[dict[str, Any]]:
    """List failed sync attempts with failure details for actors pinned to a connector version.

    Returns failed attempt records for connections using actors pinned to the specified
    version. Includes failure_summary from the attempts table for debugging.

    Key fields:
    - latest_job_attempt_status: Final job status after all retries ('succeeded' means
      the job eventually succeeded despite this failed attempt)
    - failed_attempt_number: Which attempt this was (0-indexed)
    - failure_summary: JSON containing failure details including failureType and messages

    Note: May return multiple rows per job (one per failed attempt). Results ordered by
    job_updated_at DESC, then failed_attempt_number DESC.

    Returns list of dicts with keys: job_id, connection_id, latest_job_attempt_status,
    job_started_at, job_updated_at, connection_name, actor_id, actor_name,
    actor_definition_id, pin_origin_type, pin_origin, workspace_id, workspace_name,
    organization_id, dataplane_group_id, dataplane_name, failed_attempt_id,
    failed_attempt_number, failed_attempt_status, failed_attempt_created_at,
    failed_attempt_ended_at, failure_summary, processing_task_queue
    """
    return query_failed_sync_attempts_for_version(
        connector_version_id,
        days=days,
        limit=limit,
    )


@mcp_tool(
    read_only=True,
    idempotent=True,
    open_world=True,
)
def query_prod_connections_by_connector(
    source_definition_id: Annotated[
        str | None,
        Field(
            description=(
                "Source connector definition ID (UUID) to search for. "
                "Exactly one of this or source_canonical_name is required. "
                "Example: 'afa734e4-3571-11ec-991a-1e0031268139' for YouTube Analytics."
            ),
            default=None,
        ),
    ] = None,
    source_canonical_name: Annotated[
        str | None,
        Field(
            description=(
                "Canonical source connector name to search for. "
                "Exactly one of this or source_definition_id is required. "
                "Examples: 'source-youtube-analytics', 'YouTube Analytics'."
            ),
            default=None,
        ),
    ] = None,
    organization_id: Annotated[
        str | None,
        Field(
            description=(
                "Optional organization ID (UUID) to filter results. "
                "If provided, only connections in this organization will be returned."
            ),
            default=None,
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Maximum number of results (default: 1000)", default=1000),
    ] = 1000,
) -> list[dict[str, Any]]:
    """Search for all connections using a specific source connector type.

    This tool queries the Airbyte Cloud Prod DB Replica directly for fast results.
    It finds all connections where the source connector matches the specified type,
    regardless of how the source is named by users.

    Optionally filter by organization_id to limit results to a specific organization.

    Returns a list of connection dicts with workspace context and clickable Cloud UI URLs.
    Each dict contains: connection_id, connection_name, connection_url, source_id,
    source_name, source_definition_id, workspace_id, workspace_name, organization_id,
    dataplane_group_id, dataplane_name.
    """
    # Validate that exactly one of the two parameters is provided
    if (source_definition_id is None) == (source_canonical_name is None):
        raise PyAirbyteInputError(
            message=(
                "Exactly one of source_definition_id or source_canonical_name "
                "must be provided, but not both."
            ),
        )

    # Resolve canonical name to definition ID if needed
    resolved_definition_id: str
    if source_canonical_name:
        resolved_definition_id = _resolve_canonical_name_to_definition_id(
            canonical_name=source_canonical_name,
        )
    else:
        resolved_definition_id = source_definition_id  # type: ignore[assignment]

    # Query the database and transform rows to include connection URLs
    return [
        {
            "organization_id": str(row.get("organization_id", "")),
            "workspace_id": str(row["workspace_id"]),
            "workspace_name": row.get("workspace_name", ""),
            "connection_id": str(row["connection_id"]),
            "connection_name": row.get("connection_name", ""),
            "connection_url": (
                f"{CLOUD_UI_BASE_URL}/workspaces/{row['workspace_id']}"
                f"/connections/{row['connection_id']}/status"
            ),
            "source_id": str(row["source_id"]),
            "source_name": row.get("source_name", ""),
            "source_definition_id": str(row["source_definition_id"]),
            "dataplane_group_id": str(row.get("dataplane_group_id", "")),
            "dataplane_name": row.get("dataplane_name", ""),
        }
        for row in query_connections_by_connector(
            connector_definition_id=resolved_definition_id,
            organization_id=organization_id,
            limit=limit,
        )
    ]


def register_prod_db_query_tools(app: FastMCP) -> None:
    """Register prod DB query tools with the FastMCP app."""
    register_mcp_tools(app, domain=__name__)
