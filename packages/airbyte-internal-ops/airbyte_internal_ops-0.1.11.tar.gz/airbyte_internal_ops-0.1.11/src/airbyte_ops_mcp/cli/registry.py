# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for connector registry operations.

This module provides CLI wrappers for registry operations. The core logic
lives in the `airbyte_ops_mcp.registry` capability module.

Commands:
    airbyte-ops registry connector publish-prerelease - Publish connector prerelease
    airbyte-ops registry connector publish - Publish connector (apply/rollback version override)
    airbyte-ops registry image inspect - Inspect Docker image on DockerHub
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import (
    exit_with_error,
    print_error,
    print_json,
    print_success,
)
from airbyte_ops_mcp.mcp.github import get_docker_image_info
from airbyte_ops_mcp.mcp.prerelease import publish_connector_to_airbyte_registry
from airbyte_ops_mcp.registry import (
    ConnectorPublishResult,
    PublishAction,
    publish_connector,
)

# Create the registry sub-app
registry_app = App(
    name="registry", help="Connector registry and Docker image operations."
)
app.command(registry_app)

# Create the connector sub-app under registry
connector_app = App(name="connector", help="Registry-facing connector operations.")
registry_app.command(connector_app)

# Create the image sub-app under registry
image_app = App(name="image", help="Docker image operations.")
registry_app.command(image_app)


@connector_app.command(name="publish-prerelease")
def publish_prerelease(
    connector_name: Annotated[
        str,
        Parameter(
            help="The connector name to publish (e.g., 'source-github', 'destination-postgres')."
        ),
    ],
    pr: Annotated[
        int,
        Parameter(help="The pull request number containing the connector changes."),
    ],
) -> None:
    """Publish a connector prerelease to the Airbyte registry.

    Triggers the publish-connectors-prerelease workflow in the airbytehq/airbyte
    repository. Pre-release versions are tagged with format: {version}-preview.{git-sha}

    Requires GITHUB_CONNECTOR_PUBLISHING_PAT or GITHUB_TOKEN environment variable
    with 'actions:write' permission.
    """
    result = publish_connector_to_airbyte_registry(
        connector_name=connector_name,
        pr_number=pr,
        prerelease=True,
    )
    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
    print_json(result.model_dump())


@connector_app.command(name="publish")
def publish(
    name: Annotated[
        str,
        Parameter(help="Connector technical name (e.g., source-github)."),
    ],
    repo_path: Annotated[
        Path,
        Parameter(help="Path to the Airbyte monorepo. Defaults to current directory."),
    ] = Path.cwd(),
    apply_override: Annotated[
        bool,
        Parameter(
            help="Apply a version override (promote RC to stable).",
            negative="",  # Disable --no-apply-override
        ),
    ] = False,
    rollback_override: Annotated[
        bool,
        Parameter(
            help="Rollback a version override.",
            negative="",  # Disable --no-rollback-override
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        Parameter(help="Show what would be published without making changes."),
    ] = False,
    prod: Annotated[
        bool,
        Parameter(
            help="Target the production GCS bucket. Without this flag, operations target the dev bucket for safe testing.",
            negative="",  # Disable --no-prod
        ),
    ] = False,
) -> None:
    """Publish a connector to the Airbyte registry.

    This command handles connector publishing operations including applying
    version overrides (promoting RC to stable) or rolling back version overrides.

    By default, operations target the dev bucket (dev-airbyte-cloud-connector-metadata-service-2)
    for safe testing. Use --prod to target the production bucket.
    """
    if apply_override and rollback_override:
        exit_with_error("Cannot use both --apply-override and --rollback-override")

    if not apply_override and not rollback_override:
        exit_with_error("Must specify either --apply-override or --rollback-override")

    # Map CLI flags to PublishAction
    action: PublishAction = (
        "apply-version-override" if apply_override else "rollback-version-override"
    )

    # Delegate to the capability module
    if not repo_path.exists():
        exit_with_error(f"Repository path not found: {repo_path}")

    result: ConnectorPublishResult = publish_connector(
        repo_path=repo_path,
        connector_name=name,
        action=action,
        dry_run=dry_run,
        use_prod=prod,
    )

    # Output result as JSON
    print_json(result.model_dump())

    if result.status == "failure":
        exit_with_error(result.message or "Operation failed", code=1)


@image_app.command(name="inspect")
def inspect_image(
    image: Annotated[
        str,
        Parameter(help="Docker image name (e.g., 'airbyte/source-github')."),
    ],
    tag: Annotated[
        str,
        Parameter(help="Image tag (e.g., '2.1.5-preview.abc1234')."),
    ],
) -> None:
    """Check if a Docker image exists on DockerHub.

    Returns information about the image if it exists, or indicates if it doesn't exist.
    Useful for confirming that a pre-release connector was successfully published.
    """
    result = get_docker_image_info(
        image=image,
        tag=tag,
    )
    if result.exists:
        print_success(f"Image {result.full_name} exists.")
    else:
        print_error(f"Image {result.full_name} not found.")
    print_json(result.model_dump())
