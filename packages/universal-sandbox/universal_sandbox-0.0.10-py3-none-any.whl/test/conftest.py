"""Pytest configuration and fixtures for Universal Sandbox tests."""

import os
import pytest
from universal_sandbox import Sandbox


@pytest.fixture(scope="session")
def sandbox_client():
    """Create a Sandbox client for all tests."""
    token = os.getenv("SANDBOX_API_TOKEN")
    if not token:
        pytest.skip("SANDBOX_API_TOKEN environment variable not set")

    client = Sandbox(token=token)
    yield client


@pytest.fixture(scope="function")
def cleanup_sandboxes(sandbox_client):
    """Fixture to cleanup sandboxes after each test."""
    created_sandbox_ids = []

    def track_sandbox(sandbox_id):
        """Track a sandbox ID for cleanup."""
        created_sandbox_ids.append(sandbox_id)
        return sandbox_id

    yield track_sandbox

    # Cleanup after test
    for sandbox_id in created_sandbox_ids:
        try:
            sandbox_client.sandboxes.delete(sandbox_id)
        except Exception as e:
            print(f"Warning: Failed to cleanup sandbox {sandbox_id}: {e}")
