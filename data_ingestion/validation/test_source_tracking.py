"""
Test suite for validating source URL tracking and linking.

This module tests that:
- Source URLs are correctly stored
- Chunks are properly linked to source URLs
- URL-to-chunk mappings are accurate
- Source tracking system maintains integrity
"""

import pytest
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata_manager import MetadataManager
from source_tracker import SourceTracker


@pytest.fixture
def metadata_manager():
    """Create a metadata manager instance."""
    return MetadataManager(metadata_file="data/test_metadata_index.json")


@pytest.fixture
def source_tracker():
    """Create a source tracker instance."""
    return SourceTracker(source_file="data/source_urls.json")


@pytest.fixture
def sample_chunks():
    """Load sample chunks or create mock data."""
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("chunks", [])
    except FileNotFoundError:
        # Return mock data for testing
        return [
            {
                "chunk_id": "test-chunk-1",
                "content": "HDFC Equity Fund has an expense ratio of 1.5%",
                "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                "chunk_index": 0,
                "metadata": {
                    "amc_name": "HDFC Mutual Fund",
                    "amc_id": "hdfc",
                    "title": "HDFC Equity Fund",
                },
                "embedding": [0.1] * 384,
            },
            {
                "chunk_id": "test-chunk-2",
                "content": "Minimum SIP amount is Rs. 500 per month",
                "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                "chunk_index": 1,
                "metadata": {
                    "amc_name": "HDFC Mutual Fund",
                    "amc_id": "hdfc",
                    "title": "HDFC Equity Fund",
                },
                "embedding": [0.2] * 384,
            },
        ]


class TestSourceURLStorage:
    """Test suite for source URL storage."""

    def test_all_chunks_have_source_url(self, sample_chunks):
        """Test that all chunks have a source URL."""
        for i, chunk in enumerate(sample_chunks):
            assert "source_url" in chunk, f"Chunk {i} missing source_url field"
            
            source_url = chunk.get("source_url")
            assert source_url, f"Chunk {i} has empty source_url"
            assert isinstance(source_url, str), f"Chunk {i} source_url is not a string"

    def test_source_url_format(self, sample_chunks):
        """Test that source URLs have valid format."""
        for i, chunk in enumerate(sample_chunks):
            source_url = chunk.get("source_url", "")
            
            # Check URL starts with http/https
            assert source_url.startswith("http"), (
                f"Chunk {i} source_url doesn't start with http/https: {source_url}"
            )
            
            # Check URL has a domain
            assert "://" in source_url, f"Chunk {i} source_url missing protocol separator"

    def test_source_url_consistency(self, sample_chunks):
        """Test that source URLs are consistent across related chunks."""
        url_to_chunks = defaultdict(list)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            if source_url:
                url_to_chunks[source_url].append(chunk)
        
        # If multiple chunks from same source, they should have consistent metadata
        for url, chunks in url_to_chunks.items():
            if len(chunks) > 1:
                # Check AMC name consistency
                amc_names = set()
                for chunk in chunks:
                    amc_name = chunk.get("metadata", {}).get("amc_name")
                    if amc_name:
                        amc_names.add(amc_name)
                
                assert len(amc_names) <= 1, (
                    f"Inconsistent AMC names for URL {url}: {amc_names}"
                )


class TestChunkToURLLinking:
    """Test suite for chunk-to-URL linking."""

    def test_chunk_id_to_url_mapping(self, sample_chunks):
        """Test that chunk IDs can be mapped to source URLs."""
        chunk_id_to_url = {}
        
        for chunk in sample_chunks:
            chunk_id = chunk.get("chunk_id")
            source_url = chunk.get("source_url")
            
            if chunk_id and source_url:
                # Check for duplicate chunk IDs
                if chunk_id in chunk_id_to_url:
                    assert chunk_id_to_url[chunk_id] == source_url, (
                        f"Chunk ID {chunk_id} mapped to multiple URLs"
                    )
                chunk_id_to_url[chunk_id] = source_url
        
        # Verify all chunks have unique IDs
        assert len(chunk_id_to_url) == len(sample_chunks), (
            "Some chunks have duplicate or missing chunk IDs"
        )

    def test_url_to_chunks_mapping(self, sample_chunks):
        """Test that URLs can be mapped to their chunks."""
        url_to_chunks = defaultdict(list)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            chunk_id = chunk.get("chunk_id")
            
            if source_url and chunk_id:
                url_to_chunks[source_url].append(chunk_id)
        
        # Verify each URL has at least one chunk
        for url, chunk_ids in url_to_chunks.items():
            assert len(chunk_ids) > 0, f"URL {url} has no chunks"
            
            # Verify no duplicate chunk IDs per URL
            assert len(chunk_ids) == len(set(chunk_ids)), (
                f"URL {url} has duplicate chunk IDs"
            )

    def test_chunk_index_sequence(self, sample_chunks):
        """Test that chunk indices are sequential per source URL."""
        url_to_indices = defaultdict(list)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            chunk_index = chunk.get("chunk_index")
            
            if source_url is not None and chunk_index is not None:
                url_to_indices[source_url].append(chunk_index)
        
        # Check indices are sequential for each URL
        for url, indices in url_to_indices.items():
            sorted_indices = sorted(indices)
            
            # Should start at 0
            if sorted_indices:
                assert sorted_indices[0] == 0, (
                    f"URL {url} chunk indices don't start at 0: {sorted_indices[0]}"
                )
            
            # Should be continuous (allowing for some missing chunks)
            max_gap = 5  # Allow some gaps for filtering
            for i in range(len(sorted_indices) - 1):
                gap = sorted_indices[i + 1] - sorted_indices[i]
                assert gap <= max_gap, (
                    f"URL {url} has large gap in chunk indices: {sorted_indices}"
                )


