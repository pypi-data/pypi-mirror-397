# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Query execution functions for Airbyte Cloud Prod DB Replica.

This module provides functions that execute SQL queries against the Prod DB Replica
and return structured results. Each function wraps a SQL template from sql.py.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any

import sqlalchemy
from google.cloud import secretmanager

from airbyte_ops_mcp.gcp_auth import get_secret_manager_client
from airbyte_ops_mcp.prod_db_access.db_engine import get_pool
from airbyte_ops_mcp.prod_db_access.sql import (
    SELECT_ACTORS_PINNED_TO_VERSION,
    SELECT_CONNECTIONS_BY_CONNECTOR,
    SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG,
    SELECT_CONNECTOR_VERSIONS,
    SELECT_DATAPLANES_LIST,
    SELECT_FAILED_SYNC_ATTEMPTS_FOR_VERSION,
    SELECT_NEW_CONNECTOR_RELEASES,
    SELECT_ORG_WORKSPACES,
    SELECT_SUCCESSFUL_SYNCS_FOR_VERSION,
    SELECT_SYNC_RESULTS_FOR_VERSION,
    SELECT_WORKSPACE_INFO,
)

logger = logging.getLogger(__name__)


def _run_sql_query(
    statement: sqlalchemy.sql.elements.TextClause,
    parameters: Mapping[str, Any] | None = None,
    *,
    query_name: str | None = None,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Execute a SQL text statement and return rows as list[dict], logging elapsed time.

    Args:
        statement: SQLAlchemy text clause to execute
        parameters: Query parameters to bind
        query_name: Optional name for logging (defaults to first line of SQL)
        gsm_client: GCP Secret Manager client for retrieving credentials.
            If None, a new client will be instantiated.

    Returns:
        List of row dicts from the query result
    """
    if gsm_client is None:
        gsm_client = get_secret_manager_client()
    pool = get_pool(gsm_client)
    start = perf_counter()
    with pool.connect() as conn:
        result = conn.execute(statement, parameters or {})
        rows = [dict(row._mapping) for row in result]
    elapsed = perf_counter() - start

    name = query_name or "SQL query"
    logger.info("Prod DB query %s returned %d rows in %.3f s", name, len(rows), elapsed)

    return rows


def query_connections_by_connector(
    connector_definition_id: str,
    organization_id: str | None = None,
    limit: int = 1000,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query connections by source connector type, optionally filtered by organization.

    Args:
        connector_definition_id: Connector definition UUID to filter by
        organization_id: Optional organization UUID to search within
        limit: Maximum number of results (default: 1000)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of connection records with workspace and dataplane info
    """
    # Use separate queries to avoid pg8000 NULL parameter type issues
    # pg8000 cannot determine the type of NULL parameters in patterns like
    # "(:param IS NULL OR column = :param)"
    if organization_id is None:
        return _run_sql_query(
            SELECT_CONNECTIONS_BY_CONNECTOR,
            parameters={
                "connector_definition_id": connector_definition_id,
                "limit": limit,
            },
            query_name="SELECT_CONNECTIONS_BY_CONNECTOR",
            gsm_client=gsm_client,
        )

    return _run_sql_query(
        SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG,
        parameters={
            "connector_definition_id": connector_definition_id,
            "organization_id": organization_id,
            "limit": limit,
        },
        query_name="SELECT_CONNECTIONS_BY_CONNECTOR_AND_ORG",
        gsm_client=gsm_client,
    )


def query_connector_versions(
    connector_definition_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all versions for a connector definition.

    Args:
        connector_definition_id: Connector definition UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of version records ordered by last_published DESC
    """
    return _run_sql_query(
        SELECT_CONNECTOR_VERSIONS,
        parameters={"actor_definition_id": connector_definition_id},
        query_name="SELECT_CONNECTOR_VERSIONS",
        gsm_client=gsm_client,
    )


def query_new_connector_releases(
    days: int = 7,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query recently published connector versions.

    Args:
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of recently published connector versions
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    return _run_sql_query(
        SELECT_NEW_CONNECTOR_RELEASES,
        parameters={"cutoff_date": cutoff_date, "limit": limit},
        query_name="SELECT_NEW_CONNECTOR_RELEASES",
        gsm_client=gsm_client,
    )


def query_actors_pinned_to_version(
    connector_version_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query actors (sources/destinations) pinned to a specific connector version.

    Args:
        connector_version_id: Connector version UUID to search for
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of actors pinned to the specified version
    """
    return _run_sql_query(
        SELECT_ACTORS_PINNED_TO_VERSION,
        parameters={"actor_definition_version_id": connector_version_id},
        query_name="SELECT_ACTORS_PINNED_TO_VERSION",
        gsm_client=gsm_client,
    )


def query_sync_results_for_version(
    connector_version_id: str,
    days: int = 7,
    limit: int = 100,
    successful_only: bool = False,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query sync job results for actors pinned to a specific connector version.

    Args:
        connector_version_id: Connector version UUID to filter by
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        successful_only: If True, only return successful syncs (default: False)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of sync job results
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    query = (
        SELECT_SUCCESSFUL_SYNCS_FOR_VERSION
        if successful_only
        else SELECT_SYNC_RESULTS_FOR_VERSION
    )
    query_name = (
        "SELECT_SUCCESSFUL_SYNCS_FOR_VERSION"
        if successful_only
        else "SELECT_SYNC_RESULTS_FOR_VERSION"
    )
    return _run_sql_query(
        query,
        parameters={
            "actor_definition_version_id": connector_version_id,
            "cutoff_date": cutoff_date,
            "limit": limit,
        },
        query_name=query_name,
        gsm_client=gsm_client,
    )


def query_failed_sync_attempts_for_version(
    connector_version_id: str,
    days: int = 7,
    limit: int = 100,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query failed sync job results with attempt details for actors pinned to a version.

    This query joins to the attempts table to include failure_summary and other
    attempt-level details useful for debugging. Date filters are applied to both
    jobs and attempts tables to optimize join performance.

    Note: This may return multiple rows per job (one per attempt). Results are
    ordered by job_updated_at DESC, then attempt_number DESC.

    Args:
        connector_version_id: Connector version UUID to filter by
        days: Number of days to look back (default: 7)
        limit: Maximum number of results (default: 100)
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of failed sync job results with attempt details including failure_summary
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    return _run_sql_query(
        SELECT_FAILED_SYNC_ATTEMPTS_FOR_VERSION,
        parameters={
            "actor_definition_version_id": connector_version_id,
            "cutoff_date": cutoff_date,
            "limit": limit,
        },
        query_name="SELECT_FAILED_SYNC_ATTEMPTS_FOR_VERSION",
        gsm_client=gsm_client,
    )


def query_dataplanes_list(
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all dataplane groups with workspace counts.

    Args:
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of dataplane groups ordered by workspace count DESC
    """
    return _run_sql_query(
        SELECT_DATAPLANES_LIST,
        query_name="SELECT_DATAPLANES_LIST",
        gsm_client=gsm_client,
    )


def query_workspace_info(
    workspace_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> dict[str, Any] | None:
    """Query workspace info including dataplane group.

    Args:
        workspace_id: Workspace UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        Workspace info dict, or None if not found
    """
    rows = _run_sql_query(
        SELECT_WORKSPACE_INFO,
        parameters={"workspace_id": workspace_id},
        query_name="SELECT_WORKSPACE_INFO",
        gsm_client=gsm_client,
    )
    return rows[0] if rows else None


def query_org_workspaces(
    organization_id: str,
    *,
    gsm_client: secretmanager.SecretManagerServiceClient | None = None,
) -> list[dict[str, Any]]:
    """Query all workspaces in an organization with dataplane info.

    Args:
        organization_id: Organization UUID
        gsm_client: GCP Secret Manager client. If None, a new client will be instantiated.

    Returns:
        List of workspaces in the organization
    """
    return _run_sql_query(
        SELECT_ORG_WORKSPACES,
        parameters={"organization_id": organization_id},
        query_name="SELECT_ORG_WORKSPACES",
        gsm_client=gsm_client,
    )
