"""Data models for trust score analysis."""

from typing import List
from pydantic import BaseModel


class TrustRequest(BaseModel):
    """Request model for trust score analysis."""
    url: str


class TrustFactors(BaseModel):
    """Detailed factors contributing to the trust score."""
    domain_age_days: int
    scam_reports: int
    whois_risk: float
    review_sentiment: float
    social_reputation: float
    price_outlier_score: float
    payment_risk: float
    image_reuse_score: float
    brand_typosquatting_score: float


class TrustResponse(BaseModel):
    """Response model containing trust score and analysis."""
    score: float
    label: str
    factors: TrustFactors
    explanations: List[str]

