"""
Discourses - Official Python SDK

Institutional-grade financial sentiment analysis with era-calibrated lexicons.

Basic Usage:
    >>> from discourses import Discourses
    >>> 
    >>> client = Discourses(api_key="your-api-key")
    >>> 
    >>> # Analyze single text
    >>> result = client.analyze("Apple reported record earnings")
    >>> print(f"Score: {result.score:.2f}, Sentiment: {result.sentiment}")
    >>> 
    >>> # Compare across eras
    >>> comparison = client.compare("Market disruption ahead")
    >>> for era in comparison.results:
    ...     print(f"{era.era}: {era.score:.2f}")
    >>> 
    >>> # Batch analysis
    >>> texts = ["Great quarter", "Missed expectations"]
    >>> batch = client.batch(texts)
    >>> for item in batch:
    ...     print(f"{item.result.sentiment}")

For more information, visit https://discourses.io/documentation
"""

__version__ = "1.0.0"
__author__ = "Discourses"
__email__ = "contact@discourses.dev"

# Main client
from discourses.client import Discourses

# Constants and enums
from discourses.constants import Era, BASE_URL

# Exception classes
from discourses.exceptions import (
    DiscoursesError,
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ResourceNotFoundError,
)

# Response models
from discourses.models import (
    AnalysisResult,
    CompareResult,
    BatchResult,
    BatchItem,
    EraResult,
    DriftAnalysis,
)

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Main client
    "Discourses",
    # Enums
    "Era",
    # Constants
    "BASE_URL",
    # Exceptions
    "DiscoursesError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ResourceNotFoundError",
    # Models
    "AnalysisResult",
    "CompareResult",
    "BatchResult",
    "BatchItem",
    "EraResult",
    "DriftAnalysis",
]