class TestMetadataLinking:
    """Test suite for metadata linking to source URLs."""

    def test_metadata_contains_source_info(self, sample_chunks):
        """Test that metadata contains source information."""
        for i, chunk in enumerate(sample_chunks):
            metadata = chunk.get("metadata", {})
            
            assert isinstance(metadata, dict), f"Chunk {i} metadata is not a dict"
            
            # Check for key metadata fields related to source
            source_url = chunk.get("source_url")
            if source_url:
                # At least one of these should be present
                has_source_info = (
                    "amc_name" in metadata
                    or "title" in metadata
                    or "url" in metadata
                )
                assert has_source_info, (
                    f"Chunk {i} metadata missing source information"
                )

    def test_amc_name_in_metadata(self, sample_chunks):
        """Test that AMC name is stored in metadata."""
        chunks_with_amc = 0
        
        for chunk in sample_chunks:
            metadata = chunk.get("metadata", {})
            amc_name = metadata.get("amc_name")
            
            if amc_name:
                chunks_with_amc += 1
                assert isinstance(amc_name, str), "AMC name should be a string"
                assert len(amc_name) > 0, "AMC name should not be empty"
        
        # Most chunks should have AMC name
        coverage = chunks_with_amc / len(sample_chunks) if sample_chunks else 0
        assert coverage >= 0.8, (
            f"Only {coverage:.1%} of chunks have AMC name in metadata"
        )

    def test_metadata_url_matches_source_url(self, sample_chunks):
        """Test that metadata URL matches chunk source URL."""
        for i, chunk in enumerate(sample_chunks):
            source_url = chunk.get("source_url")
            metadata = chunk.get("metadata", {})
            metadata_url = metadata.get("url")
            
            if source_url and metadata_url:
                assert source_url == metadata_url, (
                    f"Chunk {i} source_url and metadata.url don't match: "
                    f"{source_url} vs {metadata_url}"
                )


class TestMetadataManagerIntegration:
    """Test suite for metadata manager integration."""

    def test_metadata_manager_registration(self, metadata_manager, sample_chunks):
        """Test that metadata manager can register chunks."""
        for chunk in sample_chunks[:5]:  # Test with first 5 chunks
            metadata_manager.register_chunk(chunk)
        
        # Verify chunks are registered
        stats = metadata_manager.get_statistics()
        assert stats["total_chunks"] >= 5, "Chunks not properly registered"

    def test_get_chunks_by_url(self, metadata_manager, sample_chunks):
        """Test retrieving chunks by URL."""
        # Register chunks
        for chunk in sample_chunks[:10]:
            metadata_manager.register_chunk(chunk)
        
        # Get chunks by URL
        if sample_chunks:
            test_url = sample_chunks[0].get("source_url")
            if test_url:
                chunks = metadata_manager.get_chunks_by_url(test_url)
                assert isinstance(chunks, list), "Should return a list"
                assert len(chunks) > 0, f"Should find chunks for URL: {test_url}"

    def test_get_chunks_by_amc(self, metadata_manager, sample_chunks):
        """Test retrieving chunks by AMC."""
        # Register chunks
        for chunk in sample_chunks[:10]:
            metadata_manager.register_chunk(chunk)
        
        # Get chunks by AMC
        if sample_chunks:
            test_amc = sample_chunks[0].get("metadata", {}).get("amc_name")
            if test_amc:
                chunks = metadata_manager.get_chunks_by_amc(test_amc)
                assert isinstance(chunks, list), "Should return a list"
                assert len(chunks) > 0, f"Should find chunks for AMC: {test_amc}"

    def test_metadata_validation(self, metadata_manager, sample_chunks):
        """Test metadata validation for registered chunks."""
        # Register chunks
        for chunk in sample_chunks[:10]:
            metadata_manager.register_chunk(chunk)
        
        # Validate metadata
        validation = metadata_manager.validate_metadata()
        
        assert "valid" in validation, "Validation should return validity status"
        assert "issues" in validation, "Validation should return issues list"


