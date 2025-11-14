"""
Citation Utilities

Utilities for formatting source links and citations.
"""

import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Citation:
    """Represents a single citation/source."""
    
    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        amc_name: Optional[str] = None,
        content_type: Optional[str] = None,
        index: int = 1,
    ):
        self.url = url
        self.title = title or self._extract_title_from_url(url)
        self.amc_name = amc_name
        self.content_type = content_type
        self.index = index
        self.is_groww = self._is_groww_url(url)
    
    def _is_groww_url(self, url: str) -> bool:
        """Check if URL is from Groww."""
        return "groww.in" in url.lower()
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a readable title from URL."""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            
            # Get the last meaningful part of the path
            parts = path.split("/")
            if parts:
                # Convert kebab-case or snake_case to Title Case
                last_part = parts[-1].replace("-", " ").replace("_", " ")
                return last_part.title()
            
            return parsed.netloc
        except Exception:
            return "Source"
    
    def to_inline(self) -> str:
        """Format as inline citation [N]."""
        return f"[{self.index}]"
    
    def to_markdown_link(self) -> str:
        """Format as markdown link."""
        return f"[{self.title}]({self.url})"
    
    def to_formatted_source(self) -> str:
        """Format as a complete source entry."""
        if self.amc_name:
            return f"[{self.index}] {self.title} - {self.amc_name} ({self.url})"
        return f"[{self.index}] {self.title} ({self.url})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "url": self.url,
            "title": self.title,
            "amc_name": self.amc_name,
            "content_type": self.content_type,
            "is_groww": self.is_groww,
        }


class CitationFormatter:
    """
    Formats citations and source links for responses.
    
    Handles both inline citations and sources section formatting.
    """
    
    def __init__(self):
        """Initialize citation formatter."""
        logger.info("CitationFormatter initialized")
    
    def create_citations(
        self,
        sources: List[Dict[str, Any]],
        prioritize_groww: bool = True,
    ) -> List[Citation]:
        """
        Create Citation objects from source dictionaries.
        
        Args:
            sources: List of source dictionaries
            prioritize_groww: If True, put Groww sources first
            
        Returns:
            List of Citation objects with assigned indices
        """
        citations = []
        
        # Convert to Citation objects
        for source in sources:
            citation = Citation(
                url=source.get("url", ""),
                title=source.get("title"),
                amc_name=source.get("amc_name"),
                content_type=source.get("content_type"),
            )
            citations.append(citation)
        
        # Sort: Groww sources first if prioritizing
        if prioritize_groww:
            citations.sort(key=lambda c: (not c.is_groww, c.url))
        
        # Assign indices
        for i, citation in enumerate(citations, 1):
            citation.index = i
        
        return citations
    
    def format_inline_citations(
        self,
        response_text: str,
        citations: List[Citation],
    ) -> str:
        """
        Add inline citations to response text.
        
        This looks for [Source N] patterns in the text and replaces them
        with proper citation markers.
        
        Args:
            response_text: Response text with [Source N] markers
            citations: List of Citation objects
            
        Returns:
            Response text with formatted inline citations
        """
        formatted_text = response_text
        
        # Replace [Source N] with [N]
        for citation in citations:
            source_marker = f"[Source {citation.index}]"
            inline_citation = citation.to_inline()
            formatted_text = formatted_text.replace(source_marker, inline_citation)
        
        return formatted_text
    
    def format_sources_section(
        self,
        citations: List[Citation],
        format_type: str = "plain",
    ) -> str:
        """
        Format a sources section listing all citations.
        
        Args:
            citations: List of Citation objects
            format_type: Format type - "plain", "markdown", or "html"
            
        Returns:
            Formatted sources section text
        """
        if not citations:
            return ""
        
        if format_type == "markdown":
            lines = ["## Sources"]
            for citation in citations:
                lines.append(f"{citation.index}. {citation.to_markdown_link()}")
                if citation.amc_name:
                    lines.append(f"   *{citation.amc_name}*")
        
        elif format_type == "html":
            lines = ["<div class='sources-section'>", "<h3>Sources</h3>", "<ol>"]
            for citation in citations:
                lines.append(
                    f"<li><a href='{citation.url}' target='_blank' rel='noopener'>{citation.title}</a>"
                )
                if citation.amc_name:
                    lines.append(f"<span class='amc-name'>{citation.amc_name}</span>")
                lines.append("</li>")
            lines.append("</ol>")
            lines.append("</div>")
        
        else:  # plain text
            lines = ["Sources:"]
            for citation in citations:
                lines.append(citation.to_formatted_source())
        
        return "\n".join(lines)
    
    def format_response_with_citations(
        self,
        response_text: str,
        sources: List[Dict[str, Any]],
        include_sources_section: bool = True,
        format_type: str = "plain",
    ) -> Dict[str, Any]:
        """
        Format a complete response with inline citations and sources section.
        
        Args:
            response_text: Raw response text with [Source N] markers
            sources: List of source dictionaries
            include_sources_section: Whether to append sources section
            format_type: Format type for sources section
            
        Returns:
            Dictionary with formatted response and citation info
        """
        # Create citations
        citations = self.create_citations(sources, prioritize_groww=True)
        
        # Format inline citations
        formatted_response = self.format_inline_citations(response_text, citations)
        
        # Format sources section
        sources_section = ""
        if include_sources_section and citations:
            sources_section = self.format_sources_section(citations, format_type)
        
        # Combine if sources section exists
        if sources_section:
            full_response = f"{formatted_response}\n\n{sources_section}"
        else:
            full_response = formatted_response
        
        return {
            "formatted_response": full_response,
            "response_text": formatted_response,
            "sources_section": sources_section,
            "citations": [c.to_dict() for c in citations],
            "citation_count": len(citations),
        }
    
    def extract_groww_priority_url(
        self,
        sources: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Extract the primary Groww URL from sources (if available).
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Primary Groww URL or None
        """
        for source in sources:
            url = source.get("url", "")
            if "groww.in" in url.lower():
                return url
        return None
    
    def deduplicate_sources(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate sources based on URL.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Deduplicated list of sources
        """
        seen_urls = set()
        deduplicated = []
        
        for source in sources:
            url = source.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(source)
        
        return deduplicated
    
    def validate_sources(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Validate sources and return list of issues.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for i, source in enumerate(sources):
            # Check for URL
            if not source.get("url"):
                errors.append(f"Source {i+1} missing URL")
                continue
            
            # Validate URL format
            url = source["url"]
            if not url.startswith(("http://", "https://")):
                errors.append(f"Source {i+1} has invalid URL format: {url}")
            
            # Check for title (optional but recommended)
            if not source.get("title"):
                logger.debug(f"Source {i+1} missing title: {url}")
        
        return errors
    
    def create_citation_metadata(
        self,
        sources: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create metadata about citations for analytics/monitoring.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Citation metadata dictionary
        """
        citations = self.create_citations(sources)
        
        groww_count = sum(1 for c in citations if c.is_groww)
        external_count = len(citations) - groww_count
        
        # Count by AMC
        amc_counts = {}
        for citation in citations:
            if citation.amc_name:
                amc_counts[citation.amc_name] = amc_counts.get(citation.amc_name, 0) + 1
        
        # Count by content type
        content_type_counts = {}
        for citation in citations:
            if citation.content_type:
                content_type_counts[citation.content_type] = (
                    content_type_counts.get(citation.content_type, 0) + 1
                )
        
        return {
            "total_citations": len(citations),
            "groww_citations": groww_count,
            "external_citations": external_count,
            "amc_distribution": amc_counts,
            "content_type_distribution": content_type_counts,
            "has_groww_source": groww_count > 0,
        }


# Singleton instance
_citation_formatter_instance: Optional[CitationFormatter] = None


def get_citation_formatter() -> CitationFormatter:
    """
    Get or create the singleton CitationFormatter instance.
    
    Returns:
        CitationFormatter instance
    """
    global _citation_formatter_instance
    
    if _citation_formatter_instance is None:
        _citation_formatter_instance = CitationFormatter()
    
    return _citation_formatter_instance

