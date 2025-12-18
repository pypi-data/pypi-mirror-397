"""
CultureCoded API Client for Python.
"""

from typing import Dict, List, Optional, Any, Literal
from urllib.parse import quote

import requests

from .types import (
    Analysis,
    EthnicGroup,
    ExportResult,
    User,
    UsageStats,
    CultureCodedError,
)


DesignType = Literal[
    "landing_page",
    "mobile_app",
    "dashboard",
    "ecommerce",
    "social_media",
    "email",
    "advertisement",
    "other",
]

ExportFormat = Literal["pdf", "csv", "figma"]


class CultureCoded:
    """
    CultureCoded API Client.
    
    Official Python SDK for the CultureCoded Cultural UX Intelligence Platform.
    
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

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://culturecoded.replit.app",
    ):
        """
        Initialize the CultureCoded client.
        
        Args:
            api_key: Your CultureCoded API key. Get one at https://culturecoded.io/api-docs
            base_url: API base URL (defaults to production)
        """
        if not api_key:
            raise ValueError("API key is required. Get one at https://culturecoded.io/api-docs")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "culturecoded-sdk-python/1.0.0",
        })

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an API request."""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.request(method, url, json=json)
            
            if not response.ok:
                try:
                    error_data = response.json()
                    message = error_data.get("message", f"Request failed with status {response.status_code}")
                    code = error_data.get("code")
                except Exception:
                    message = f"Request failed with status {response.status_code}"
                    code = None
                
                raise CultureCodedError(message, response.status_code, code)
            
            if response.status_code == 204:
                return None
            
            return response.json()
            
        except requests.RequestException as e:
            raise CultureCodedError(f"Network error: {str(e)}")

    # ============================================
    # Cultural Analysis
    # ============================================

    def analyze_design(
        self,
        target_region: str,
        target_country: str,
        design_type: DesignType,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        ethnic_group: Optional[str] = None,
        industry: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> Analysis:
        """
        Analyze a design for cultural adaptation recommendations.
        
        Args:
            target_region: Target region (e.g., "Africa", "Asia-Pacific", "Europe")
            target_country: Target country within the region
            design_type: Type of design being analyzed
            image_url: URL of the design image to analyze
            image_base64: Base64-encoded image data (alternative to image_url)
            ethnic_group: Optional ethnic group for more targeted analysis
            industry: Industry context (e.g., "fintech", "healthcare")
            additional_context: Additional context or notes
        
        Returns:
            Analysis object with recommendations and cultural insights
        
        Example:
            >>> analysis = cc.analyze_design(
            ...     image_url="https://example.com/landing.png",
            ...     target_region="Africa",
            ...     target_country="Nigeria",
            ...     ethnic_group="Yoruba",
            ...     design_type="landing_page",
            ...     industry="fintech"
            ... )
        """
        if not image_url and not image_base64:
            raise ValueError("Either image_url or image_base64 is required")
        
        payload: Dict[str, Any] = {
            "targetRegion": target_region,
            "targetCountry": target_country,
            "designType": design_type,
        }
        
        if image_url:
            payload["imageUrl"] = image_url
        if image_base64:
            payload["imageBase64"] = image_base64
        if ethnic_group:
            payload["ethnicGroup"] = ethnic_group
        if industry:
            payload["industry"] = industry
        if additional_context:
            payload["additionalContext"] = additional_context
        
        data = self._request("POST", "/api/v1/analyze", json=payload)
        return Analysis.from_dict(data)

    def get_analyses(self) -> List[Analysis]:
        """
        Get all analyses for the authenticated user.
        
        Returns:
            List of Analysis objects
        """
        data = self._request("GET", "/api/v1/analyses")
        return [Analysis.from_dict(a) for a in data]

    def get_analysis(self, analysis_id: str) -> Analysis:
        """
        Get a specific analysis by ID.
        
        Args:
            analysis_id: The analysis ID
        
        Returns:
            Full Analysis object with recommendations
        """
        data = self._request("GET", f"/api/v1/analyses/{analysis_id}")
        return Analysis.from_dict(data)

    def delete_analysis(self, analysis_id: str) -> None:
        """
        Delete an analysis.
        
        Args:
            analysis_id: The analysis ID to delete
        """
        self._request("DELETE", f"/api/v1/analyses/{analysis_id}")

    # ============================================
    # Cultural Communities (Ethnic Groups)
    # ============================================

    def get_ethnic_groups(self, country: str) -> List[EthnicGroup]:
        """
        Get available cultural communities for a specific country.
        
        Args:
            country: Country name (e.g., "Nigeria", "Kenya")
        
        Returns:
            List of EthnicGroup objects with cultural dimension profiles
        
        Example:
            >>> groups = cc.get_ethnic_groups("Nigeria")
            >>> for group in groups:
            ...     print(group.name)
            Yoruba
            Igbo
            Hausa-Fulani
        """
        data = self._request("GET", f"/api/v1/ethnic-groups/{quote(country)}")
        return [EthnicGroup.from_dict(g) for g in data]

    def get_regions(self) -> Dict[str, List[str]]:
        """
        Get all available regions and their countries.
        
        Returns:
            Dictionary mapping region names to lists of country names
        """
        return self._request("GET", "/api/v1/regions")

    # ============================================
    # Export & Integrations
    # ============================================

    def export_analysis(
        self,
        analysis_id: str,
        format: ExportFormat,
        figma_file_key: Optional[str] = None,
    ) -> ExportResult:
        """
        Export an analysis in various formats.
        
        Args:
            analysis_id: The analysis ID to export
            format: Export format ("pdf", "csv", or "figma")
            figma_file_key: Required for Figma exports
        
        Returns:
            ExportResult with download URL or Figma data
        
        Example:
            >>> pdf_export = cc.export_analysis("abc123", format="pdf")
            >>> print(pdf_export.download_url)
        """
        if format == "figma" and not figma_file_key:
            raise ValueError("figma_file_key is required for Figma exports")
        
        payload: Dict[str, Any] = {
            "analysisId": analysis_id,
            "format": format,
        }
        if figma_file_key:
            payload["figmaFileKey"] = figma_file_key
        
        data = self._request("POST", "/api/v1/exports", json=payload)
        return ExportResult.from_dict(data)

    def export_to_figma(self, analysis_id: str, figma_file_key: str) -> ExportResult:
        """
        Export an analysis to Figma.
        
        Args:
            analysis_id: The analysis ID to export
            figma_file_key: Figma file key to update
        
        Returns:
            ExportResult with Figma data
        """
        return self.export_analysis(analysis_id, format="figma", figma_file_key=figma_file_key)

    def get_exports(self) -> List[ExportResult]:
        """
        Get all exports for the authenticated user.
        
        Returns:
            List of ExportResult objects
        """
        data = self._request("GET", "/api/v1/exports")
        return [ExportResult.from_dict(e) for e in data]

    # ============================================
    # User & Credits
    # ============================================

    def get_user(self) -> User:
        """
        Get current user profile.
        
        Returns:
            User object including credits and tier
        """
        data = self._request("GET", "/api/v1/user")
        return User.from_dict(data)

    def get_usage(self) -> UsageStats:
        """
        Get API usage statistics for the current billing period.
        
        Returns:
            UsageStats object
        """
        data = self._request("GET", "/api/v1/stats")
        return UsageStats.from_dict(data)
