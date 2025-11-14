"""
Metadata Manager Module

This module manages metadata schemas and storage for linking chunks to source
URLs, content types, and other relevant information.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration."""

    AMC_PAGE = "amc_page"
    FUND_PAGE = "fund_page"
    SCHEME_PAGE = "scheme_page"
    BLOG_POST = "blog_post"
    COMPARISON_PAGE = "comparison_page"
    UNKNOWN = "unknown"


@dataclass
class SourceMetadata:
    """Metadata for a source document."""

    source_url: str
    content_type: str
    amc_name: Optional[str] = None
    amc_id: Optional[str] = None
    title: Optional[str] = None
    scraped_at: Optional[str] = None
    last_updated: Optional[str] = None
    domain: Optional[str] = None
    page_type: Optional[str] = None


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""

    chunk_id: str
    source_url: str
    chunk_index: int
    content_type: str
    amc_name: Optional[str] = None
    amc_id: Optional[str] = None
    title: Optional[str] = None
    content_length: int = 0
    has_structured_info: bool = False
    structured_info: Optional[Dict] = None
    groww_page_url: Optional[str] = None
    created_at: Optional[str] = None


class MetadataManager:
    """
    Manages metadata schemas and linking between chunks and sources.
    """

    def __init__(self, metadata_file: str = "data/metadata_index.json"):
        """
        Initialize the metadata manager.

        Args:
            metadata_file: Path to store metadata index
        """
        self.metadata_file = metadata_file
        self.source_registry = {}  # URL -> SourceMetadata
        self.chunk_registry = {}  # chunk_id -> ChunkMetadata
        self.url_to_chunks = {}  # URL -> [chunk_ids]
        self.amc_to_chunks = {}  # AMC name -> [chunk_ids]

        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from file if it exists."""
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.source_registry = data.get("sources", {})
                self.chunk_registry = data.get("chunks", {})
                self.url_to_chunks = data.get("url_to_chunks", {})
                self.amc_to_chunks = data.get("amc_to_chunks", {})
            logger.info(f"Loaded metadata from {self.metadata_file}")
        except FileNotFoundError:
            logger.info("No existing metadata file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")

    def save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            data = {
                "sources": self.source_registry,
                "chunks": self.chunk_registry,
                "url_to_chunks": self.url_to_chunks,
                "amc_to_chunks": self.amc_to_chunks,
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved metadata to {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise

    def register_source(self, source_metadata: Dict) -> None:
        """
        Register a source document.

        Args:
            source_metadata: Source metadata dictionary
        """
        url = source_metadata.get("url")
        if not url:
            logger.warning("Source metadata missing URL, skipping")
            return

        # Determine content type
        content_type = self._determine_content_type(url, source_metadata)

        # Extract domain
        domain = self._extract_domain(url)

        # Create source metadata
        source = {
            "source_url": url,
            "content_type": content_type,
            "amc_name": source_metadata.get("amc_name"),
            "amc_id": source_metadata.get("amc_id"),
            "title": source_metadata.get("title"),
            "scraped_at": source_metadata.get("scraped_at", datetime.now().isoformat()),
            "domain": domain,
            "page_type": source_metadata.get("page_type"),
        }

        self.source_registry[url] = source
        logger.debug(f"Registered source: {url}")

    def register_chunk(self, chunk: Dict) -> None:
        """
        Register a chunk with its metadata.

        Args:
            chunk: Chunk dictionary
        """
        chunk_id = chunk.get("chunk_id")
        if not chunk_id:
            logger.warning("Chunk missing chunk_id, skipping")
            return

        source_url = chunk.get("source_url", "")
        chunk_metadata = chunk.get("metadata", {})
        structured_info = chunk_metadata.get("structured_info", {})

        # Create chunk metadata
        metadata = {
            "chunk_id": chunk_id,
            "source_url": source_url,
            "chunk_index": chunk.get("chunk_index", 0),
            "content_type": self._determine_content_type(source_url, chunk_metadata),
            "amc_name": chunk_metadata.get("amc_name"),
            "amc_id": chunk_metadata.get("amc_id"),
            "title": chunk_metadata.get("title"),
            "content_length": len(chunk.get("content", "")),
            "has_structured_info": bool(structured_info),
            "structured_info": structured_info if structured_info else None,
            "created_at": datetime.now().isoformat(),
        }

        # Register chunk
        self.chunk_registry[chunk_id] = metadata

        # Update URL to chunks mapping
        if source_url:
            if source_url not in self.url_to_chunks:
                self.url_to_chunks[source_url] = []
            if chunk_id not in self.url_to_chunks[source_url]:
                self.url_to_chunks[source_url].append(chunk_id)

        # Update AMC to chunks mapping
        amc_name = chunk_metadata.get("amc_name")
        if amc_name:
            if amc_name not in self.amc_to_chunks:
                self.amc_to_chunks[amc_name] = []
            if chunk_id not in self.amc_to_chunks[amc_name]:
                self.amc_to_chunks[amc_name].append(chunk_id)

        logger.debug(f"Registered chunk: {chunk_id}")

    def register_groww_mapping(self, chunk_id: str, groww_url: str) -> None:
        """
        Register a mapping between a chunk and a Groww website page.

        Args:
            chunk_id: Chunk ID
            groww_url: Groww website URL
        """
        if chunk_id in self.chunk_registry:
            self.chunk_registry[chunk_id]["groww_page_url"] = groww_url
            logger.debug(f"Registered Groww mapping for chunk {chunk_id}")
        else:
            logger.warning(f"Chunk {chunk_id} not found in registry")

    def get_source_metadata(self, url: str) -> Optional[Dict]:
        """
        Get metadata for a source URL.

        Args:
            url: Source URL

        Returns:
            Source metadata or None
        """
        return self.source_registry.get(url)

    def get_chunk_metadata(self, chunk_id: str) -> Optional[Dict]:
        """
        Get metadata for a chunk.

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk metadata or None
        """
        return self.chunk_registry.get(chunk_id)

    def get_chunks_by_url(self, url: str) -> List[str]:
        """
        Get all chunk IDs for a source URL.

        Args:
            url: Source URL

        Returns:
            List of chunk IDs
        """
        return self.url_to_chunks.get(url, [])

    def get_chunks_by_amc(self, amc_name: str) -> List[str]:
        """
        Get all chunk IDs for an AMC.

        Args:
            amc_name: AMC name

        Returns:
            List of chunk IDs
        """
        return self.amc_to_chunks.get(amc_name, [])

    def get_all_sources(self) -> List[Dict]:
        """
        Get all registered sources.

        Returns:
            List of source metadata dictionaries
        """
        return list(self.source_registry.values())

    def get_all_chunks(self) -> List[Dict]:
        """
        Get all registered chunks.

        Returns:
            List of chunk metadata dictionaries
        """
        return list(self.chunk_registry.values())

    def get_statistics(self) -> Dict:
        """
        Get statistics about registered metadata.

        Returns:
            Statistics dictionary
        """
        total_sources = len(self.source_registry)
        total_chunks = len(self.chunk_registry)
        total_amcs = len(self.amc_to_chunks)

        chunks_with_structured_info = sum(
            1 for chunk in self.chunk_registry.values() if chunk.get("has_structured_info")
        )

        chunks_with_groww_mapping = sum(
            1 for chunk in self.chunk_registry.values() if chunk.get("groww_page_url")
        )

        return {
            "total_sources": total_sources,
            "total_chunks": total_chunks,
            "total_amcs": total_amcs,
            "chunks_with_structured_info": chunks_with_structured_info,
            "chunks_with_groww_mapping": chunks_with_groww_mapping,
            "avg_chunks_per_source": total_chunks / total_sources if total_sources > 0 else 0,
        }

    def _determine_content_type(self, url: str, metadata: Dict) -> str:
        """
        Determine content type from URL and metadata.

        Args:
            url: Source URL
            metadata: Metadata dictionary

        Returns:
            Content type string
        """
        url_lower = url.lower()

        if "/amc/" in url_lower:
            return ContentType.AMC_PAGE.value
        elif "/mutual-funds/" in url_lower:
            if "/top/" in url_lower or "/best-" in url_lower:
                return ContentType.COMPARISON_PAGE.value
            else:
                return ContentType.FUND_PAGE.value
        elif "/blog/" in url_lower:
            return ContentType.BLOG_POST.value
        else:
            return ContentType.UNKNOWN.value

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: Source URL

        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"

    def validate_metadata(self) -> Dict:
        """
        Validate metadata integrity.

        Returns:
            Validation results dictionary
        """
        issues = []

        # Check for orphaned chunks (chunks without valid source)
        for chunk_id, chunk_meta in self.chunk_registry.items():
            source_url = chunk_meta.get("source_url")
            if source_url and source_url not in self.source_registry:
                issues.append(
                    {
                        "type": "orphaned_chunk",
                        "chunk_id": chunk_id,
                        "source_url": source_url,
                    }
                )

        # Check for missing URL mappings
        for chunk_id, chunk_meta in self.chunk_registry.items():
            source_url = chunk_meta.get("source_url")
            if source_url and chunk_id not in self.url_to_chunks.get(source_url, []):
                issues.append(
                    {
                        "type": "missing_url_mapping",
                        "chunk_id": chunk_id,
                        "source_url": source_url,
                    }
                )

        # Check for missing AMC mappings
        for chunk_id, chunk_meta in self.chunk_registry.items():
            amc_name = chunk_meta.get("amc_name")
            if amc_name and chunk_id not in self.amc_to_chunks.get(amc_name, []):
                issues.append(
                    {
                        "type": "missing_amc_mapping",
                        "chunk_id": chunk_id,
                        "amc_name": amc_name,
                    }
                )

        return {
            "valid": len(issues) == 0,
            "total_issues": len(issues),
            "issues": issues,
        }


def main():
    """Main function for testing metadata manager."""
    import json

    # Initialize metadata manager
    manager = MetadataManager(metadata_file="data/metadata_index.json")

    # Load chunks with embeddings
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        logger.error("Chunks file not found")
        return

    # Register sources and chunks
    processed_urls = set()

    for chunk in chunks:
        # Register source if not already done
        source_url = chunk.get("source_url")
        if source_url and source_url not in processed_urls:
            source_metadata = {
                "url": source_url,
                "amc_name": chunk.get("metadata", {}).get("amc_name"),
                "amc_id": chunk.get("metadata", {}).get("amc_id"),
                "title": chunk.get("metadata", {}).get("title"),
            }
            manager.register_source(source_metadata)
            processed_urls.add(source_url)

        # Register chunk
        manager.register_chunk(chunk)

    # Save metadata
    manager.save_metadata()

    # Print statistics
    stats = manager.get_statistics()
    print("\nMetadata Statistics:")
    print(f"Total sources: {stats['total_sources']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total AMCs: {stats['total_amcs']}")
    print(f"Chunks with structured info: {stats['chunks_with_structured_info']}")
    print(f"Chunks with Groww mapping: {stats['chunks_with_groww_mapping']}")
    print(f"Avg chunks per source: {stats['avg_chunks_per_source']:.2f}")

    # Validate metadata
    validation = manager.validate_metadata()
    print(f"\nMetadata validation: {'PASSED' if validation['valid'] else 'FAILED'}")
    if not validation["valid"]:
        print(f"Issues found: {validation['total_issues']}")


if __name__ == "__main__":
    main()

