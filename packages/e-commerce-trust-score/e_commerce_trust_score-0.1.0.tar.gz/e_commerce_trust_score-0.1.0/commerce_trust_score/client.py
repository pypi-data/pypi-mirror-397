"""High-level client interface for trust score analysis."""

from typing import Optional
from dotenv import load_dotenv

from .agent import run_trust_agent
from .models import TrustResponse
from .config import Config


class TrustScoreClient:
    """
    High-level client for analyzing URL trust scores.
    
    Example usage:
        >>> from trust_score_agent import TrustScoreClient
        >>> 
        >>> # Initialize client (will use ANTHROPIC_API_KEY from environment)
        >>> client = TrustScoreClient()
        >>> 
        >>> # Analyze a URL
        >>> result = await client.analyze_url("https://example.com")
        >>> print(f"Score: {result.score}, Label: {result.label}")
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the trust score client.
        
        Args:
            anthropic_api_key: Optional Anthropic API key. If not provided,
                              will look for ANTHROPIC_API_KEY environment variable.
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Validate configuration
        self.config = Config(anthropic_api_key=anthropic_api_key)
    
    async def analyze_url(
        self, 
        url: str, 
        max_turns: int = 3
    ) -> TrustResponse:
        """
        Analyze a URL and return trust score information.
        
        Args:
            url: The URL to analyze
            max_turns: Maximum number of agent conversation turns (default: 3)
            
        Returns:
            TrustResponse: Analysis result with score, label, factors, and explanations
            
        Example:
            >>> client = TrustScoreClient()
            >>> result = await client.analyze_url("https://nike.com")
            >>> print(f"Trust score: {result.score}")
            >>> print(f"Label: {result.label}")
            >>> for explanation in result.explanations:
            ...     print(f"- {explanation}")
        """
        result_dict = await run_trust_agent(url, max_turns=max_turns)
        return TrustResponse(**result_dict)
    
    async def analyze_urls(self, urls: list[str], max_turns: int = 3) -> list[TrustResponse]:
        """
        Analyze multiple URLs sequentially.
        
        Args:
            urls: List of URLs to analyze
            max_turns: Maximum number of agent conversation turns per URL
            
        Returns:
            list[TrustResponse]: List of analysis results
            
        Example:
            >>> client = TrustScoreClient()
            >>> urls = ["https://nike.com", "https://suspicious-site.com"]
            >>> results = await client.analyze_urls(urls)
            >>> for url, result in zip(urls, results):
            ...     print(f"{url}: {result.label}")
        """
        results = []
        for url in urls:
            result = await self.analyze_url(url, max_turns=max_turns)
            results.append(result)
        return results

