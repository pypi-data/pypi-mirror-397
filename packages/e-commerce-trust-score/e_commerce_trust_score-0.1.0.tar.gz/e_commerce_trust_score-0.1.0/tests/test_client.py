"""Tests for TrustScoreClient."""

import pytest
from unittest.mock import AsyncMock, patch
from commerce_trust_score import TrustScoreClient, TrustResponse


@pytest.fixture
def mock_api_key(monkeypatch):
    """Fixture to set a mock API key."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")


def test_client_initialization(mock_api_key):
    """Test client initializes correctly."""
    client = TrustScoreClient()
    assert client.config.anthropic_api_key == "test-key-12345"


def test_client_with_custom_key():
    """Test client with custom API key."""
    client = TrustScoreClient(anthropic_api_key="custom-key")
    assert client.config.anthropic_api_key == "custom-key"


@pytest.mark.asyncio
async def test_client_analyze_url(mock_api_key):
    """Test client analyze_url method."""
    # Mock the run_trust_agent function
    mock_result = {
        "score": 0.85,
        "label": "likely_safe",
        "factors": {
            "domain_age_days": 1000,
            "scam_reports": 0,
            "whois_risk": 0.2,
            "review_sentiment": 0.8,
            "social_reputation": 0.9,
            "price_outlier_score": 0.1,
            "payment_risk": 0.1,
            "image_reuse_score": 0.0,
            "brand_typosquatting_score": 0.0
        },
        "explanations": ["Test explanation"]
    }
    
    with patch('commerce_trust_score.client.run_trust_agent', new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_result
        
        client = TrustScoreClient()
        result = await client.analyze_url("https://example.com")
        
        assert isinstance(result, TrustResponse)
        assert result.score == 0.85
        assert result.label == "likely_safe"
        mock_agent.assert_called_once_with("https://example.com", max_turns=3)


@pytest.mark.asyncio
async def test_client_analyze_urls(mock_api_key):
    """Test client analyze_urls method."""
    mock_result = {
        "score": 0.85,
        "label": "likely_safe",
        "factors": {
            "domain_age_days": 1000,
            "scam_reports": 0,
            "whois_risk": 0.2,
            "review_sentiment": 0.8,
            "social_reputation": 0.9,
            "price_outlier_score": 0.1,
            "payment_risk": 0.1,
            "image_reuse_score": 0.0,
            "brand_typosquatting_score": 0.0
        },
        "explanations": ["Test explanation"]
    }
    
    with patch('commerce_trust_score.client.run_trust_agent', new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_result
        
        client = TrustScoreClient()
        urls = ["https://example1.com", "https://example2.com"]
        results = await client.analyze_urls(urls)
        
        assert len(results) == 2
        assert all(isinstance(r, TrustResponse) for r in results)
        assert mock_agent.call_count == 2

