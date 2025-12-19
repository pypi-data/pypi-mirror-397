# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""GitHub Actions API utilities.

This module provides core utilities for interacting with GitHub Actions workflows,
including workflow dispatch, run discovery, and authentication. These utilities
are used by MCP tools but are not MCP-specific.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

GITHUB_API_BASE = "https://api.github.com"


def resolve_github_token(preferred_env_vars: list[str] | None = None) -> str:
    """Resolve GitHub token from environment variables.

    Checks environment variables in order of preference, returning the first
    non-empty value found.

    Args:
        preferred_env_vars: List of environment variable names to check in order.
            Defaults to ["GITHUB_CI_WORKFLOW_TRIGGER_PAT", "GITHUB_TOKEN"].

    Returns:
        GitHub token string.

    Raises:
        ValueError: If no GitHub token is found in any of the specified env vars.
    """
    if preferred_env_vars is None:
        preferred_env_vars = ["GITHUB_CI_WORKFLOW_TRIGGER_PAT", "GITHUB_TOKEN"]

    for env_var in preferred_env_vars:
        token = os.getenv(env_var)
        if token:
            return token

    env_var_list = ", ".join(preferred_env_vars)
    raise ValueError(
        f"No GitHub token found. Set one of: {env_var_list} environment variable."
    )


@dataclass
class WorkflowDispatchResult:
    """Result of triggering a workflow dispatch."""

    workflow_url: str
    """URL to the workflow file (e.g., .../actions/workflows/my-workflow.yml)"""

    run_id: int | None = None
    """GitHub Actions run ID, if discovered"""

    run_url: str | None = None
    """Direct URL to the workflow run, if discovered"""


def find_workflow_run(
    owner: str,
    repo: str,
    workflow_file: str,
    ref: str,
    token: str,
    created_after: datetime,
    max_wait_seconds: float = 5.0,
) -> tuple[int, str] | None:
    """Find a workflow run that was created after a given time.

    This is used to find the run that was just triggered via workflow_dispatch.
    Polls for up to max_wait_seconds to handle GitHub API eventual consistency.

    Args:
        owner: Repository owner
        repo: Repository name
        workflow_file: Workflow file name
        ref: Git ref the workflow was triggered on
        token: GitHub API token
        created_after: Only consider runs created after this time
        max_wait_seconds: Maximum time to wait for run to appear (default 5 seconds)

    Returns:
        Tuple of (run_id, run_url) if found, None otherwise.
    """
    url = (
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/runs"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    params = {
        "branch": ref,
        "event": "workflow_dispatch",
        "per_page": 5,
    }

    # Add a small buffer to handle timestamp precision differences between
    # local time and GitHub's created_at (which has second resolution)
    search_after = created_after - timedelta(seconds=2)

    deadline = time.monotonic() + max_wait_seconds
    attempt = 0

    while time.monotonic() < deadline:
        if attempt > 0:
            time.sleep(1.0)
        attempt += 1

        response = requests.get(url, headers=headers, params=params, timeout=30)
        if not response.ok:
            continue

        data = response.json()
        runs = data.get("workflow_runs", [])

        for run in runs:
            run_created_at = datetime.fromisoformat(
                run["created_at"].replace("Z", "+00:00")
            )
            if run_created_at >= search_after:
                return run["id"], run["html_url"]

    return None


def trigger_workflow_dispatch(
    owner: str,
    repo: str,
    workflow_file: str,
    ref: str,
    inputs: dict,
    token: str,
    find_run: bool = True,
    max_wait_seconds: float = 5.0,
) -> WorkflowDispatchResult:
    """Trigger a GitHub Actions workflow via workflow_dispatch.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte-ops-mcp")
        workflow_file: Workflow file name (e.g., "connector-live-test.yml")
        ref: Git ref to run the workflow on (branch name)
        inputs: Workflow inputs dictionary
        token: GitHub API token
        find_run: Whether to attempt to find the run after dispatch (default True)
        max_wait_seconds: Maximum time to wait for run discovery (default 5 seconds)

    Returns:
        WorkflowDispatchResult with workflow URL and optionally run ID/URL.

    Raises:
        requests.HTTPError: If API request fails.
    """
    dispatch_time = datetime.now(tz=datetime.now().astimezone().tzinfo)

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "ref": ref,
        "inputs": inputs,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    workflow_url = (
        f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_file}"
    )

    if not find_run:
        return WorkflowDispatchResult(workflow_url=workflow_url)

    # Best-effort lookup of the run that was just triggered
    run_info = find_workflow_run(
        owner, repo, workflow_file, ref, token, dispatch_time, max_wait_seconds
    )
    if run_info:
        run_id, run_url = run_info
        return WorkflowDispatchResult(
            workflow_url=workflow_url,
            run_id=run_id,
            run_url=run_url,
        )

    return WorkflowDispatchResult(workflow_url=workflow_url)
