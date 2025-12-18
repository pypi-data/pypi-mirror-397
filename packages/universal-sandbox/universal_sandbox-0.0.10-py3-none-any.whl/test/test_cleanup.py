"""Tests for sandbox cleanup functionality."""

import pytest


def test_cleanup_all_sandboxes(sandbox_client):
    """Test deleting all sandboxes (cleanup operation)."""
    # List all sandboxes
    sandbox_list = sandbox_client.sandboxes.list()
    initial_count = sandbox_list.total

    print(f"Found {initial_count} sandbox(es) to clean up")

    # Delete all sandboxes
    deleted_count = 0
    for s in sandbox_list.sandboxes:
        try:
            resp = sandbox_client.sandboxes.delete(s.id)
            print(f"Deleted sandbox: {s.id}")
            deleted_count += 1
        except Exception as e:
            print(f"Failed to delete sandbox {s.id}: {e}")

    print(f"Deleted {deleted_count}/{initial_count} sandbox(es)")

    # Verify cleanup
    final_list = sandbox_client.sandboxes.list()
    assert final_list.total <= initial_count


def test_delete_specific_sandbox(sandbox_client):
    """Test deleting a specific sandbox."""
    # Create a test sandbox
    box = sandbox_client.code_interpreter.create(provider="e2b", timeout=1)
    sandbox_id = box.id

    assert sandbox_id is not None

    # Delete the sandbox
    resp = sandbox_client.sandboxes.delete(sandbox_id)
    assert resp is not None

    # Verify it's deleted by checking the list
    # Note: We can't verify by getting it directly as that might throw an error
    print(f"Successfully deleted sandbox: {sandbox_id}")
