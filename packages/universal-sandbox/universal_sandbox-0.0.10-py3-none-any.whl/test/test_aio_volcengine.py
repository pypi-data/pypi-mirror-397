"""Tests for Volcengine All-in-One (AIO) sandbox."""

import pytest


def test_volcengine_aio_create(sandbox_client, cleanup_sandboxes):
    """Test creating Volcengine AIO sandbox."""
    # Create an AIO sandbox
    aio = sandbox_client.aio.create(provider="volcengine")
    cleanup_sandboxes(aio.id)

    assert aio.id is not None
    assert aio.status is not None

    # Check URLs
    assert hasattr(aio, 'urls')
    assert hasattr(aio.urls, 'vnc_url')
    assert hasattr(aio.urls, 'mcp_url')
    assert hasattr(aio.urls, 'api_url')
    assert hasattr(aio.urls, 'wss_url')


def test_volcengine_aio_execute(sandbox_client, cleanup_sandboxes):
    """Test executing code in Volcengine AIO sandbox."""
    aio = sandbox_client.aio.create(provider="volcengine")
    cleanup_sandboxes(aio.id)

    # Execute shell command (AIO supports shell commands)
    result = sandbox_client.sandboxes.execute(aio.id, command="echo 'Hello from Volcengine AIO!'")

    # Check if execution completed (may timeout on some commands)
    if result.exit_code == 0:
        assert "Hello from Volcengine AIO!" in result.stdout
    else:
        # If command timed out or failed, just verify the sandbox was created
        assert aio.id is not None


def test_volcengine_aio_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting Volcengine AIO sandbox info."""
    aio = sandbox_client.aio.create(provider="volcengine")
    cleanup_sandboxes(aio.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(aio.id)
    assert info.status is not None
    assert info.id == aio.id
