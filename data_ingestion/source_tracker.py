"""
Source URL Tracking System

This module tracks and validates source URLs, maintaining mappings between
content chunks and their source URLs for citation generation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceURLTracker:
    """
    Tracks source URLs and maintains mappings between content and sources.
    """

    def __init__(self, storage_file: str = "data/source_tracking.json"):
        """
        Initialize the source tracker.

        Args:
            storage_file: Path to JSON file for storing source tracking data
        """
        self.storage_file = Path(storage_file)
        self.sources: Dict[str, Dict] = {}
        self.url_to_id: Dict[str, str] = {}
        self.content_to_sources: Dict[str, List[str]] = {}
        
        # Load existing data if available
        self._load_tracking_data()

    def _load_tracking_data(self):
        """Load existing tracking data from file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.sources = data.get("sources", {})
                self.url_to_id = data.get("url_to_id", {})
                self.content_to_sources = data.get("content_to_sources", {})
                
                logger.info(f"Loaded {len(self.sources)} tracked sources")
            except Exception as e:
                logger.error(f"Error loading tracking data: {e}")
        else:
            logger.info("No existing tracking data found, starting fresh")

    def add_source(
        self,
        url: str,
        amc_name: str,
        title: Optional[str] = None,
        source_type: str = "groww",
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Add a source URL to the tracking system.

        Args:
            url: Source URL
            amc_name: AMC name
            title: Page title
            source_type: Type of source (groww, amc, sebi, amfi)
            metadata: Additional metadata

        Returns:
            Source ID
        """
        # Generate source ID
        source_id = self._generate_source_id(url)

        # Check if source already exists
        if source_id in self.sources:
            logger.debug(f"Source already tracked: {url}")
            return source_id

        # Add source
        self.sources[source_id] = {
            "url": url,
            "amc_name": amc_name,
            "title": title or url,
            "source_type": source_type,
            "domain": urlparse(url).netloc,
            "added_at": datetime.now().isoformat(),
            "validated": False,
            "validation_date": None,
            "is_accessible": None,
            "metadata": metadata or {},
        }

        self.url_to_id[url] = source_id
        logger.info(f"Added source: {url} -> {source_id}")

        return source_id

    def _generate_source_id(self, url: str) -> str:
        """
        Generate a unique source ID from URL.

        Args:
            url: Source URL

        Returns:
            Source ID
        """
        # Use URL path as basis for ID
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").replace("/", "_")
        
        # Create a clean ID
        source_id = f"{parsed.netloc}_{path_parts}".replace(".", "_").replace("-", "_")
        
        # Ensure uniqueness by appending counter if needed
        base_id = source_id
        counter = 1
        while source_id in self.sources and self.sources[source_id]["url"] != url:
            source_id = f"{base_id}_{counter}"
            counter += 1

        return source_id

    def link_content_to_source(self, content_id: str, source_url: str):
        """
        Link a content chunk to its source URL.

        Args:
            content_id: Unique content chunk ID
            source_url: Source URL
        """
        source_id = self.url_to_id.get(source_url)
        
        if not source_id:
            logger.warning(f"Source URL not tracked: {source_url}")
            return

        if content_id not in self.content_to_sources:
            self.content_to_sources[content_id] = []

        if source_id not in self.content_to_sources[content_id]:
            self.content_to_sources[content_id].append(source_id)
            logger.debug(f"Linked content {content_id} to source {source_id}")

    def get_source_by_id(self, source_id: str) -> Optional[Dict]:
        """
        Get source information by ID.

        Args:
            source_id: Source ID

        Returns:
            Source information dictionary or None
        """
        return self.sources.get(source_id)

    def get_source_by_url(self, url: str) -> Optional[Dict]:
        """
        Get source information by URL.

        Args:
            url: Source URL

        Returns:
            Source information dictionary or None
        """
        source_id = self.url_to_id.get(url)
        if source_id:
            return self.sources.get(source_id)
        return None

    def get_sources_for_content(self, content_id: str) -> List[Dict]:
        """
        Get all source information for a content chunk.

        Args:
            content_id: Content chunk ID

        Returns:
            List of source information dictionaries
        """
        source_ids = self.content_to_sources.get(content_id, [])
        return [self.sources[sid] for sid in source_ids if sid in self.sources]

    def validate_source(self, source_id: str, timeout: int = 10) -> bool:
        """
        Validate that a source URL is accessible.

        Args:
            source_id: Source ID
            timeout: Request timeout in seconds

        Returns:
            True if accessible, False otherwise
        """
        source = self.sources.get(source_id)
        if not source:
            logger.warning(f"Source not found: {source_id}")
            return False

        url = source["url"]
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            is_accessible = response.status_code == 200
            
            # Update source
            self.sources[source_id]["validated"] = True
            self.sources[source_id]["validation_date"] = datetime.now().isoformat()
            self.sources[source_id]["is_accessible"] = is_accessible
            
            logger.info(f"Validated {url}: {'accessible' if is_accessible else 'not accessible'}")
            return is_accessible

        except Exception as e:
            logger.warning(f"Validation failed for {url}: {e}")
            self.sources[source_id]["validated"] = True
            self.sources[source_id]["validation_date"] = datetime.now().isoformat()
            self.sources[source_id]["is_accessible"] = False
            return False

    def validate_all_sources(self, timeout: int = 10) -> Dict[str, int]:
        """
        Validate all tracked sources.

        Args:
            timeout: Request timeout in seconds

        Returns:
            Dictionary with validation statistics
        """
        logger.info(f"Validating {len(self.sources)} sources...")
        
        stats = {
            "total": len(self.sources),
            "accessible": 0,
            "inaccessible": 0,
            "failed": 0,
        }

        for source_id in self.sources.keys():
            is_accessible = self.validate_source(source_id, timeout)
            if is_accessible:
                stats["accessible"] += 1
            else:
                stats["inaccessible"] += 1

        logger.info(f"Validation complete: {stats}")
        return stats

    def get_all_sources(self, source_type: Optional[str] = None) -> List[Dict]:
        """
        Get all tracked sources, optionally filtered by type.

        Args:
            source_type: Filter by source type (groww, amc, sebi, amfi)

        Returns:
            List of source information dictionaries
        """
        if source_type:
            return [s for s in self.sources.values() if s["source_type"] == source_type]
        return list(self.sources.values())

    def get_sources_by_amc(self, amc_name: str) -> List[Dict]:
        """
        Get all sources for a specific AMC.

        Args:
            amc_name: AMC name

        Returns:
            List of source information dictionaries
        """
        return [s for s in self.sources.values() if s["amc_name"] == amc_name]

    def save_tracking_data(self):
        """Save tracking data to file."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sources": self.sources,
            "url_to_id": self.url_to_id,
            "content_to_sources": self.content_to_sources,
            "metadata": {
                "total_sources": len(self.sources),
                "total_content_links": len(self.content_to_sources),
                "last_updated": datetime.now().isoformat(),
            },
        }

        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved tracking data to {self.storage_file}")

    def get_statistics(self) -> Dict:
        """
        Get statistics about tracked sources.

        Returns:
            Dictionary with statistics
        """
        validated_count = sum(1 for s in self.sources.values() if s["validated"])
        accessible_count = sum(1 for s in self.sources.values() if s.get("is_accessible"))
        
        source_types = {}
        for source in self.sources.values():
            stype = source["source_type"]
            source_types[stype] = source_types.get(stype, 0) + 1

        return {
            "total_sources": len(self.sources),
            "validated_sources": validated_count,
            "accessible_sources": accessible_count,
            "total_content_links": len(self.content_to_sources),
            "sources_by_type": source_types,
            "unique_amcs": len(set(s["amc_name"] for s in self.sources.values())),
        }


def main():
    """Main function for testing source tracker."""
    # Initialize tracker
    tracker = SourceURLTracker()

    # Load source URLs
    with open("data/source_urls.json", "r") as f:
        source_data = json.load(f)

    # Add all sources
    for amc in source_data["amcs"]:
        for url in amc["urls"]:
            tracker.add_source(
                url=url,
                amc_name=amc["name"],
                source_type="groww",
                metadata={"amc_id": amc["amc_id"]},
            )

    # Validate sources
    print("\nValidating sources...")
    stats = tracker.validate_all_sources()
    print(f"Validation complete: {stats}")

    # Get statistics
    print("\nTracker Statistics:")
    for key, value in tracker.get_statistics().items():
        print(f"  {key}: {value}")

    # Save tracking data
    tracker.save_tracking_data()


if __name__ == "__main__":
    main()

