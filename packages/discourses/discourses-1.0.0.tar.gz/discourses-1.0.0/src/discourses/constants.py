"""
Constants for the Discourses SDK.

This module defines API configuration values, endpoints, and enumerations
used throughout the SDK.
"""

from enum import Enum


# API Configuration
BASE_URL = "https://discourses.io/api/v1"
DEFAULT_TIMEOUT = 30  # seconds


# API Endpoints
ENDPOINTS = {
    "analyze": "/analyze",
    "compare": "/compare",
    "batch": "/batch",
}


class Era(str, Enum):
    """
    Financial language eras for sentiment analysis.
    
    Each era captures distinct vocabulary and sentiment patterns
    characteristic of that time period in financial markets.
    
    Attributes:
        ERA_1: Early social media era (2007-2011)
               - Emergence of financial Twitter/StockTwits
               - Simple sentiment vocabulary
               - High signal-to-noise ratio
        
        ERA_2: Post-crisis recovery (2012-2015)
               - QE-influenced language
               - Recovery optimism patterns
               - Regulatory terminology surge
        
        ERA_3: Algorithmic trading rise (2016-2019)
               - Machine-readable language adoption
               - Crypto/fintech vocabulary emergence
               - Volatility event terminology
        
        ERA_4: Modern market discourse (2020-present)
               - Pandemic market vocabulary
               - Retail trading revolution (meme stocks)
               - Fed policy sensitivity
               - Most comprehensive lexicon
    
    Example:
        >>> from discourses import Era
        >>> client.analyze("Market disruption ahead", era=Era.ERA_4)
    """
    
    ERA_1 = "era_1"
    ERA_2 = "era_2"
    ERA_3 = "era_3"
    ERA_4 = "era_4"
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def all(cls) -> list:
        """Return list of all eras."""
        return [era for era in cls]
    
    @classmethod
    def from_string(cls, value: str) -> "Era":
        """
        Create Era from string value.
        
        Args:
            value: Era string (e.g., 'era_1', 'ERA_1', '1')
        
        Returns:
            Matching Era enum
        
        Raises:
            ValueError: If no matching era found
        """
        value = value.lower().strip()
        
        # Handle direct enum names
        if value in ("era_1", "1"):
            return cls.ERA_1
        if value in ("era_2", "2"):
            return cls.ERA_2
        if value in ("era_3", "3"):
            return cls.ERA_3
        if value in ("era_4", "4"):
            return cls.ERA_4
        
        raise ValueError(f"Unknown era: {value}")


# Rate Limiting
RATE_LIMIT_REQUESTS = 100  # requests per minute (varies by plan)