class TestSourceTracker:
    """Test suite for source tracker."""

    def test_source_urls_loaded(self, source_tracker):
        """Test that source URLs are loaded."""
        sources = source_tracker.get_all_sources()
        
        assert isinstance(sources, dict), "Sources should be a dictionary"
        assert len(sources) > 0, "Should have source URLs loaded"

    def test_url_validation(self, source_tracker):
        """Test URL validation functionality."""
        # Valid URL
        valid_url = "https://groww.in/mutual-funds/hdfc-equity-fund"
        assert source_tracker.validate_url(valid_url), "Valid URL should pass"
        
        # Invalid URL
        invalid_url = "not-a-url"
        assert not source_tracker.validate_url(invalid_url), "Invalid URL should fail"

    def test_amc_url_mapping(self, source_tracker):
        """Test AMC to URL mapping."""
        sources = source_tracker.get_all_sources()
        
        for amc_name, urls in sources.items():
            assert isinstance(urls, list), f"URLs for {amc_name} should be a list"
            assert len(urls) > 0, f"AMC {amc_name} should have URLs"
            
            # Verify all URLs are valid
            for url in urls:
                assert isinstance(url, str), "Each URL should be a string"
                assert url.startswith("http"), f"Invalid URL format: {url}"


class TestSourceLinkageIntegrity:
    """Test suite for source linkage integrity."""

    def test_no_orphaned_chunks(self, sample_chunks):
        """Test that no chunks are orphaned (missing source URL)."""
        orphaned_chunks = []
        
        for i, chunk in enumerate(sample_chunks):
            source_url = chunk.get("source_url")
            if not source_url:
                orphaned_chunks.append(i)
        
        assert len(orphaned_chunks) == 0, (
            f"Found {len(orphaned_chunks)} orphaned chunks: {orphaned_chunks}"
        )

    def test_bidirectional_linking(self, sample_chunks):
        """Test bidirectional linking between chunks and URLs."""
        # Build mappings
        chunk_to_url = {}
        url_to_chunks = defaultdict(set)
        
        for chunk in sample_chunks:
            chunk_id = chunk.get("chunk_id")
            source_url = chunk.get("source_url")
            
            if chunk_id and source_url:
                chunk_to_url[chunk_id] = source_url
                url_to_chunks[source_url].add(chunk_id)
        
        # Verify bidirectional consistency
        for chunk_id, url in chunk_to_url.items():
            assert chunk_id in url_to_chunks[url], (
                f"Chunk {chunk_id} not in reverse mapping for URL {url}"
            )
        
        for url, chunk_ids in url_to_chunks.items():
            for chunk_id in chunk_ids:
                assert chunk_to_url.get(chunk_id) == url, (
                    f"Reverse mapping mismatch for chunk {chunk_id}"
                )

    def test_coverage_statistics(self, sample_chunks):
        """Test source URL coverage statistics."""
        unique_urls = set()
        chunks_with_urls = 0
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            if source_url:
                unique_urls.add(source_url)
                chunks_with_urls += 1
        
        # All chunks should have URLs
        coverage = chunks_with_urls / len(sample_chunks) if sample_chunks else 0
        assert coverage == 1.0, f"Only {coverage:.1%} of chunks have source URLs"
        
        # Should have multiple unique URLs
        assert len(unique_urls) > 0, "No unique source URLs found"


def test_source_tracking_integration():
    """Integration test for complete source tracking system."""
    # This test validates the entire source tracking workflow
    
    # Load sample data
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        pytest.skip("No chunks data available for integration test")
    
    if not chunks:
        pytest.skip("No chunks available for integration test")
    
    # Create metadata manager
    manager = MetadataManager(metadata_file="data/test_metadata_index.json")
    
    # Register all chunks
    for chunk in chunks:
        manager.register_chunk(chunk)
    
    # Get statistics
    stats = manager.get_statistics()
    
    # Verify statistics
    assert stats["total_chunks"] == len(chunks)
    assert stats["total_sources"] > 0
    assert stats["total_amcs"] > 0
    
    # Validate metadata
    validation = manager.validate_metadata()
    assert validation["valid"] or validation["total_issues"] < len(chunks) * 0.1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

