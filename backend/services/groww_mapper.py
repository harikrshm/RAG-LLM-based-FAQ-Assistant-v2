"""
Groww Page Mapping Service

Maps user queries and retrieved content to relevant Groww website pages.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin

from backend.config.settings import settings
from backend.models.knowledge import KnowledgeChunk
from backend.utils.config_loader import get_groww_mappings

logger = logging.getLogger(__name__)


class InformationCategory(str):
    """Categories of information that can be shown on Groww."""
    FUND_DETAILS = "fund_details"
    AMC_OVERVIEW = "amc_overview"
    FUND_PERFORMANCE = "fund_performance"
    FUND_COMPARISON = "fund_comparison"
    AMC_FUNDS_LIST = "amc_funds_list"
    CATEGORY_FUNDS = "category_funds"
    BLOG_ARTICLE = "blog_article"
    GENERAL_INFO = "general_info"


class GrówwPageMapper:
    """
    Service to map queries and content to Groww website pages.
    
    Implements the fallback logic: prioritize Groww pages first,
    then fall back to external AMC/SEBI/AMFI sources.
    """
    
    def __init__(self):
        """Initialize the Groww page mapper."""
        # Load configuration from file
        self.config = get_groww_mappings()
        self.base_url = self.config.get("base_url", settings.GROWW_BASE_URL)
        
        # Load mappings from config
        self.amc_mappings = self.config.get("amc_mappings", {})
        self.url_patterns = self.config.get("url_patterns", {})
        self.query_patterns = self.config.get("query_patterns", {})
        self.information_categories = self.config.get("information_categories", {})
        self.page_sections = self.config.get("page_sections", {})
        
        # Build regex patterns from query patterns
        self._build_query_patterns()
        
        logger.info(f"GrowwPageMapper initialized with base URL: {self.base_url}")
        logger.info(f"Loaded {len(self.amc_mappings)} AMC mappings")
        logger.info(f"Loaded {len(self.url_patterns)} URL patterns")
    
    def _build_query_patterns(self):
        """Build regex patterns from query patterns configuration."""
        self.QUERY_PATTERNS = {}
        
        for category, patterns in self.query_patterns.items():
            regex_patterns = []
            for pattern in patterns:
                # Convert simple string patterns to regex
                # Escape special characters and make case-insensitive
                escaped = re.escape(pattern.lower())
                regex_patterns.append(escaped)
            
            self.QUERY_PATTERNS[category] = regex_patterns
    
    def find_groww_page(
        self,
        query: str,
        chunks: List[KnowledgeChunk],
    ) -> Optional[str]:
        """
        Find the most relevant Groww page for a query and retrieved chunks.
        
        Args:
            query: User's question
            chunks: Retrieved knowledge chunks
            
        Returns:
            Groww page URL if available, None otherwise
        """
        # Strategy 1: Check if chunks already have Groww page mappings
        groww_url = self._extract_groww_from_chunks(chunks)
        if groww_url:
            logger.info(f"Found Groww page from chunks: {groww_url}")
            return groww_url
        
        # Strategy 2: Identify query category and construct Groww URL
        category = self._identify_query_category(query)
        logger.debug(f"Query category identified: {category}")
        
        # Strategy 3: Extract entities (AMC, fund name) from query
        amc_slug = self._extract_amc_from_query(query)
        fund_slug = self._extract_fund_from_chunks(chunks)
        
        # Build Groww URL based on category and entities
        # Use string comparison for flexibility with config-based categories
        category_str = str(category)
        
        if category_str == InformationCategory.FUND_DETAILS or category_str == "fund_details":
            if fund_slug:
                # Check if we need a specific section (e.g., expense ratio)
                section = self._identify_section_from_query(query)
                return self._build_fund_url(fund_slug, section)
        
        elif category_str == InformationCategory.AMC_OVERVIEW or category_str == "amc_overview":
            if amc_slug:
                return self._build_amc_url(amc_slug)
        
        elif category_str == InformationCategory.AMC_FUNDS_LIST or category_str == "amc_funds_list":
            if amc_slug:
                return self._build_amc_funds_url(amc_slug)
        
        elif category_str == InformationCategory.FUND_COMPARISON or category_str == "fund_comparison":
            pattern_config = self.url_patterns.get("fund_comparison", {})
            pattern = pattern_config.get("pattern", "/mutual-funds/compare")
            return urljoin(self.base_url, pattern)
        
        # If no specific Groww page found, return None
        # (caller will fall back to external sources)
        logger.debug("No specific Groww page found for query")
        return None
    
    def _extract_groww_from_chunks(
        self,
        chunks: List[KnowledgeChunk],
    ) -> Optional[str]:
        """
        Extract Groww page URL from knowledge chunks.
        
        Prioritizes chunks that already have Groww page mappings.
        
        Args:
            chunks: List of knowledge chunks
            
        Returns:
            Groww URL if found, None otherwise
        """
        for chunk in chunks:
            if chunk.groww_page_url:
                return chunk.groww_page_url
            
            # Also check if source_url is a Groww URL
            if "groww.in" in chunk.source_url.lower():
                return chunk.source_url
        
        return None
    
    def _identify_query_category(self, query: str) -> str:
        """
        Identify the information category from the query.
        
        Args:
            query: User's question
            
        Returns:
            Information category
        """
        query_lower = query.lower()
        
        # Check each category's patterns from config
        for category, patterns in self.QUERY_PATTERNS.items():
            for pattern in patterns:
                # Try exact match first (for simple string patterns)
                if pattern in query_lower:
                    return category
                # Try regex match
                try:
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        return category
                except re.error:
                    # If pattern is not valid regex, skip it
                    continue
        
        # Map to InformationCategory enum if available
        if InformationCategory.GENERAL_INFO:
            return InformationCategory.GENERAL_INFO
        return "general_info"
    
    def _extract_amc_from_query(self, query: str) -> Optional[str]:
        """
        Extract AMC slug from query text.
        
        Args:
            query: User's question
            
        Returns:
            AMC slug for Groww URL or None
        """
        query_lower = query.lower()
        
        # Check for AMC name variations from config
        for amc_variant, amc_slug in self.amc_mappings.items():
            if amc_variant.lower() in query_lower:
                logger.debug(f"Extracted AMC from query: {amc_slug}")
                return amc_slug
        
        return None
    
    def _extract_fund_from_chunks(
        self,
        chunks: List[KnowledgeChunk],
    ) -> Optional[str]:
        """
        Extract fund slug from knowledge chunks.
        
        Args:
            chunks: List of knowledge chunks
            
        Returns:
            Fund slug for Groww URL or None
        """
        for chunk in chunks:
            # If source URL is a Groww fund page, extract slug
            if "groww.in/mutual-funds/" in chunk.source_url:
                # Extract the slug from URL like:
                # https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
                parts = chunk.source_url.split("/mutual-funds/")
                if len(parts) == 2:
                    fund_slug = parts[1].split("?")[0].strip("/")
                    if fund_slug and fund_slug != "amc":
                        logger.debug(f"Extracted fund slug: {fund_slug}")
                        return fund_slug
        
        return None
    
    def _identify_section_from_query(self, query: str) -> Optional[str]:
        """
        Identify page section from query (e.g., expense_ratio, exit_load).
        
        Args:
            query: User's question
            
        Returns:
            Section identifier or None
        """
        query_lower = query.lower()
        
        # Check page sections configuration
        for section_id, section_config in self.page_sections.items():
            # Check if section name appears in query
            section_name = section_id.replace("_", " ")
            if section_name in query_lower:
                return section_id
            
            # Check keywords if available
            keywords = section_config.get("keywords", [])
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        return section_id
        
        return None
    
    def _build_fund_url(self, fund_slug: str, section: Optional[str] = None) -> str:
        """
        Build Groww URL for a specific fund page.
        
        Args:
            fund_slug: Fund identifier slug
            section: Optional section anchor (e.g., "expense_ratio")
            
        Returns:
            Complete Groww URL
        """
        pattern_config = self.url_patterns.get("fund_details", {})
        pattern = pattern_config.get("pattern", "/mutual-funds/{fund_slug}")
        
        url = urljoin(self.base_url, pattern.format(fund_slug=fund_slug))
        
        # Add section anchor if provided
        if section:
            section_config = self.page_sections.get(section, {})
            section_id = section_config.get("section_id", f"#{section}")
            url += section_id
        
        return url
    
    def _build_amc_url(self, amc_slug: str) -> str:
        """
        Build Groww URL for an AMC overview page.
        
        Args:
            amc_slug: AMC identifier slug
            
        Returns:
            Complete Groww URL
        """
        pattern_config = self.url_patterns.get("amc_overview", {})
        pattern = pattern_config.get("pattern", "/mutual-funds/amc/{amc_slug}")
        
        return urljoin(self.base_url, pattern.format(amc_slug=amc_slug))
    
    def _build_amc_funds_url(self, amc_slug: str) -> str:
        """
        Build Groww URL for AMC's funds listing.
        
        Args:
            amc_slug: AMC identifier slug
            
        Returns:
            Complete Groww URL
        """
        pattern_config = self.url_patterns.get("amc_funds_list", {})
        pattern = pattern_config.get("pattern", "/mutual-funds/top/best-{amc_name}-equity-mutual-funds")
        
        # Extract AMC name from slug (e.g., "hdfc-mutual-funds" -> "hdfc")
        amc_name = amc_slug.split("-")[0]
        
        return urljoin(self.base_url, pattern.format(amc_name=amc_name))
    
    def check_groww_availability(
        self,
        query: str,
        chunks: List[KnowledgeChunk],
    ) -> Dict[str, Any]:
        """
        Check if information is available on Groww and provide details.
        
        Args:
            query: User's question
            chunks: Retrieved knowledge chunks
            
        Returns:
            Dictionary with availability info and URL
        """
        groww_url = self.find_groww_page(query, chunks)
        
        has_groww_source = any(
            "groww.in" in chunk.source_url.lower() 
            for chunk in chunks
        )
        
        return {
            "is_available_on_groww": groww_url is not None,
            "groww_page_url": groww_url,
            "has_groww_source": has_groww_source,
            "source_count": len([c for c in chunks if "groww.in" in c.source_url.lower()]),
            "total_chunks": len(chunks),
        }
    
    def prioritize_sources(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Reorder sources to prioritize Groww URLs first.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Reordered list with Groww sources first
        """
        groww_sources = []
        external_sources = []
        
        for source in sources:
            url = source.get("url", "")
            if "groww.in" in url.lower():
                groww_sources.append(source)
            else:
                external_sources.append(source)
        
        # Groww sources first, then external
        return groww_sources + external_sources
    
    def get_fallback_sources(
        self,
        chunks: List[KnowledgeChunk],
    ) -> List[Dict[str, Any]]:
        """
        Get fallback sources when Groww page is not available.
        
        Returns external AMC/SEBI/AMFI sources.
        
        Args:
            chunks: Retrieved knowledge chunks
            
        Returns:
            List of external source dictionaries
        """
        external_sources = []
        seen_urls = set()
        
        for chunk in chunks:
            url = chunk.source_url
            
            # Skip Groww URLs
            if "groww.in" in url.lower():
                continue
            
            # Skip duplicates
            if url in seen_urls:
                continue
            
            seen_urls.add(url)
            external_sources.append({
                "url": url,
                "title": chunk.metadata.title,
                "amc_name": chunk.metadata.amc_name,
                "content_type": chunk.metadata.content_type,
            })
        
        return external_sources
    
    def create_response_metadata(
        self,
        query: str,
        chunks: List[KnowledgeChunk],
    ) -> Dict[str, Any]:
        """
        Create metadata about Groww page mapping for response.
        
        Args:
            query: User's question
            chunks: Retrieved knowledge chunks
            
        Returns:
            Metadata dictionary
        """
        availability = self.check_groww_availability(query, chunks)
        category = self._identify_query_category(query)
        
        return {
            "query_category": category,
            "groww_availability": availability,
            "amc_identified": self._extract_amc_from_query(query),
            "fund_identified": self._extract_fund_from_chunks(chunks),
        }


# Singleton instance
_groww_mapper_instance: Optional[GrówwPageMapper] = None


def get_groww_mapper() -> GrówwPageMapper:
    """
    Get or create the singleton GrowwPageMapper instance.
    
    Returns:
        GrowwPageMapper instance
    """
    global _groww_mapper_instance
    
    if _groww_mapper_instance is None:
        _groww_mapper_instance = GrówwPageMapper()
    
    return _groww_mapper_instance

