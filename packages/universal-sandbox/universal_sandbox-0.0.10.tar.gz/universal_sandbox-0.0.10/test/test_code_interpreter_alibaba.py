"""Tests for Alibaba Code Interpreter sandbox."""

import pytest


def test_alibaba_code_interpreter_create_and_execute(sandbox_client, cleanup_sandboxes):
    """Test creating and executing code in Alibaba sandbox."""
    # Create a code interpreter sandbox
    box = sandbox_client.code_interpreter.create(provider="alibaba", region="cn-hangzhou")
    cleanup_sandboxes(box.id)

    assert box.id is not None
    assert box.provider == "alibaba"

    # Execute code
    result = sandbox_client.code_interpreter.execute(box.id, command="print('Hello from Alibaba Cloud!')")
    assert "Hello from Alibaba Cloud!" in result.stdout


def test_alibaba_sandbox_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting Alibaba sandbox info."""
    box = sandbox_client.code_interpreter.create(provider="alibaba", region="cn-hangzhou")
    cleanup_sandboxes(box.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(box.id)
    assert info.status is not None
    assert info.id == box.id


def test_alibaba_sandbox_list(sandbox_client):
    """Test listing sandboxes."""
    sandbox_list = sandbox_client.sandboxes.list()
    assert sandbox_list.total >= 0
    assert hasattr(sandbox_list, 'sandboxes')
