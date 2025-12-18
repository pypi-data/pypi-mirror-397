"""Tests for Alibaba Browser sandbox."""

import pytest


def test_alibaba_browser_create(sandbox_client, cleanup_sandboxes):
    """Test creating Alibaba browser sandbox."""
    # Create a browser sandbox
    browser = sandbox_client.browser.create(provider="alibaba", region="cn-hangzhou")
    cleanup_sandboxes(browser.id)

    assert browser.id is not None
    assert browser.status is not None


def test_alibaba_browser_get_info(sandbox_client, cleanup_sandboxes):
    """Test getting Alibaba browser sandbox info."""
    browser = sandbox_client.browser.create(provider="alibaba", region="cn-hangzhou")
    cleanup_sandboxes(browser.id)

    # Get sandbox info
    info = sandbox_client.sandboxes.get(browser.id)
    assert info.status is not None
    assert info.id == browser.id
