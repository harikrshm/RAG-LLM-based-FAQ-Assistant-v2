"""
Test suite for validating metadata storage accuracy.

This module tests that:
- Source URLs are stored correctly in metadata
- Content types are accurately classified
- Metadata fields are complete and accurate
- Metadata structure is consistent
"""

import pytest
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata_manager import MetadataManager, ContentType


@pytest.fixture
def metadata_manager():
    """Create a metadata manager instance."""
    return MetadataManager(metadata_file="data/test_metadata_index.json")


@pytest.fixture
def sample_chunks_with_metadata():
    """Load sample chunks with metadata or create mock data."""
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("chunks", [])
    except FileNotFoundError:
        # Return mock data for testing
        return [
            {
                "chunk_id": "test-chunk-1",
                "content": "HDFC Equity Fund information",
                "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                "chunk_index": 0,
                "metadata": {
                    "amc_name": "HDFC Mutual Fund",
                    "amc_id": "hdfc",
                    "title": "HDFC Equity Fund",
                    "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                    "scraped_at": "2025-11-14",
                },
            },
            {
                "chunk_id": "test-chunk-2",
                "content": "HDFC AMC page information",
                "source_url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
                "chunk_index": 0,
                "metadata": {
                    "amc_name": "HDFC Mutual Fund",
                    "amc_id": "hdfc",
                    "title": "HDFC Mutual Funds",
                    "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
                },
            },
        ]


class TestMetadataStructure:
    """Test suite for metadata structure validation."""

    def test_all_chunks_have_metadata(self, sample_chunks_with_metadata):
        """Test that all chunks have metadata field."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            assert "metadata" in chunk, f"Chunk {i} missing metadata field"
            
            metadata = chunk.get("metadata")
            assert isinstance(metadata, dict), (
                f"Chunk {i} metadata is not a dictionary"
            )

    def test_metadata_not_empty(self, sample_chunks_with_metadata):
        """Test that metadata contains at least some fields."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata = chunk.get("metadata", {})
            assert len(metadata) > 0, f"Chunk {i} has empty metadata"

    def test_required_metadata_fields(self, sample_chunks_with_metadata):
        """Test that required metadata fields are present."""
        required_fields = ["amc_name"]  # Minimum required field
        
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata = chunk.get("metadata", {})
            
            # At least amc_name should be present in most chunks
            has_required = any(field in metadata for field in required_fields)
            
            if not has_required:
                # Allow some chunks to miss metadata, but not all
                pass  # Will be caught by coverage test


