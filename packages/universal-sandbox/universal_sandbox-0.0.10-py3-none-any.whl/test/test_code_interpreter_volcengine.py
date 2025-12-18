"""Tests for Volcengine Code Interpreter sandbox."""

import pytest


def test_volcengine_code_interpreter_create_and_execute(sandbox_client, cleanup_sandboxes):
    """Test creating and executing code in Volcengine sandbox."""
    # Create a code interpreter sandbox
    box = sandbox_client.code_interpreter.create(provider="volcengine")
    cleanup_sandboxes(box.id)

    assert box.id is not None
    assert box.provider == "volcengine"

    # Execute code
    result = sandbox_client.sandboxes.execute(box.id, command="echo 'Hello from Volcengine!'")
    assert "Hello from Volcengine!" in result.stdout


def test_volcengine_sandbox_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting Volcengine sandbox info."""
    box = sandbox_client.code_interpreter.create(provider="volcengine")
    cleanup_sandboxes(box.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(box.id)
    assert info.status is not None
    assert info.id == box.id
