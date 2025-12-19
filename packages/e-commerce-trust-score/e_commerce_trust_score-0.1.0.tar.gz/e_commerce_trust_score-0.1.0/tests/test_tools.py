"""Tests for MCP tools."""

import pytest
from commerce_trust_score.tools import inspect_url, create_url_tools_server


@pytest.mark.asyncio
async def test_inspect_url_https():
    """Test inspect_url with HTTPS URL."""
    result = await inspect_url({"url": "https://example.com"})
    
    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"
    
    import json
    data = json.loads(result["content"][0]["text"])
    
    assert data["url"] == "https://example.com"
    assert data["is_https"] is True
    assert data["hostname"] == "example.com"
    assert "tool_score" in data
    assert 0 <= data["tool_score"] <= 1


@pytest.mark.asyncio
async def test_inspect_url_http():
    """Test inspect_url with HTTP URL."""
    result = await inspect_url({"url": "http://example.com"})
    
    import json
    data = json.loads(result["content"][0]["text"])
    
    assert data["is_https"] is False
    # HTTP should have lower score than HTTPS
    assert data["tool_score"] < 0.7


@pytest.mark.asyncio
async def test_inspect_url_suspicious_keywords():
    """Test inspect_url detects suspicious keywords."""
    result = await inspect_url({"url": "https://nike-clearance90off.shop"})
    
    import json
    data = json.loads(result["content"][0]["text"])
    
    assert len(data["suspicious_keywords"]) > 0
    assert "clearance" in data["suspicious_keywords"] or "90off" in data["suspicious_keywords"]
    # Suspicious keywords should lower the score
    assert data["tool_score"] < 0.6


@pytest.mark.asyncio
async def test_inspect_url_long_hostname():
    """Test inspect_url penalizes very long hostnames."""
    long_url = "https://this-is-a-very-long-suspicious-hostname-that-might-be-a-scam.com"
    result = await inspect_url({"url": long_url})
    
    import json
    data = json.loads(result["content"][0]["text"])
    
    # Long hostname should be penalized
    assert len(data["hostname"]) > 30
    assert data["tool_score"] < 0.7


def test_create_url_tools_server():
    """Test creating the MCP server."""
    server = create_url_tools_server()
    
    assert server is not None
    # The server should have our tool registered
    assert hasattr(server, "name") or hasattr(server, "tools")

