"""
Data models for the Discourses SDK.

This module defines dataclasses for API request and response objects,
providing type-safe access to analysis results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class AnalysisResult:
    """
    Result from single text sentiment analysis.
    
    Contains the sentiment score, classification, and detailed metrics
    from analyzing text with an era-specific lexicon.
    
    Attributes:
        score: Sentiment score (-1.0 to 1.0)
               Negative = bearish, Positive = bullish
        sentiment: Categorical sentiment (positive, negative, neutral)
        magnitude: Strength of sentiment (0.0 to 1.0)
        confidence: Model confidence in the result (0.0 to 1.0)
        era: Era lexicon used for analysis
        word_count: Number of words in the text
        matches: Sentiment words found and their individual scores
        processing_time_ms: API processing time in milliseconds
        raw: Raw API response for advanced usage
    
    Example:
        >>> result = client.analyze("Strong revenue growth")
        >>> print(f"Score: {result.score:.2f}")  # Score: 0.65
        >>> print(f"Sentiment: {result.sentiment}")  # Sentiment: positive
        >>> print(f"Confidence: {result.confidence:.0%}")  # Confidence: 92%
    """
    
    score: float
    sentiment: str
    magnitude: float
    confidence: float
    era: str
    word_count: int = 0
    matches: List[Dict[str, Any]] = field(default_factory=list)
    processing_time_ms: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create AnalysisResult from API response dictionary."""
        return cls(
            score=float(data.get("score", 0)),
            sentiment=data.get("sentiment", "neutral"),
            magnitude=float(data.get("magnitude", 0)),
            confidence=float(data.get("confidence", 0)),
            era=data.get("era", ""),
            word_count=int(data.get("word_count", 0)),
            matches=data.get("matches", []),
            processing_time_ms=data.get("processing_time_ms"),
            raw=data,
        )
    
    @property
    def is_positive(self) -> bool:
        """True if sentiment is positive."""
        return self.sentiment == "positive"
    
    @property
    def is_negative(self) -> bool:
        """True if sentiment is negative."""
        return self.sentiment == "negative"
    
    @property
    def is_neutral(self) -> bool:
        """True if sentiment is neutral."""
        return self.sentiment == "neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "sentiment": self.sentiment,
            "magnitude": self.magnitude,
            "confidence": self.confidence,
            "era": self.era,
            "word_count": self.word_count,
            "matches": self.matches,
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class EraResult:
    """
    Sentiment result for a specific era in comparison analysis.
    
    Attributes:
        era: Era identifier (era_1, era_2, era_3, era_4)
        score: Sentiment score for this era (-1.0 to 1.0)
        sentiment: Categorical sentiment (positive, negative, neutral)
        magnitude: Strength of sentiment (0.0 to 1.0)
        confidence: Model confidence (0.0 to 1.0)
    """
    
    era: str
    score: float
    sentiment: str
    magnitude: float
    confidence: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EraResult":
        """Create EraResult from API response dictionary."""
        return cls(
            era=data.get("era", ""),
            score=float(data.get("score", 0)),
            sentiment=data.get("sentiment", "neutral"),
            magnitude=float(data.get("magnitude", 0)),
            confidence=float(data.get("confidence", 0)),
        )


@dataclass
class DriftAnalysis:
    """
    Semantic drift analysis across eras.
    
    Measures how sentiment interpretation changes across time periods,
    essential for understanding historical context and backtesting.
    
    Attributes:
        max_drift: Maximum score difference between any two eras
        min_score: Lowest score across all eras
        max_score: Highest score across all eras
        mean_score: Average score across all eras
        std_dev: Standard deviation of scores
        trend: Direction of drift (increasing, decreasing, stable)
        drift_pairs: Detailed drift between specific era pairs
    """
    
    max_drift: float
    min_score: float
    max_score: float
    mean_score: float
    std_dev: float
    trend: str
    drift_pairs: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DriftAnalysis":
        """Create DriftAnalysis from API response dictionary."""
        return cls(
            max_drift=float(data.get("max_drift", 0)),
            min_score=float(data.get("min_score", 0)),
            max_score=float(data.get("max_score", 0)),
            mean_score=float(data.get("mean_score", 0)),
            std_dev=float(data.get("std_dev", 0)),
            trend=data.get("trend", "stable"),
            drift_pairs=data.get("drift_pairs", []),
        )
    
    @property
    def has_significant_drift(self) -> bool:
        """True if drift exceeds 0.2 threshold."""
        return abs(self.max_drift) > 0.2


