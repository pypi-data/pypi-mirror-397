"""
Commerce Trust Score - A Python library for analyzing URL trust scores using Claude AI.

This library provides a client interface to analyze URLs and determine their 
trustworthiness based on various factors like domain characteristics, suspicious 
patterns, and more.

Basic usage (local analysis):
    >>> from commerce_trust_score import TrustScoreClient
    >>> import asyncio
    >>> 
    >>> async def main():
    ...     client = TrustScoreClient()
    ...     result = await client.analyze_url("https://example.com")
    ...     print(f"Score: {result.score}, Label: {result.label}")
    >>> 
    >>> asyncio.run(main())

Using remote API (with API key):
    >>> from commerce_trust_score import TrustScoreAPIClient
    >>> 
    >>> async def main():
    ...     client = TrustScoreAPIClient(
    ...         api_url="https://your-api.com",
    ...         api_key="your-service-api-key"
    ...     )
    ...     result = await client.analyze_url("https://example.com")
    ...     print(f"Score: {result.score}")
    >>> 
    >>> asyncio.run(main())

For server deployment, see server_example.py in the repository.
"""

from .__version__ import __version__
from .client import TrustScoreClient
from .http_client import TrustScoreAPIClient
from .models import TrustRequest, TrustResponse, TrustFactors
from .agent import run_trust_agent
from .config import Config

__all__ = [
    "__version__",
    "TrustScoreClient",
    "TrustScoreAPIClient",
    "TrustRequest",
    "TrustResponse",
    "TrustFactors",
    "run_trust_agent",
    "Config",
]

