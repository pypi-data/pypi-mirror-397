"""
CultureCoded SDK

Official Python SDK for the CultureCoded Cultural UX Intelligence Platform.
Analyze designs for cultural adaptation and get AI-powered recommendations
based on 11 cross-cultural research frameworks.

Example:
    >>> from culturecoded import CultureCoded
    >>> 
    >>> cc = CultureCoded(api_key="your-api-key")
    >>> 
    >>> analysis = cc.analyze_design(
    ...     image_url="https://example.com/design.png",
    ...     target_region="Africa",
    ...     target_country="Nigeria",
    ...     ethnic_group="Yoruba",
    ...     design_type="landing_page",
    ...     industry="fintech"
    ... )
    >>> 
    >>> for rec in analysis.recommendations:
    ...     print(f"{rec.category}: {rec.suggestion}")
"""

from .client import CultureCoded
from .types import (
    Analysis,
    Recommendation,
    CulturalDimensions,
    ResearchSource,
    EthnicGroup,
    ExportResult,
    User,
    UsageStats,
    CultureCodedError,
)

__version__ = "1.0.1"
__all__ = [
    "CultureCoded",
    "Analysis",
    "Recommendation",
    "CulturalDimensions",
    "ResearchSource",
    "EthnicGroup",
    "ExportResult",
    "User",
    "UsageStats",
    "CultureCodedError",
]
