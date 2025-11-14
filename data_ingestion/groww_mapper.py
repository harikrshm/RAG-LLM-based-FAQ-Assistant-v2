"""
Groww Website Mapping Module

This module identifies and maps information to Groww website pages, implementing
the fallback logic where Groww pages are prioritized over external AMC/SEBI/AMFI pages.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrowwMapper:
    """
    Maps content and queries to Groww website pages.
    """

    def __init__(self):
        """Initialize the Groww mapper."""
        self.groww_domain = "groww.in"
        self.groww_base_url = "https://groww.in"

        # Define information categories and their Groww page patterns
        self.info_categories = {
            "fund_details": {
                "keywords": ["fund", "scheme", "details", "overview"],
                "url_pattern": "/mutual-funds/{fund_slug}",
            },
            "amc_page": {
                "keywords": ["amc", "asset management", "company"],
                "url_pattern": "/mutual-funds/amc/{amc_slug}",
            },
            "expense_ratio": {
                "keywords": ["expense ratio", "fees", "charges"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#expense-ratio",
            },
            "exit_load": {
                "keywords": ["exit load", "redemption", "exit fee"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#exit-load",
            },
            "minimum_sip": {
                "keywords": ["minimum sip", "sip amount", "minimum investment"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#investment-details",
            },
            "returns": {
                "keywords": ["returns", "performance", "cagr"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#returns",
            },
            "nav": {
                "keywords": ["nav", "net asset value", "unit price"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#nav",
            },
            "portfolio": {
                "keywords": ["portfolio", "holdings", "assets"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/{fund_slug}",
                "section": "#portfolio",
            },
            "download_statement": {
                "keywords": ["download statement", "statement", "account statement"],
                "groww_available": True,
                "url_pattern": "/mutual-funds/user/statements",
            },
            "tax_treatment": {
                "keywords": ["tax", "taxation", "capital gains"],
                "groww_available": False,
                "external_required": True,
            },
            "scheme_document": {
                "keywords": ["scheme document", "sid", "scheme information"],
                "groww_available": False,
                "external_required": True,
            },
        }

        # AMC name to slug mapping
        self.amc_slug_mapping = {
            "SBI Mutual Fund": "sbi-mutual-funds",
            "HDFC Mutual Fund": "hdfc-mutual-funds",
            "ICICI Prudential Mutual Fund": "icici-prudential-mutual-funds",
            "Axis Mutual Fund": "axis-mutual-funds",
            "Nippon India Mutual Fund": "nippon-india-mutual-funds",
        }

        # Cache for fund slugs
        self.fund_slug_cache = {}

    def identify_info_category(self, query: str) -> Optional[str]:
        """
        Identify the information category from a query.

        Args:
            query: User query or content text

        Returns:
            Information category or None
        """
        query_lower = query.lower()

        # Check each category
        for category, config in self.info_categories.items():
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword in query_lower:
                    logger.debug(f"Identified category: {category}")
                    return category

        return None

    def is_groww_url(self, url: str) -> bool:
        """
        Check if a URL is from Groww website.

        Args:
            url: URL to check

        Returns:
            True if URL is from Groww, False otherwise
        """
        try:
            parsed = urlparse(url)
            return self.groww_domain in parsed.netloc
        except Exception:
            return False

    def extract_fund_slug_from_url(self, url: str) -> Optional[str]:
        """
        Extract fund slug from a Groww URL.

        Args:
            url: Groww URL

        Returns:
            Fund slug or None
        """
        if not self.is_groww_url(url):
            return None

        # Pattern: /mutual-funds/{fund-slug}
        pattern = r"/mutual-funds/([a-z0-9\-]+)"
        match = re.search(pattern, url)

        if match:
            slug = match.group(1)
            # Filter out special pages
            if slug not in ["amc", "top", "user"]:
                return slug

        return None

    def extract_amc_slug_from_url(self, url: str) -> Optional[str]:
        """
        Extract AMC slug from a Groww URL.

        Args:
            url: Groww URL

        Returns:
            AMC slug or None
        """
        if not self.is_groww_url(url):
            return None

        # Pattern: /mutual-funds/amc/{amc-slug}
        pattern = r"/mutual-funds/amc/([a-z0-9\-]+)"
        match = re.search(pattern, url)

        if match:
            return match.group(1)

        return None

    def get_amc_slug(self, amc_name: str) -> Optional[str]:
        """
        Get AMC slug from AMC name.

        Args:
            amc_name: AMC name

        Returns:
            AMC slug or None
        """
        return self.amc_slug_mapping.get(amc_name)

    def build_groww_url(
        self, category: str, fund_slug: Optional[str] = None, amc_slug: Optional[str] = None
    ) -> Optional[str]:
        """
        Build a Groww URL for a specific information category.

        Args:
            category: Information category
            fund_slug: Fund slug
            amc_slug: AMC slug

        Returns:
            Groww URL or None
        """
        if category not in self.info_categories:
            return None

        config = self.info_categories[category]

        if not config.get("groww_available", True):
            return None

        url_pattern = config.get("url_pattern", "")
        section = config.get("section", "")

        # Replace placeholders
        url = url_pattern.replace("{fund_slug}", fund_slug or "")
        url = url.replace("{amc_slug}", amc_slug or "")

        # Build full URL
        full_url = self.groww_base_url + url + section

        return full_url

    def map_chunk_to_groww(self, chunk: Dict) -> Optional[str]:
        """
        Map a chunk to a Groww page URL.

        Args:
            chunk: Chunk dictionary with content and metadata

        Returns:
            Groww page URL or None
        """
        source_url = chunk.get("source_url", "")

        # If chunk is already from Groww, return the source URL
        if self.is_groww_url(source_url):
            return source_url

        # Try to identify the information category from content
        content = chunk.get("content", "")
        category = self.identify_info_category(content)

        if not category:
            return None

        # Check if this information is available on Groww
        if not self.info_categories[category].get("groww_available", True):
            return None

        # Extract fund/AMC information
        metadata = chunk.get("metadata", {})
        amc_name = metadata.get("amc_name")
        amc_slug = self.get_amc_slug(amc_name) if amc_name else None

        # Try to extract fund slug from source URL if it's a Groww URL
        fund_slug = self.extract_fund_slug_from_url(source_url)

        # Build Groww URL
        if fund_slug:
            groww_url = self.build_groww_url(category, fund_slug=fund_slug)
        elif amc_slug:
            groww_url = self.build_groww_url(category, amc_slug=amc_slug)
        else:
            groww_url = None

        return groww_url

    def determine_source_priority(
        self, query: str, chunk: Dict, groww_url: Optional[str]
    ) -> Tuple[str, str]:
        """
        Determine which source URL to prioritize (Groww vs external).

        Args:
            query: User query
            chunk: Chunk dictionary
            groww_url: Mapped Groww URL

        Returns:
            Tuple of (primary_url, secondary_url)
        """
        source_url = chunk.get("source_url", "")
        category = self.identify_info_category(query)

        # If information is not available on Groww, use external source
        if category and not self.info_categories[category].get("groww_available", True):
            return (source_url, None)

        # If we have a Groww URL, prioritize it
        if groww_url:
            return (groww_url, source_url)

        # Otherwise use the source URL
        return (source_url, None)

    def get_fallback_message(self, category: Optional[str], primary_url: str) -> str:
        """
        Get appropriate fallback message based on category and URL.

        Args:
            category: Information category
            primary_url: Primary source URL

        Returns:
            Fallback message
        """
        if self.is_groww_url(primary_url):
            return f"You can find this information on Groww: {primary_url}"
        else:
            return f"This information is available on the official source: {primary_url}"

    def process_chunks_with_mapping(self, chunks: List[Dict]) -> List[Dict]:
        """
        Process chunks and add Groww page mappings.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of chunks with groww_page_url field added
        """
        logger.info(f"Processing {len(chunks)} chunks for Groww mapping")

        processed_chunks = []

        for i, chunk in enumerate(chunks):
            try:
                # Map to Groww page
                groww_url = self.map_chunk_to_groww(chunk)

                # Add groww_page_url to chunk
                chunk["groww_page_url"] = groww_url

                processed_chunks.append(chunk)

                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(chunks)} chunks")

            except Exception as e:
                logger.error(f"Error processing chunk {i}: {e}")
                chunk["groww_page_url"] = None
                processed_chunks.append(chunk)

        # Count successful mappings
        mapped_count = sum(1 for c in processed_chunks if c.get("groww_page_url"))
        logger.info(f"Successfully mapped {mapped_count}/{len(processed_chunks)} chunks to Groww pages")

        return processed_chunks

    def get_mapping_statistics(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about Groww page mappings.

        Args:
            chunks: List of chunks with groww_page_url field

        Returns:
            Statistics dictionary
        """
        total_chunks = len(chunks)
        chunks_with_groww_url = sum(1 for c in chunks if c.get("groww_page_url"))
        chunks_from_groww_source = sum(
            1 for c in chunks if self.is_groww_url(c.get("source_url", ""))
        )

        # Count by category
        category_counts = {}
        for chunk in chunks:
            content = chunk.get("content", "")
            category = self.identify_info_category(content)
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_chunks": total_chunks,
            "chunks_with_groww_url": chunks_with_groww_url,
            "chunks_from_groww_source": chunks_from_groww_source,
            "mapping_rate": (
                chunks_with_groww_url / total_chunks * 100 if total_chunks > 0 else 0
            ),
            "category_distribution": category_counts,
        }


