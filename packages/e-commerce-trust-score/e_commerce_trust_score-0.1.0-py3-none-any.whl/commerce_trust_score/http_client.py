"""HTTP client for accessing remote trust score API service."""

from typing import Optional
import httpx
from dotenv import load_dotenv

from .models import TrustRequest, TrustResponse


class TrustScoreAPIClient:
    """
    HTTP client for accessing a remote trust score API service.
    
    This client is used when you want to call a deployed trust score API server
    instead of running the analysis locally.
    
    Example usage:
        >>> from commerce_trust_score import TrustScoreAPIClient
        >>> 
        >>> # Initialize client with API endpoint and key
        >>> client = TrustScoreAPIClient(
        ...     api_url="https://your-api.com",
        ...     api_key="your-service-api-key"
        ... )
        >>> 
        >>> # Analyze a URL
        >>> result = await client.analyze_url("https://example.com")
        >>> print(f"Score: {result.score}, Label: {result.label}")
    """
    
    def __init__(
        self, 
        api_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the HTTP client for trust score API.
        
        Args:
            api_url: Base URL of the trust score API server
                    (e.g., "https://api.example.com" or "http://localhost:8000")
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        # Prepare headers
        self.headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            self.headers["X-API-Key"] = self.api_key
    
    async def analyze_url(self, url: str) -> TrustResponse:
        """
        Analyze a URL by calling the remote API service.
        
        Args:
            url: The URL to analyze
            
        Returns:
            TrustResponse: Analysis result with score, label, factors, and explanations
            
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the API returns invalid data
            
        Example:
            >>> client = TrustScoreAPIClient(api_url="https://api.example.com", api_key="key")
            >>> result = await client.analyze_url("https://nike.com")
            >>> print(f"Trust score: {result.score}")
            >>> print(f"Label: {result.label}")
        """
        request = TrustRequest(url=url)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/api/trust-score",
                json=request.dict(),
                headers=self.headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return TrustResponse(**data)
    
    async def analyze_urls(self, urls: list[str]) -> list[TrustResponse]:
        """
        Analyze multiple URLs by calling the remote API service.
        
        This method calls the batch endpoint if available, or falls back to
        individual requests.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            list[TrustResponse]: List of analysis results
            
        Example:
            >>> client = TrustScoreAPIClient(api_url="https://api.example.com", api_key="key")
            >>> urls = ["https://nike.com", "https://suspicious-site.com"]
            >>> results = await client.analyze_urls(urls)
            >>> for url, result in zip(urls, results):
            ...     print(f"{url}: {result.label}")
        """
        # Try batch endpoint first
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/trust-score/batch",
                    json=urls,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    batch_data = response.json()
                    return [
                        TrustResponse(
                            score=item["score"],
                            label=item["label"],
                            factors=item["factors"],
                            explanations=item["explanations"]
                        )
                        for item in batch_data
                    ]
        except (httpx.HTTPError, KeyError):
            # Batch endpoint not available or failed, fall back to individual requests
            pass
        
        # Fall back to individual requests
        results = []
        for url in urls:
            result = await self.analyze_url(url)
            results.append(result)
        return results
    
    async def health_check(self) -> dict:
        """
        Check if the API service is healthy.
        
        Returns:
            dict: Health check response
            
        Example:
            >>> client = TrustScoreAPIClient(api_url="https://api.example.com")
            >>> health = await client.health_check()
            >>> print(health["status"])
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.api_url}/health",
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()

