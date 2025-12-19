"""Tests for data models."""

import pytest
from commerce_trust_score.models import TrustRequest, TrustResponse, TrustFactors


def test_trust_request():
    """Test TrustRequest model."""
    req = TrustRequest(url="https://example.com")
    assert req.url == "https://example.com"


def test_trust_factors():
    """Test TrustFactors model."""
    factors = TrustFactors(
        domain_age_days=1000,
        scam_reports=0,
        whois_risk=0.2,
        review_sentiment=0.8,
        social_reputation=0.9,
        price_outlier_score=0.1,
        payment_risk=0.1,
        image_reuse_score=0.0,
        brand_typosquatting_score=0.0
    )
    assert factors.domain_age_days == 1000
    assert factors.scam_reports == 0
    assert factors.whois_risk == 0.2


def test_trust_response():
    """Test TrustResponse model."""
    factors = TrustFactors(
        domain_age_days=1000,
        scam_reports=0,
        whois_risk=0.2,
        review_sentiment=0.8,
        social_reputation=0.9,
        price_outlier_score=0.1,
        payment_risk=0.1,
        image_reuse_score=0.0,
        brand_typosquatting_score=0.0
    )
    
    response = TrustResponse(
        score=0.85,
        label="likely_safe",
        factors=factors,
        explanations=["Test explanation"]
    )
    
    assert response.score == 0.85
    assert response.label == "likely_safe"
    assert len(response.explanations) == 1
    assert response.explanations[0] == "Test explanation"


def test_trust_response_validation():
    """Test TrustResponse validates correctly."""
    factors = TrustFactors(
        domain_age_days=1000,
        scam_reports=0,
        whois_risk=0.2,
        review_sentiment=0.8,
        social_reputation=0.9,
        price_outlier_score=0.1,
        payment_risk=0.1,
        image_reuse_score=0.0,
        brand_typosquatting_score=0.0
    )
    
    # This should not raise an error
    response = TrustResponse(
        score=0.85,
        label="likely_safe",
        factors=factors,
        explanations=["Safe", "Trusted"]
    )
    
    assert isinstance(response.explanations, list)
    assert len(response.explanations) == 2

