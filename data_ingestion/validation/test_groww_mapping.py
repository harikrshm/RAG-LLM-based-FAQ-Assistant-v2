"""
Test suite for validating Groww page mappings.

This module tests that:
- Groww page mappings are correctly stored
- Mapping logic follows priority rules
- Groww URLs are valid
- Chunks from Groww sources are properly identified
- Fallback logic works correctly
"""

import pytest
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from groww_mapper import GrowwMapper


@pytest.fixture
def groww_mapper():
    """Create a Groww mapper instance."""
    return GrowwMapper()


@pytest.fixture
def sample_chunks_with_mappings():
    """Load sample chunks with Groww mappings or create mock data."""
    try:
        with open("data/chunks_final.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("chunks", [])
    except FileNotFoundError:
        try:
            with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("chunks", [])
        except FileNotFoundError:
            # Return mock data for testing
            return [
                {
                    "chunk_id": "test-1",
                    "content": "Expense ratio is 1.5%",
                    "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                    "metadata": {"amc_name": "HDFC Mutual Fund"},
                    "groww_page_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
                },
                {
                    "chunk_id": "test-2",
                    "content": "HDFC AMC information",
                    "source_url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
                    "metadata": {"amc_name": "HDFC Mutual Fund"},
                    "groww_page_url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
                },
            ]


class TestGrowwMappingPresence:
    """Test suite for Groww mapping presence."""

    def test_groww_page_url_field_exists(self, sample_chunks_with_mappings):
        """Test that groww_page_url field exists in chunks."""
        chunks_with_field = 0
        
        for chunk in sample_chunks_with_mappings:
            if "groww_page_url" in chunk:
                chunks_with_field += 1
        
        # Most chunks should have this field (even if None)
        ratio = chunks_with_field / len(sample_chunks_with_mappings) if sample_chunks_with_mappings else 0
        assert ratio >= 0.9, (
            f"Only {ratio:.1%} of chunks have groww_page_url field"
        )

    def test_groww_chunks_have_mapping(self, sample_chunks_with_mappings):
        """Test that chunks from Groww sources have Groww mappings."""
        groww_chunks = []
        groww_chunks_with_mapping = []
        
        for chunk in sample_chunks_with_mappings:
            source_url = chunk.get("source_url", "")
            groww_page_url = chunk.get("groww_page_url")
            
            if "groww.in" in source_url:
                groww_chunks.append(chunk)
                if groww_page_url:
                    groww_chunks_with_mapping.append(chunk)
        
        if groww_chunks:
            ratio = len(groww_chunks_with_mapping) / len(groww_chunks)
            assert ratio >= 0.9, (
                f"Only {ratio:.1%} of Groww chunks have groww_page_url"
            )


class TestGrowwURLValidity:
    """Test suite for Groww URL validity."""

    def test_groww_urls_are_valid(self, sample_chunks_with_mappings):
        """Test that Groww URLs are valid."""
        for i, chunk in enumerate(sample_chunks_with_mappings):
            groww_url = chunk.get("groww_page_url")
            
            if groww_url:
                # Should be a string
                assert isinstance(groww_url, str), (
                    f"Chunk {i} groww_page_url is not a string"
                )
                
                # Should start with http/https
                assert groww_url.startswith("http"), (
                    f"Chunk {i} groww_page_url has invalid format: {groww_url}"
                )
                
                # Should contain groww.in
                assert "groww.in" in groww_url, (
                    f"Chunk {i} groww_page_url is not a Groww URL: {groww_url}"
                )

    def test_groww_urls_have_proper_paths(self, sample_chunks_with_mappings):
        """Test that Groww URLs have proper path structure."""
        for i, chunk in enumerate(sample_chunks_with_mappings):
            groww_url = chunk.get("groww_page_url")
            
            if groww_url:
                # Should have /mutual-funds/ path
                assert "/mutual-funds/" in groww_url, (
                    f"Chunk {i} groww_page_url missing /mutual-funds/ path: {groww_url}"
                )


class TestMappingLogic:
    """Test suite for mapping logic."""

    def test_category_identification(self, groww_mapper):
        """Test that information categories are correctly identified."""
        test_cases = [
            ("What is the expense ratio?", "expense_ratio"),
            ("Tell me about exit load", "exit_load"),
            ("What is minimum SIP amount?", "minimum_sip"),
            ("Show me the returns", "returns"),
            ("What is the NAV?", "nav"),
            ("Show portfolio holdings", "portfolio"),
            ("How to download statement?", "download_statement"),
        ]
        
        for query, expected_category in test_cases:
            identified = groww_mapper.identify_info_category(query)
            assert identified == expected_category, (
                f"Query '{query}' identified as '{identified}', "
                f"expected '{expected_category}'"
            )

    def test_url_detection(self, groww_mapper):
        """Test Groww URL detection."""
        # Groww URLs
        assert groww_mapper.is_groww_url("https://groww.in/mutual-funds/hdfc") is True
        assert groww_mapper.is_groww_url("https://www.groww.in/mutual-funds/sbi") is True
        
        # Non-Groww URLs
        assert groww_mapper.is_groww_url("https://amfiindia.com") is False
        assert groww_mapper.is_groww_url("https://sebi.gov.in") is False

    def test_fund_slug_extraction(self, groww_mapper):
        """Test fund slug extraction from URLs."""
        test_cases = [
            ("https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth", 
             "hdfc-equity-fund-direct-growth"),
            ("https://groww.in/mutual-funds/sbi-bluechip-fund-direct-plan-growth", 
             "sbi-bluechip-fund-direct-plan-growth"),
        ]
        
        for url, expected_slug in test_cases:
            slug = groww_mapper.extract_fund_slug_from_url(url)
            assert slug == expected_slug, (
                f"URL {url} extracted slug '{slug}', expected '{expected_slug}'"
            )

    def test_amc_slug_extraction(self, groww_mapper):
        """Test AMC slug extraction from URLs."""
        test_cases = [
            ("https://groww.in/mutual-funds/amc/hdfc-mutual-funds", "hdfc-mutual-funds"),
            ("https://groww.in/mutual-funds/amc/sbi-mutual-funds", "sbi-mutual-funds"),
        ]
        
        for url, expected_slug in test_cases:
            slug = groww_mapper.extract_amc_slug_from_url(url)
            assert slug == expected_slug, (
                f"URL {url} extracted AMC slug '{slug}', expected '{expected_slug}'"
            )


class TestAMCSlugMapping:
    """Test suite for AMC slug mapping."""

    def test_all_amcs_have_slugs(self, groww_mapper):
        """Test that all expected AMCs have slug mappings."""
        expected_amcs = [
            "SBI Mutual Fund",
            "HDFC Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Nippon India Mutual Fund",
        ]
        
        for amc in expected_amcs:
            slug = groww_mapper.get_amc_slug(amc)
            assert slug is not None, f"AMC '{amc}' has no slug mapping"
            assert isinstance(slug, str), f"AMC '{amc}' slug is not a string"
            assert len(slug) > 0, f"AMC '{amc}' has empty slug"

    def test_amc_slug_format(self, groww_mapper):
        """Test that AMC slugs have correct format."""
        expected_amcs = [
            "SBI Mutual Fund",
            "HDFC Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Nippon India Mutual Fund",
        ]
        
        for amc in expected_amcs:
            slug = groww_mapper.get_amc_slug(amc)
            if slug:
                # Should be lowercase
                assert slug.islower(), f"AMC '{amc}' slug not lowercase: {slug}"
                
                # Should use hyphens, not spaces
                assert " " not in slug, f"AMC '{amc}' slug contains spaces: {slug}"


class TestSourcePriority:
    """Test suite for source priority logic."""

    def test_groww_source_mapping(self, groww_mapper):
        """Test that chunks from Groww sources map to themselves."""
        chunk = {
            "content": "Expense ratio is 1.5%",
            "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
            "metadata": {"amc_name": "HDFC Mutual Fund"},
        }
        
        groww_url = groww_mapper.map_chunk_to_groww(chunk)
        
        # Should return the same URL
        assert groww_url == chunk["source_url"], (
            f"Groww source should map to itself, got: {groww_url}"
        )

    def test_priority_determination(self, groww_mapper):
        """Test source priority determination."""
        chunk = {
            "source_url": "https://external.com/fund",
            "metadata": {},
        }
        
        query = "What is the expense ratio?"
        groww_url = "https://groww.in/mutual-funds/test-fund"
        
        primary, secondary = groww_mapper.determine_source_priority(
            query, chunk, groww_url
        )
        
        # Groww URL should be primary
        assert primary == groww_url, "Groww URL should be primary source"
        assert secondary == chunk["source_url"], "External URL should be secondary"


class TestMappingCoverage:
    """Test suite for mapping coverage."""

    def test_mapping_statistics(self, sample_chunks_with_mappings):
        """Test mapping coverage statistics."""
        total_chunks = len(sample_chunks_with_mappings)
        chunks_with_mapping = sum(
            1 for chunk in sample_chunks_with_mappings 
            if chunk.get("groww_page_url")
        )
        
        mapping_rate = chunks_with_mapping / total_chunks if total_chunks > 0 else 0
        
        # At least 50% should have mappings (since we're using Groww as source)
        assert mapping_rate >= 0.5, (
            f"Low mapping coverage: {mapping_rate:.1%}"
        )

    def test_groww_source_coverage(self, sample_chunks_with_mappings):
        """Test that Groww sources have high mapping coverage."""
        groww_chunks = [
            chunk for chunk in sample_chunks_with_mappings
            if "groww.in" in chunk.get("source_url", "")
        ]
        
        if groww_chunks:
            mapped_groww = [
                chunk for chunk in groww_chunks
                if chunk.get("groww_page_url")
            ]
            
            coverage = len(mapped_groww) / len(groww_chunks)
            assert coverage >= 0.9, (
                f"Groww sources should have high mapping coverage: {coverage:.1%}"
            )


class TestInfoCategoryAvailability:
    """Test suite for information category availability on Groww."""

    def test_available_categories(self, groww_mapper):
        """Test that expected categories are marked as available on Groww."""
        available_categories = [
            "expense_ratio",
            "exit_load",
            "minimum_sip",
            "returns",
            "nav",
            "portfolio",
            "download_statement",
        ]
        
        for category in available_categories:
            config = groww_mapper.info_categories.get(category, {})
            is_available = config.get("groww_available", True)
            
            assert is_available is True, (
                f"Category '{category}' should be available on Groww"
            )

    def test_unavailable_categories(self, groww_mapper):
        """Test that certain categories require external sources."""
        unavailable_categories = [
            "scheme_document",
            "tax_treatment",
        ]
        
        for category in unavailable_categories:
            config = groww_mapper.info_categories.get(category, {})
            is_available = config.get("groww_available", True)
            requires_external = config.get("external_required", False)
            
            assert is_available is False or requires_external is True, (
                f"Category '{category}' should require external sources"
            )


class TestURLConstruction:
    """Test suite for Groww URL construction."""

    def test_build_fund_url(self, groww_mapper):
        """Test building fund-specific URLs."""
        url = groww_mapper.build_groww_url(
            "expense_ratio",
            fund_slug="hdfc-equity-fund-direct-growth"
        )
        
        assert url is not None, "Should build URL for available category"
        assert "groww.in" in url, "Should be a Groww URL"
        assert "hdfc-equity-fund-direct-growth" in url, "Should contain fund slug"
        assert "#expense-ratio" in url, "Should have section anchor"

    def test_build_amc_url(self, groww_mapper):
        """Test building AMC-specific URLs."""
        url = groww_mapper.build_groww_url(
            "amc_page",
            amc_slug="hdfc-mutual-funds"
        )
        
        assert url is not None, "Should build AMC URL"
        assert "groww.in" in url, "Should be a Groww URL"
        assert "/amc/" in url, "Should have AMC path"
        assert "hdfc-mutual-funds" in url, "Should contain AMC slug"

    def test_unavailable_category_returns_none(self, groww_mapper):
        """Test that unavailable categories return None."""
        url = groww_mapper.build_groww_url(
            "scheme_document",
            fund_slug="test-fund"
        )
        
        assert url is None, (
            "Unavailable category should return None for Groww URL"
        )


class TestMappingConsistency:
    """Test suite for mapping consistency."""

    def test_same_source_same_mapping(self, sample_chunks_with_mappings):
        """Test that chunks from same source have consistent mappings."""
        url_to_mappings = defaultdict(set)
        
        for chunk in sample_chunks_with_mappings:
            source_url = chunk.get("source_url")
            groww_url = chunk.get("groww_page_url")
            
            if source_url and groww_url:
                url_to_mappings[source_url].add(groww_url)
        
        # Each source should map to at most one Groww URL
        for source_url, mappings in url_to_mappings.items():
            assert len(mappings) == 1, (
                f"Source {source_url} has inconsistent mappings: {mappings}"
            )

    def test_mapping_idempotency(self, groww_mapper):
        """Test that mapping is idempotent."""
        chunk = {
            "content": "Expense ratio information",
            "source_url": "https://groww.in/mutual-funds/test-fund",
            "metadata": {"amc_name": "Test AMC"},
        }
        
        # Map twice
        result1 = groww_mapper.map_chunk_to_groww(chunk)
        result2 = groww_mapper.map_chunk_to_groww(chunk)
        
        # Should get same result
        assert result1 == result2, "Mapping should be idempotent"


class TestBatchProcessing:
    """Test suite for batch processing of mappings."""

    def test_process_chunks_with_mapping(self, groww_mapper):
        """Test batch processing of chunks."""
        chunks = [
            {
                "chunk_id": f"test-{i}",
                "content": "Test content about mutual funds",
                "source_url": f"https://groww.in/mutual-funds/test-{i}",
                "metadata": {"amc_name": "Test AMC"},
            }
            for i in range(5)
        ]
        
        processed = groww_mapper.process_chunks_with_mapping(chunks)
        
        assert len(processed) == 5, "Should process all chunks"
        
        for chunk in processed:
            assert "groww_page_url" in chunk, "Should add groww_page_url field"

    def test_mapping_statistics(self, groww_mapper):
        """Test mapping statistics generation."""
        chunks = [
            {
                "chunk_id": "test-1",
                "content": "Expense ratio information",
                "source_url": "https://groww.in/mutual-funds/test-1",
                "groww_page_url": "https://groww.in/mutual-funds/test-1",
            },
            {
                "chunk_id": "test-2",
                "content": "Other information",
                "source_url": "https://external.com",
                "groww_page_url": None,
            },
        ]
        
        stats = groww_mapper.get_mapping_statistics(chunks)
        
        assert "total_chunks" in stats
        assert "chunks_with_groww_url" in stats
        assert "mapping_rate" in stats
        
        assert stats["total_chunks"] == 2
        assert stats["chunks_with_groww_url"] == 1
        assert stats["mapping_rate"] == 50.0


def test_groww_mapping_integration():
    """Integration test for complete Groww mapping workflow."""
    # Create mapper
    mapper = GrowwMapper()
    
    # Create sample chunks
    chunks = [
        {
            "chunk_id": "int-test-1",
            "content": "HDFC Equity Fund has an expense ratio of 1.5%",
            "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
            "metadata": {"amc_name": "HDFC Mutual Fund"},
        },
        {
            "chunk_id": "int-test-2",
            "content": "SBI Mutual Fund information",
            "source_url": "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
            "metadata": {"amc_name": "SBI Mutual Fund"},
        },
    ]
    
    # Process chunks
    processed = mapper.process_chunks_with_mapping(chunks)
    
    # Validate
    assert len(processed) == 2
    
    for chunk in processed:
        assert "groww_page_url" in chunk
        groww_url = chunk["groww_page_url"]
        
        # Should map to itself for Groww sources
        assert groww_url == chunk["source_url"]
        assert "groww.in" in groww_url


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