def main():
    """Main function for testing Groww mapper."""
    import json

    # Initialize mapper
    mapper = GrowwMapper()

    # Load chunks
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        logger.error("Chunks file not found")
        return

    # Process chunks with Groww mapping
    processed_chunks = mapper.process_chunks_with_mapping(chunks)

    # Save chunks with mappings
    output_data = {
        "chunks": processed_chunks,
        "metadata": data.get("metadata", {}),
    }

    with open("data/chunks_with_mappings.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info("Saved chunks with Groww mappings")

    # Print statistics
    stats = mapper.get_mapping_statistics(processed_chunks)
    print("\nGroww Mapping Statistics:")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Chunks with Groww URL: {stats['chunks_with_groww_url']}")
    print(f"Chunks from Groww source: {stats['chunks_from_groww_source']}")
    print(f"Mapping rate: {stats['mapping_rate']:.2f}%")

    print("\nCategory distribution:")
    for category, count in sorted(
        stats["category_distribution"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {category}: {count}")

    # Show sample mappings
    print("\nSample Groww mappings:")
    mapped_chunks = [c for c in processed_chunks if c.get("groww_page_url")][:5]
    for i, chunk in enumerate(mapped_chunks):
        print(f"\n{i+1}.")
        print(f"  Source: {chunk.get('source_url', 'Unknown')[:60]}...")
        print(f"  Groww URL: {chunk.get('groww_page_url', 'None')}")
        print(f"  Content: {chunk.get('content', '')[:80]}...")


if __name__ == "__main__":
    main()