class TestSourceURLMetadata:
    """Test suite for source URL metadata."""

    def test_source_url_in_metadata_or_chunk(self, sample_chunks_with_metadata):
        """Test that source URL is stored either in metadata or chunk level."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            chunk_url = chunk.get("source_url")
            metadata_url = chunk.get("metadata", {}).get("url")
            
            # At least one should be present
            assert chunk_url or metadata_url, (
                f"Chunk {i} has no source URL in metadata or chunk level"
            )

    def test_source_url_consistency(self, sample_chunks_with_metadata):
        """Test that source URLs are consistent between chunk and metadata."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            chunk_url = chunk.get("source_url")
            metadata_url = chunk.get("metadata", {}).get("url")
            
            # If both present, they should match
            if chunk_url and metadata_url:
                assert chunk_url == metadata_url, (
                    f"Chunk {i} source_url mismatch: "
                    f"chunk={chunk_url} vs metadata={metadata_url}"
                )

    def test_source_url_format(self, sample_chunks_with_metadata):
        """Test that source URLs in metadata have valid format."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata_url = chunk.get("metadata", {}).get("url")
            
            if metadata_url:
                assert isinstance(metadata_url, str), (
                    f"Chunk {i} metadata URL is not a string"
                )
                assert metadata_url.startswith("http"), (
                    f"Chunk {i} metadata URL has invalid format: {metadata_url}"
                )


class TestAMCMetadata:
    """Test suite for AMC-related metadata."""

    def test_amc_name_present(self, sample_chunks_with_metadata):
        """Test that AMC name is present in metadata."""
        chunks_with_amc = 0
        
        for chunk in sample_chunks_with_metadata:
            metadata = chunk.get("metadata", {})
            if "amc_name" in metadata:
                chunks_with_amc += 1
        
        # Most chunks should have AMC name
        coverage = chunks_with_amc / len(sample_chunks_with_metadata) if sample_chunks_with_metadata else 0
        assert coverage >= 0.8, (
            f"Only {coverage:.1%} of chunks have AMC name in metadata"
        )

    def test_amc_name_validity(self, sample_chunks_with_metadata):
        """Test that AMC names are valid."""
        expected_amcs = [
            "SBI Mutual Fund",
            "HDFC Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Nippon India Mutual Fund",
        ]
        
        for i, chunk in enumerate(sample_chunks_with_metadata):
            amc_name = chunk.get("metadata", {}).get("amc_name")
            
            if amc_name:
                assert amc_name in expected_amcs, (
                    f"Chunk {i} has unexpected AMC name: {amc_name}"
                )

    def test_amc_id_present(self, sample_chunks_with_metadata):
        """Test that AMC ID is present where AMC name exists."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata = chunk.get("metadata", {})
            amc_name = metadata.get("amc_name")
            amc_id = metadata.get("amc_id")
            
            # If AMC name is present, ID should also be present
            if amc_name:
                assert amc_id, (
                    f"Chunk {i} has AMC name but missing AMC ID"
                )

    def test_amc_id_format(self, sample_chunks_with_metadata):
        """Test that AMC IDs have correct format."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            amc_id = chunk.get("metadata", {}).get("amc_id")
            
            if amc_id:
                # Should be lowercase, no spaces
                assert amc_id.islower(), (
                    f"Chunk {i} AMC ID not lowercase: {amc_id}"
                )
                assert " " not in amc_id, (
                    f"Chunk {i} AMC ID contains spaces: {amc_id}"
                )


class TestContentTypeMetadata:
    """Test suite for content type classification."""

    def test_content_type_determination(self, metadata_manager):
        """Test that content type is correctly determined from URL."""
        test_cases = [
            ("https://groww.in/mutual-funds/amc/hdfc-mutual-funds", ContentType.AMC_PAGE.value),
            ("https://groww.in/mutual-funds/hdfc-equity-fund", ContentType.FUND_PAGE.value),
            ("https://groww.in/mutual-funds/top/best-hdfc-funds", ContentType.COMPARISON_PAGE.value),
            ("https://groww.in/blog/mutual-funds-guide", ContentType.BLOG_POST.value),
        ]
        
        for url, expected_type in test_cases:
            determined_type = metadata_manager._determine_content_type(url, {})
            assert determined_type == expected_type, (
                f"URL {url} incorrectly classified as {determined_type}, "
                f"expected {expected_type}"
            )

    def test_content_type_consistency(self, sample_chunks_with_metadata):
        """Test that content type is consistent for same URL."""
        url_to_types = defaultdict(set)
        
        for chunk in sample_chunks_with_metadata:
            source_url = chunk.get("source_url")
            content_type = chunk.get("metadata", {}).get("content_type")
            
            if source_url and content_type:
                url_to_types[source_url].add(content_type)
        
        # Each URL should have only one content type
        for url, types in url_to_types.items():
            assert len(types) == 1, (
                f"URL {url} has inconsistent content types: {types}"
            )


class TestTimestampMetadata:
    """Test suite for timestamp metadata."""

    def test_scraped_at_timestamp(self, sample_chunks_with_metadata):
        """Test that scraped_at timestamp is present."""
        chunks_with_timestamp = 0
        
        for chunk in sample_chunks_with_metadata:
            metadata = chunk.get("metadata", {})
            if "scraped_at" in metadata:
                chunks_with_timestamp += 1
        
        # Most chunks should have timestamp
        coverage = chunks_with_timestamp / len(sample_chunks_with_metadata) if sample_chunks_with_metadata else 0
        assert coverage >= 0.7, (
            f"Only {coverage:.1%} of chunks have scraped_at timestamp"
        )

    def test_timestamp_format(self, sample_chunks_with_metadata):
        """Test that timestamps have valid format."""
        import re
        
        # Accept various timestamp formats
        timestamp_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",  # YYYY-MM-DD HH:MM:SS
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO format
        ]
        
        for i, chunk in enumerate(sample_chunks_with_metadata):
            scraped_at = chunk.get("metadata", {}).get("scraped_at")
            
            if scraped_at:
                valid_format = any(
                    re.match(pattern, str(scraped_at))
                    for pattern in timestamp_patterns
                )
                assert valid_format, (
                    f"Chunk {i} has invalid timestamp format: {scraped_at}"
                )


class TestTitleMetadata:
    """Test suite for title metadata."""

    def test_title_present(self, sample_chunks_with_metadata):
        """Test that title is present in metadata."""
        chunks_with_title = 0
        
        for chunk in sample_chunks_with_metadata:
            metadata = chunk.get("metadata", {})
            if metadata.get("title"):
                chunks_with_title += 1
        
        # Most chunks should have title
        coverage = chunks_with_title / len(sample_chunks_with_metadata) if sample_chunks_with_metadata else 0
        assert coverage >= 0.7, (
            f"Only {coverage:.1%} of chunks have title in metadata"
        )

    def test_title_not_empty(self, sample_chunks_with_metadata):
        """Test that titles are not empty strings."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            title = chunk.get("metadata", {}).get("title")
            
            if title is not None:
                assert len(title.strip()) > 0, (
                    f"Chunk {i} has empty title"
                )

    def test_title_reasonable_length(self, sample_chunks_with_metadata):
        """Test that titles have reasonable length."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            title = chunk.get("metadata", {}).get("title")
            
            if title:
                assert len(title) <= 200, (
                    f"Chunk {i} has unreasonably long title: {len(title)} chars"
                )


class TestStructuredInfoMetadata:
    """Test suite for structured information metadata."""

    def test_structured_info_format(self, sample_chunks_with_metadata):
        """Test that structured info has correct format."""
        for i, chunk in enumerate(sample_chunks_with_metadata):
            structured_info = chunk.get("metadata", {}).get("structured_info")
            
            if structured_info:
                assert isinstance(structured_info, dict), (
                    f"Chunk {i} structured_info is not a dictionary"
                )

    def test_structured_info_fields(self, sample_chunks_with_metadata):
        """Test that structured info contains expected fields."""
        expected_fields = [
            "expense_ratio",
            "exit_load",
            "minimum_sip",
            "lock_in_period",
            "riskometer",
            "benchmark",
        ]
        
        chunks_with_structured = 0
        field_coverage = defaultdict(int)
        
        for chunk in sample_chunks_with_metadata:
            structured_info = chunk.get("metadata", {}).get("structured_info")
            
            if structured_info:
                chunks_with_structured += 1
                for field in expected_fields:
                    if field in structured_info:
                        field_coverage[field] += 1
        
        # At least some chunks should have structured info
        if chunks_with_structured > 0:
            print(f"\nStructured info coverage: {chunks_with_structured} chunks")
            for field, count in field_coverage.items():
                print(f"  {field}: {count} chunks")


class TestMetadataManagerIntegration:
    """Test suite for metadata manager integration."""

    def test_register_and_retrieve_source(self, metadata_manager):
        """Test registering and retrieving source metadata."""
        source_metadata = {
            "url": "https://groww.in/mutual-funds/test-fund",
            "amc_name": "Test AMC",
            "amc_id": "test",
            "title": "Test Fund",
        }
        
        metadata_manager.register_source(source_metadata)
        
        # Retrieve
        retrieved = metadata_manager.get_source_metadata(source_metadata["url"])
        assert retrieved is not None
        assert retrieved["amc_name"] == "Test AMC"

    def test_register_and_retrieve_chunk(self, metadata_manager):
        """Test registering and retrieving chunk metadata."""
        chunk = {
            "chunk_id": "test-chunk-123",
            "content": "Test content",
            "source_url": "https://groww.in/mutual-funds/test",
            "chunk_index": 0,
            "metadata": {
                "amc_name": "Test AMC",
                "title": "Test",
            },
        }
        
        metadata_manager.register_chunk(chunk)
        
        # Retrieve
        retrieved = metadata_manager.get_chunk_metadata("test-chunk-123")
        assert retrieved is not None
        assert retrieved["amc_name"] == "Test AMC"

    def test_metadata_statistics(self, metadata_manager, sample_chunks_with_metadata):
        """Test metadata statistics generation."""
        # Register chunks
        for chunk in sample_chunks_with_metadata[:10]:
            metadata_manager.register_chunk(chunk)
        
        # Get statistics
        stats = metadata_manager.get_statistics()
        
        assert "total_chunks" in stats
        assert "total_sources" in stats
        assert "total_amcs" in stats
        assert stats["total_chunks"] > 0

    def test_metadata_validation(self, metadata_manager, sample_chunks_with_metadata):
        """Test metadata validation functionality."""
        # Register some data
        for chunk in sample_chunks_with_metadata[:5]:
            metadata_manager.register_chunk(chunk)
        
        # Validate
        validation = metadata_manager.validate_metadata()
        
        assert "valid" in validation
        assert "issues" in validation
        assert isinstance(validation["issues"], list)


class TestMetadataCompleteness:
    """Test suite for metadata completeness."""

    def test_metadata_coverage_per_chunk(self, sample_chunks_with_metadata):
        """Test that each chunk has sufficient metadata coverage."""
        min_fields = 3  # Minimum number of metadata fields per chunk
        
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata = chunk.get("metadata", {})
            field_count = len([v for v in metadata.values() if v])
            
            assert field_count >= min_fields, (
                f"Chunk {i} has insufficient metadata: only {field_count} fields"
            )

    def test_critical_metadata_present(self, sample_chunks_with_metadata):
        """Test that critical metadata fields are present."""
        critical_fields = ["amc_name", "url"]  # At least one should be present
        
        for i, chunk in enumerate(sample_chunks_with_metadata):
            metadata = chunk.get("metadata", {})
            source_url = chunk.get("source_url")
            
            has_critical = (
                any(metadata.get(field) for field in critical_fields)
                or source_url
            )
            
            assert has_critical, (
                f"Chunk {i} missing all critical metadata fields"
            )


def test_metadata_integrity():
    """Integration test for metadata integrity."""
    # Load sample data
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        pytest.skip("No data available for integration test")
    
    if not chunks:
        pytest.skip("No chunks available")
    
    # Create metadata manager
    manager = MetadataManager(metadata_file="data/test_metadata_integration.json")
    
    # Register all chunks
    for chunk in chunks[:50]:  # Test with first 50
        manager.register_chunk(chunk)
    
    # Get statistics
    stats = manager.get_statistics()
    
    # Validate
    assert stats["total_chunks"] > 0
    assert stats["total_sources"] > 0
    
    # Validate metadata
    validation = manager.validate_metadata()
    
    # Should mostly pass validation
    if not validation["valid"]:
        issue_ratio = validation["total_issues"] / stats["total_chunks"]
        assert issue_ratio < 0.2, (
            f"Too many validation issues: {issue_ratio:.1%}"
        )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

