# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Constants for the Airbyte Admin MCP server."""

from __future__ import annotations

from enum import Enum

MCP_SERVER_NAME = "airbyte-internal-ops"
"""The name of the MCP server."""

# Environment variable names for internal admin authentication
ENV_AIRBYTE_INTERNAL_ADMIN_FLAG = "AIRBYTE_INTERNAL_ADMIN_FLAG"
ENV_AIRBYTE_INTERNAL_ADMIN_USER = "AIRBYTE_INTERNAL_ADMIN_USER"

# Environment variable for GCP credentials (JSON content, not file path)
ENV_GCP_PROD_DB_ACCESS_CREDENTIALS = "GCP_PROD_DB_ACCESS_CREDENTIALS"
"""Environment variable containing GCP service account JSON credentials for prod DB access."""

# Expected values for internal admin authentication
EXPECTED_ADMIN_FLAG_VALUE = "airbyte.io"
EXPECTED_ADMIN_EMAIL_DOMAIN = "@airbyte.io"

# =============================================================================
# GCP and Prod DB Constants (from connection-retriever)
# =============================================================================

GCP_PROJECT_NAME = "prod-ab-cloud-proj"
"""The GCP project name for Airbyte Cloud production."""

CLOUD_SQL_INSTANCE = "prod-ab-cloud-proj:us-west3:prod-pgsql-replica"
"""The Cloud SQL instance connection name for the Prod DB Replica."""

DEFAULT_CLOUD_SQL_PROXY_PORT = 15432
"""Default port for Cloud SQL Proxy connections."""

CLOUD_SQL_PROXY_PID_FILE = "/tmp/airbyte-cloud-sql-proxy.pid"
"""PID file for tracking the Cloud SQL Proxy process."""

CLOUD_REGISTRY_URL = (
    "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
)
"""URL for the Airbyte Cloud connector registry."""

CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID = (
    "projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS"
)
"""GCP Secret Manager ID for Prod DB connection details."""


class ConnectionObject(Enum):
    """Types of connection objects that can be retrieved."""

    CONNECTION = "connection"
    SOURCE_ID = "source-id"
    DESTINATION_ID = "destination-id"
    DESTINATION_CONFIG = "destination-config"
    SOURCE_CONFIG = "source-config"
    CATALOG = "catalog"
    CONFIGURED_CATALOG = "configured-catalog"
    STATE = "state"
    WORKSPACE_ID = "workspace-id"
    DESTINATION_DOCKER_IMAGE = "destination-docker-image"
    SOURCE_DOCKER_IMAGE = "source-docker-image"
