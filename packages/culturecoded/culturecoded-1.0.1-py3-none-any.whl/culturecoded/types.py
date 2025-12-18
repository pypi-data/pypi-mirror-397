"""
Type definitions for the CultureCoded SDK.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Literal


@dataclass
class CulturalDimensions:
    """Cultural dimension scores based on Hofstede's model."""
    
    power_distance: Optional[float] = None
    individualism: Optional[float] = None
    masculinity: Optional[float] = None
    uncertainty_avoidance: Optional[float] = None
    long_term_orientation: Optional[float] = None
    indulgence: Optional[float] = None
    context_style: Optional[Literal["high", "low"]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CulturalDimensions":
        return cls(
            power_distance=data.get("powerDistance"),
            individualism=data.get("individualism"),
            masculinity=data.get("masculinity"),
            uncertainty_avoidance=data.get("uncertaintyAvoidance"),
            long_term_orientation=data.get("longTermOrientation"),
            indulgence=data.get("indulgence"),
            context_style=data.get("contextStyle"),
        )


@dataclass
class Recommendation:
    """A cultural design recommendation."""
    
    category: str
    priority: Literal["high", "medium", "low"]
    suggestion: str
    cultural_rationale: Optional[str] = None
    research_framework: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recommendation":
        return cls(
            category=data.get("category", ""),
            priority=data.get("priority", "medium"),
            suggestion=data.get("suggestion", ""),
            cultural_rationale=data.get("culturalRationale"),
            research_framework=data.get("researchFramework"),
        )


@dataclass
class ResearchSource:
    """A research framework source used in analysis."""
    
    framework: str
    author: str
    region: Optional[str] = None
    year: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchSource":
        return cls(
            framework=data.get("framework", ""),
            author=data.get("author", ""),
            region=data.get("region"),
            year=data.get("year"),
        )


@dataclass
class Analysis:
    """A cultural design analysis result."""
    
    id: str
    user_id: str
    target_region: str
    target_country: str
    design_type: str
    recommendations: List[Recommendation] = field(default_factory=list)
    ethnic_group: Optional[str] = None
    industry: Optional[str] = None
    cultural_dimensions: Optional[CulturalDimensions] = None
    research_sources: List[ResearchSource] = field(default_factory=list)
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Analysis":
        recommendations = [
            Recommendation.from_dict(r) for r in data.get("recommendations", [])
        ]
        research_sources = [
            ResearchSource.from_dict(s) for s in data.get("researchSources", [])
        ]
        cultural_dimensions = None
        if data.get("culturalDimensions"):
            cultural_dimensions = CulturalDimensions.from_dict(data["culturalDimensions"])
        
        return cls(
            id=data.get("id", ""),
            user_id=data.get("userId", ""),
            target_region=data.get("targetRegion", ""),
            target_country=data.get("targetCountry", ""),
            design_type=data.get("designType", ""),
            recommendations=recommendations,
            ethnic_group=data.get("ethnicGroup"),
            industry=data.get("industry"),
            cultural_dimensions=cultural_dimensions,
            research_sources=research_sources,
            created_at=data.get("createdAt"),
        )


@dataclass
class EthnicGroup:
    """A cultural community within a country."""
    
    id: int
    name: str
    country: str
    cultural_dimensions: Optional[CulturalDimensions] = None
    design_considerations: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EthnicGroup":
        cultural_dimensions = None
        if data.get("culturalDimensions"):
            cultural_dimensions = CulturalDimensions.from_dict(data["culturalDimensions"])
        
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            country=data.get("country", ""),
            cultural_dimensions=cultural_dimensions,
            design_considerations=data.get("designConsiderations", []),
        )


@dataclass
class ExportResult:
    """Result of an export operation."""
    
    format: str
    credit_cost: int
    id: Optional[str] = None
    download_url: Optional[str] = None
    figma_data: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None
    analysis_id: Optional[str] = None
    exported_at: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExportResult":
        return cls(
            id=data.get("id"),
            format=data.get("format", ""),
            credit_cost=data.get("creditCost", 0),
            download_url=data.get("downloadUrl"),
            figma_data=data.get("figmaData"),
            success=data.get("success"),
            analysis_id=data.get("analysisId"),
            exported_at=data.get("exportedAt"),
            message=data.get("message"),
        )


@dataclass
class User:
    """User profile information."""
    
    id: str
    email: str
    credits: int
    tier: Literal["starter", "professional", "enterprise"]
    username: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            credits=data.get("credits", 0),
            tier=data.get("tier", "starter"),
            username=data.get("username"),
        )


@dataclass
class UsageStats:
    """API usage statistics."""
    
    analyses_this_month: int
    credits_used: int
    credits_remaining: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageStats":
        return cls(
            analyses_this_month=data.get("analysesThisMonth", 0),
            credits_used=data.get("creditsUsed", 0),
            credits_remaining=data.get("creditsRemaining", 0),
        )


class CultureCodedError(Exception):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

    def __str__(self) -> str:
        if self.status_code:
            return f"CultureCodedError ({self.status_code}): {self.message}"
        return f"CultureCodedError: {self.message}"
