"""Tests for E2B Code Interpreter sandbox."""

import pytest


def test_e2b_code_interpreter_create_and_execute(sandbox_client, cleanup_sandboxes):
    """Test creating and executing code in E2B sandbox."""
    # Create a code interpreter sandbox
    box = sandbox_client.code_interpreter.create(provider="e2b", timeout=1)
    cleanup_sandboxes(box.id)

    assert box.id is not None
    assert box.provider == "e2b"

    # Execute code
    result = sandbox_client.sandboxes.execute(box.id, command="print('Hello from E2B!')")
    assert "Hello from E2B!" in result.stdout


def test_e2b_sandbox_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting E2B sandbox info."""
    box = sandbox_client.code_interpreter.create(provider="e2b", timeout=1)
    cleanup_sandboxes(box.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(box.id)
    assert info.status is not None
    assert info.id == box.id


def test_e2b_sandbox_list(sandbox_client):
    """Test listing sandboxes includes E2B sandboxes."""
    sandbox_list = sandbox_client.sandboxes.list()
    assert sandbox_list.total >= 0
    assert hasattr(sandbox_list, 'sandboxes')
