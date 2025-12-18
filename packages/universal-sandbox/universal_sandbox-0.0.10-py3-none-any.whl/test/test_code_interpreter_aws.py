"""Tests for AWS Code Interpreter sandbox."""

import pytest


def test_aws_code_interpreter_create_and_execute(sandbox_client, cleanup_sandboxes):
    """Test creating and executing code in AWS sandbox."""
    # Create a code interpreter sandbox
    box = sandbox_client.code_interpreter.create(provider="aws")
    cleanup_sandboxes(box.id)

    assert box.id is not None
    assert box.provider == "aws"
    assert box.status is not None

    # Execute code
    result = sandbox_client.code_interpreter.execute(box.id, command="print('Hello from AWS!')")
    assert "Hello from AWS!" in result.stdout


def test_aws_sandbox_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting AWS sandbox info."""
    box = sandbox_client.code_interpreter.create(provider="aws")
    cleanup_sandboxes(box.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(box.id)
    assert info.status is not None
    assert info.id == box.id
