# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Database engine and connection management for Airbyte Cloud Prod DB Replica.

This module provides connection pooling and engine management for querying
the Airbyte Cloud production database replica.

For SQL query templates and schema documentation, see sql.py.
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any, Callable

import sqlalchemy
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
from google.cloud.sql.connector.enums import IPTypes

from airbyte_ops_mcp.constants import (
    CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID,
)

PG_DRIVER = "pg8000"

# Lazy-initialized to avoid import-time GCP auth
_connector: Connector | None = None


def _get_connector() -> Connector:
    """Get the Cloud SQL connector, initializing lazily on first use."""
    global _connector
    if _connector is None:
        _connector = Connector()
    return _connector


def _get_secret_value(
    gsm_client: secretmanager.SecretManagerServiceClient, secret_id: str
) -> str:
    """Get the value of the enabled version of a secret.

    Args:
        gsm_client: GCP Secret Manager client
        secret_id: The id of the secret

    Returns:
        The value of the enabled version of the secret
    """
    response = gsm_client.list_secret_versions(
        request={"parent": secret_id, "filter": "state:ENABLED"}
    )
    if len(response.versions) == 0:
        raise ValueError(f"No enabled version of secret {secret_id} found")
    enabled_version = response.versions[0]
    response = gsm_client.access_secret_version(name=enabled_version.name)
    return response.payload.data.decode("UTF-8")


def get_database_creator(pg_connection_details: dict) -> Callable:
    """Create a database connection creator function."""

    def creator() -> Any:
        return _get_connector().connect(
            pg_connection_details["database_address"],
            PG_DRIVER,
            user=pg_connection_details["pg_user"],
            password=pg_connection_details["pg_password"],
            db=pg_connection_details["database_name"],
            ip_type=IPTypes.PRIVATE,
        )

    return creator


def get_pool(
    gsm_client: secretmanager.SecretManagerServiceClient,
) -> sqlalchemy.Engine:
    """Get a SQLAlchemy connection pool for the Airbyte Cloud database.

    This function supports two connection modes:
    1. Direct connection via Cloud SQL Python Connector (default, requires VPC access)
    2. Connection via Cloud SQL Auth Proxy (when CI or USE_CLOUD_SQL_PROXY env var is set)

    For proxy mode, start the proxy with:
        cloud-sql-proxy prod-ab-cloud-proj:us-west3:prod-pgsql-replica --port=<port>

    Environment variables:
        CI: If set, uses proxy connection mode
        USE_CLOUD_SQL_PROXY: If set, uses proxy connection mode
        DB_PORT: Port for proxy connection (default: 5432)

    Args:
        gsm_client: GCP Secret Manager client for retrieving credentials

    Returns:
        SQLAlchemy Engine connected to the Prod DB Replica
    """
    pg_connection_details = json.loads(
        _get_secret_value(
            gsm_client, CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID
        )
    )

    if os.getenv("CI") or os.getenv("USE_CLOUD_SQL_PROXY"):
        # Connect via Cloud SQL Auth Proxy, running on localhost
        # Port can be configured via DB_PORT env var (default: 5432)
        host = "127.0.0.1"
        port = os.getenv("DB_PORT", "5432")
        try:
            return sqlalchemy.create_engine(
                f"postgresql+{PG_DRIVER}://{pg_connection_details['pg_user']}:{pg_connection_details['pg_password']}@{host}:{port}/{pg_connection_details['database_name']}",
            )
        except Exception as e:
            raise AssertionError(
                f"sqlalchemy.create_engine exception; could not connect to the proxy at {host}:{port}. "
                f"Error: {traceback.format_exception(e)}"
            ) from e

    # Default: Connect via Cloud SQL Python Connector (requires VPC access)
    return sqlalchemy.create_engine(
        f"postgresql+{PG_DRIVER}://",
        creator=get_database_creator(pg_connection_details),
    )
