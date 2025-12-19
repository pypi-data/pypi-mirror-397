"""
Main client for the Discourses API.

This module provides the Discourses class, which is the primary interface
for interacting with the Discourses sentiment analysis API.
"""

from typing import List, Optional, Union, Dict, Any

import requests

from discourses.constants import BASE_URL, DEFAULT_TIMEOUT, ENDPOINTS, Era
from discourses.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)
from discourses.models import AnalysisResult, CompareResult, BatchResult


class Discourses:
    """
    Client for the Discourses financial sentiment analysis API.
    
    The Discourses API provides institutional-grade sentiment analysis using
    era-calibrated lexicons, powered by academic methodology from Paolucci et al. 2024.
    
    Args:
        api_key: Your Discourses API key. Get one at https://discourses.io/dashboard
        base_url: API base URL (default: https://discourses.io/api/v1)
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> from discourses import Discourses
        >>> client = Discourses(api_key="your-api-key")
        >>> 
        >>> # Single text analysis
        >>> result = client.analyze("Apple reported record earnings")
        >>> print(f"Score: {result.score:.2f}, Sentiment: {result.sentiment}")
        >>>
        >>> # Compare across eras
        >>> comparison = client.compare("Market disruption ahead")
        >>> for era in comparison.results:
        ...     print(f"{era.era}: {era.score:.2f}")
        >>>
        >>> # Batch analysis
        >>> texts = ["Great quarter", "Missed expectations", "Steady growth"]
        >>> batch = client.batch(texts)
        >>> for item in batch:
        ...     print(f"{item.result.sentiment}")
    
    Attributes:
        api_key: The API key used for authentication.
        base_url: The base URL for API requests.
        timeout: Request timeout in seconds.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "discourses-python/1.0.0",
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise APIError(f"Request timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise APIError("Failed to connect to API")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: requests Response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            AuthenticationError: For 401 responses
            RateLimitError: For 429 responses
            ValidationError: For 400/422 responses
            APIError: For other error responses
        """
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text or "Unknown error"}
        
        if response.status_code == 200:
            return data
        
        message = data.get("message", data.get("error", "Unknown error"))
        
        if response.status_code == 401:
            raise AuthenticationError(
                message=message,
                status_code=response.status_code,
                response=data,
            )
        
        if response.status_code == 429:
            retry_after = response.headers.get("X-RateLimit-Reset")
            raise RateLimitError(
                message=message,
                status_code=response.status_code,
                response=data,
                retry_after=int(retry_after) if retry_after else None,
            )
        
        if response.status_code in (400, 422):
            raise ValidationError(
                message=message,
                status_code=response.status_code,
                response=data,
            )
        
        raise APIError(
            message=message,
            status_code=response.status_code,
            response=data,
        )
    
    def analyze(
        self,
        text: str,
        era: Union[str, Era] = Era.ERA_4,
    ) -> AnalysisResult:
        """
        Analyze sentiment of text using era-specific lexicons.
        
        Each era captures the distinct financial vocabulary and sentiment
        patterns of its time period, from early social media through
        modern market discourse.
        
        Args:
            text: The text to analyze (news, social media, research, etc.)
            era: Era to use for analysis. Defaults to ERA_4 (modern market).
                 Options: ERA_1, ERA_2, ERA_3, ERA_4
        
        Returns:
            AnalysisResult with score, magnitude, confidence, and more.
        
        Raises:
            ValidationError: If text is empty or too long
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
        
        Example:
            >>> result = client.analyze(
            ...     text="Company beat earnings expectations",
            ...     era=Era.ERA_4
            ... )
            >>> print(f"Score: {result.score:.2f}")
            >>> print(f"Sentiment: {result.sentiment}")
            >>> print(f"Confidence: {result.confidence:.0%}")
        """
        if not text or not text.strip():
            raise ValidationError("text cannot be empty")
        
        era_value = str(era) if isinstance(era, Era) else era
        
        data = self._request(
            method="POST",
            endpoint=ENDPOINTS["analyze"],
            data={
                "text": text,
                "era": era_value,
            },
        )
        
        return AnalysisResult.from_dict(data)
    
    def compare(
        self,
        text: str,
        eras: Optional[List[Union[str, Era]]] = None,
    ) -> CompareResult:
        """
        Analyze text across multiple eras to understand semantic drift.
        
        Compare how the same text would be interpreted in different time
        periods, perfect for backtesting, historical analysis, and
        understanding how financial language evolves.
        
        Args:
            text: The text to analyze across eras.
            eras: List of eras to compare. Defaults to all eras.
        
        Returns:
            CompareResult with results per era and drift analysis.
        
        Raises:
            ValidationError: If text is empty or eras list is invalid
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
        
        Example:
            >>> result = client.compare("market disruption ahead")
            >>> 
            >>> # View results per era
            >>> for era_result in result.results:
            ...     print(f"{era_result.era}: {era_result.score:.2f}")
            >>>
            >>> # Check semantic drift
            >>> print(f"Max drift: {result.drift.max_drift:.2f}")
            >>> print(f"Trend: {result.drift.trend}")
        """
        if not text or not text.strip():
            raise ValidationError("text cannot be empty")
        
        request_data: Dict[str, Any] = {"text": text}
        
        if eras:
            request_data["eras"] = [str(e) if isinstance(e, Era) else e for e in eras]
        
        data = self._request(
            method="POST",
            endpoint=ENDPOINTS["compare"],
            data=request_data,
        )
        
        return CompareResult.from_dict(data)
    
    def batch(
        self,
        texts: List[str],
        era: Union[str, Era] = Era.ERA_4,
        compare_eras: bool = False,
    ) -> BatchResult:
        """
        Analyze multiple texts in a single request.
        
        Efficient batch processing for analyzing large volumes of text.
        Supports both single-era and multi-era comparison for each text.
        Ideal for processing news feeds, social media streams, or
        historical document analysis.
        
        Args:
            texts: List of texts to analyze (max 100 per request).
            era: Era to use for single-era mode. Ignored if compare_eras=True.
            compare_eras: If True, analyze each text across all eras
                         with drift detection.
        
        Returns:
            BatchResult with results for each text.
        
        Raises:
            ValidationError: If texts list is empty or exceeds limit
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
        
        Example:
            >>> # Single era batch
            >>> texts = ["Great quarter", "Missed expectations", "Steady growth"]
            >>> result = client.batch(texts, era=Era.ERA_4)
            >>> for item in result:
            ...     print(f"{item.index}: {item.result.sentiment}")
            >>>
            >>> # Multi-era comparison batch
            >>> result = client.batch(texts, compare_eras=True)
            >>> for item in result:
            ...     print(f"{item.index}: drift={item.comparison.drift.max_drift:.2f}")
        """
        if not texts:
            raise ValidationError("texts list cannot be empty")
        
        if len(texts) > 100:
            raise ValidationError("texts list cannot exceed 100 items")
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValidationError("texts list contains no valid text")
        
        era_value = str(era) if isinstance(era, Era) else era
        
        request_data: Dict[str, Any] = {
            "texts": valid_texts,
            "compare_eras": compare_eras,
        }
        
        if not compare_eras:
            request_data["era"] = era_value
        
        data = self._request(
            method="POST",
            endpoint=ENDPOINTS["batch"],
            data=request_data,
        )
        
        return BatchResult.from_dict(data)
    
    def __repr__(self) -> str:
        return f"Discourses(base_url='{self.base_url}')"