@dataclass
class CompareResult:
    """
    Result from comparing text across multiple eras.
    
    Provides per-era sentiment analysis and drift metrics to understand
    how the same text would be interpreted in different time periods.
    
    Attributes:
        text: Original text that was analyzed
        results: List of EraResult for each analyzed era
        drift: Drift analysis metrics
        processing_time_ms: API processing time in milliseconds
        raw: Raw API response for advanced usage
    
    Example:
        >>> comparison = client.compare("Market disruption ahead")
        >>> 
        >>> # Access per-era results
        >>> for era in comparison.results:
        ...     print(f"{era.era}: {era.score:.2f} ({era.sentiment})")
        >>> 
        >>> # Check semantic drift
        >>> if comparison.drift.has_significant_drift:
        ...     print(f"Warning: High drift ({comparison.drift.max_drift:.2f})")
    """
    
    text: str
    results: List[EraResult]
    drift: DriftAnalysis
    processing_time_ms: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompareResult":
        """Create CompareResult from API response dictionary."""
        results = [EraResult.from_dict(r) for r in data.get("results", [])]
        drift = DriftAnalysis.from_dict(data.get("drift", {}))
        
        return cls(
            text=data.get("text", ""),
            results=results,
            drift=drift,
            processing_time_ms=data.get("processing_time_ms"),
            raw=data,
        )
    
    def get_era(self, era: str) -> Optional[EraResult]:
        """Get result for a specific era."""
        for result in self.results:
            if result.era == era:
                return result
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "text": self.text,
            "results": [
                {
                    "era": r.era,
                    "score": r.score,
                    "sentiment": r.sentiment,
                    "magnitude": r.magnitude,
                    "confidence": r.confidence,
                }
                for r in self.results
            ],
            "drift": {
                "max_drift": self.drift.max_drift,
                "min_score": self.drift.min_score,
                "max_score": self.drift.max_score,
                "mean_score": self.drift.mean_score,
                "trend": self.drift.trend,
            },
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class BatchItem:
    """
    Single item result from batch analysis.
    
    Attributes:
        index: Index in the original texts array
        text: The analyzed text
        result: AnalysisResult (for single-era mode)
        comparison: CompareResult (for compare_eras mode)
        error: Error message if this item failed
    """
    
    index: int
    text: str
    result: Optional[AnalysisResult] = None
    comparison: Optional[CompareResult] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchItem":
        """Create BatchItem from API response dictionary."""
        result = None
        comparison = None
        
        if "result" in data:
            result = AnalysisResult.from_dict(data["result"])
        if "comparison" in data:
            comparison = CompareResult.from_dict(data["comparison"])
        
        return cls(
            index=data.get("index", 0),
            text=data.get("text", ""),
            result=result,
            comparison=comparison,
            error=data.get("error"),
        )
    
    @property
    def succeeded(self) -> bool:
        """True if this item was processed successfully."""
        return self.error is None


@dataclass
class BatchResult:
    """
    Result from batch text analysis.
    
    Contains results for each text in the batch, with support for
    both single-era and multi-era comparison modes.
    
    Attributes:
        items: List of BatchItem results
        total_count: Total number of texts processed
        success_count: Number of successfully processed texts
        error_count: Number of failed texts
        processing_time_ms: Total API processing time
        raw: Raw API response for advanced usage
    
    Example:
        >>> texts = ["Great quarter", "Missed expectations", "Steady growth"]
        >>> batch = client.batch(texts)
        >>> 
        >>> # Iterate over results
        >>> for item in batch:
        ...     if item.succeeded:
        ...         print(f"{item.index}: {item.result.sentiment}")
        ...     else:
        ...         print(f"{item.index}: Error - {item.error}")
        >>> 
        >>> # Check success rate
        >>> print(f"Processed: {batch.success_count}/{batch.total_count}")
    """
    
    items: List[BatchItem]
    total_count: int = 0
    success_count: int = 0
    error_count: int = 0
    processing_time_ms: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchResult":
        """Create BatchResult from API response dictionary."""
        items = [BatchItem.from_dict(item) for item in data.get("items", [])]
        
        return cls(
            items=items,
            total_count=data.get("total_count", len(items)),
            success_count=data.get("success_count", sum(1 for i in items if i.succeeded)),
            error_count=data.get("error_count", sum(1 for i in items if not i.succeeded)),
            processing_time_ms=data.get("processing_time_ms"),
            raw=data,
        )
    
    def __iter__(self) -> Iterator[BatchItem]:
        """Iterate over batch items."""
        return iter(self.items)
    
    def __len__(self) -> int:
        """Return number of items in batch."""
        return len(self.items)
    
    def __getitem__(self, index: int) -> BatchItem:
        """Get item by index."""
        return self.items[index]
    
    @property
    def all_succeeded(self) -> bool:
        """True if all items were processed successfully."""
        return self.error_count == 0
    
    def get_successful(self) -> List[BatchItem]:
        """Get only successfully processed items."""
        return [item for item in self.items if item.succeeded]
    
    def get_failed(self) -> List[BatchItem]:
        """Get only failed items."""
        return [item for item in self.items if not item.succeeded]
