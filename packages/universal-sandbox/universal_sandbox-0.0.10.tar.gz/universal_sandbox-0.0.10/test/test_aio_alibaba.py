"""Tests for Alibaba All-in-One (AIO) sandbox."""

import pytest


def test_alibaba_aio_create(sandbox_client, cleanup_sandboxes):
    """Test creating Alibaba AIO sandbox."""
    # Create an AIO sandbox
    aio = sandbox_client.aio.create(provider="alibaba", region="cn-hangzhou", timeout=10)
    cleanup_sandboxes(aio.id)

    assert aio.id is not None
    assert aio.provider == "alibaba"
    assert aio.status is not None

    # Check URLs
    assert hasattr(aio, 'urls')
    assert hasattr(aio.urls, 'vnc_url')
    assert hasattr(aio.urls, 'mcp_url')
    assert hasattr(aio.urls, 'api_url')
    assert hasattr(aio.urls, 'wss_url')


def test_alibaba_aio_execute(sandbox_client, cleanup_sandboxes):
    """Test executing code in Alibaba AIO sandbox."""
    aio = sandbox_client.aio.create(provider="alibaba", region="cn-hangzhou", timeout=10)
    cleanup_sandboxes(aio.id)

    # Execute code
    result = sandbox_client.sandboxes.execute(aio.id, command="print('Hello from Alibaba Cloud AIO!')")
    assert "Hello from Alibaba Cloud AIO!" in result.stdout


def test_alibaba_aio_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting Alibaba AIO sandbox info."""
    aio = sandbox_client.aio.create(provider="alibaba", region="cn-hangzhou", timeout=10)
    cleanup_sandboxes(aio.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(aio.id)
    assert info.status is not None
    assert info.id == aio.id
