"""Tests for basic API functionality."""

import pytest


def test_check_health(sandbox_client):
    """Test API health check."""
    health = sandbox_client.check_health()
    assert health.status is not None


def test_list_regions(sandbox_client):
    """Test listing available regions."""
    regions = sandbox_client.list_regions()
    assert regions is not None


def test_get_limits(sandbox_client):
    """Test getting account limits."""
    limits = sandbox_client.get_limits()
    assert limits is not None


def test_list_sandboxes(sandbox_client):
    """Test listing all sandboxes."""
    sandbox_list = sandbox_client.sandboxes.list()
    assert sandbox_list.total >= 0
    assert hasattr(sandbox_list, 'sandboxes')
