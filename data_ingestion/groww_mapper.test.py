"""
Unit tests for the groww_mapper module
"""

import pytest
from groww_mapper import GrowwMapper


@pytest.fixture
def mapper():
    """Create a Groww mapper."""
    return GrowwMapper()


def test_mapper_initialization(mapper):
    """Test mapper initialization."""
    assert mapper.groww_domain == "groww.in"
    assert mapper.groww_base_url == "https://groww.in"
    assert len(mapper.info_categories) > 0


def test_is_groww_url(mapper):
    """Test Groww URL detection."""
    # Groww URLs
    assert mapper.is_groww_url("https://groww.in/mutual-funds/hdfc-equity") is True
    assert mapper.is_groww_url("https://www.groww.in/mutual-funds/amc/hdfc") is True

    # Non-Groww URLs
    assert mapper.is_groww_url("https://www.amfiindia.com/") is False
    assert mapper.is_groww_url("https://www.sebi.gov.in/") is False


def test_identify_info_category(mapper):
    """Test information category identification."""
    # Expense ratio
    assert mapper.identify_info_category("What is the expense ratio?") == "expense_ratio"

    # Exit load
    assert mapper.identify_info_category("Tell me about exit load") == "exit_load"

    # Minimum SIP
    assert mapper.identify_info_category("What is minimum SIP amount?") == "minimum_sip"

    # Returns
    assert mapper.identify_info_category("Show me the returns") == "returns"

    # NAV
    assert mapper.identify_info_category("What is the current NAV?") == "nav"

    # Unknown
    assert mapper.identify_info_category("Random unrelated query") is None


def test_extract_fund_slug_from_url(mapper):
    """Test fund slug extraction."""
    # Valid fund URL
    url = "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth"
    slug = mapper.extract_fund_slug_from_url(url)
    assert slug == "hdfc-equity-fund-direct-growth"

    # AMC URL (should return None)
    url = "https://groww.in/mutual-funds/amc/hdfc-mutual-funds"
    slug = mapper.extract_fund_slug_from_url(url)
    assert slug is None

    # Non-Groww URL
    url = "https://www.amfiindia.com/schemes"
    slug = mapper.extract_fund_slug_from_url(url)
    assert slug is None


def test_extract_amc_slug_from_url(mapper):
    """Test AMC slug extraction."""
    # Valid AMC URL
    url = "https://groww.in/mutual-funds/amc/hdfc-mutual-funds"
    slug = mapper.extract_amc_slug_from_url(url)
    assert slug == "hdfc-mutual-funds"

    # Fund URL (should return None)
    url = "https://groww.in/mutual-funds/hdfc-equity-fund"
    slug = mapper.extract_amc_slug_from_url(url)
    assert slug is None


def test_get_amc_slug(mapper):
    """Test getting AMC slug from name."""
    assert mapper.get_amc_slug("HDFC Mutual Fund") == "hdfc-mutual-funds"
    assert mapper.get_amc_slug("SBI Mutual Fund") == "sbi-mutual-funds"
    assert mapper.get_amc_slug("Unknown AMC") is None


def test_build_groww_url(mapper):
    """Test building Groww URLs."""
    # Fund details
    url = mapper.build_groww_url("expense_ratio", fund_slug="hdfc-equity-fund")
    assert "groww.in/mutual-funds/hdfc-equity-fund" in url
    assert "#expense-ratio" in url

    # AMC page
    url = mapper.build_groww_url("amc_page", amc_slug="hdfc-mutual-funds")
    assert "groww.in/mutual-funds/amc/hdfc-mutual-funds" in url

    # Download statement (no slug needed)
    url = mapper.build_groww_url("download_statement")
    assert "groww.in/mutual-funds/user/statements" in url

    # Category not available on Groww
    url = mapper.build_groww_url("scheme_document", fund_slug="test")
    assert url is None


def test_map_chunk_to_groww(mapper):
    """Test mapping chunk to Groww page."""
    # Chunk with Groww source URL
    chunk = {
        "content": "The expense ratio is 1.5%",
        "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund",
        "metadata": {"amc_name": "HDFC Mutual Fund"},
    }
    groww_url = mapper.map_chunk_to_groww(chunk)
    assert groww_url == "https://groww.in/mutual-funds/hdfc-equity-fund"

    # Chunk with non-Groww source but identifiable category
    chunk = {
        "content": "Minimum SIP amount is Rs. 500",
        "source_url": "https://example.com",
        "metadata": {"amc_name": "HDFC Mutual Fund"},
    }
    groww_url = mapper.map_chunk_to_groww(chunk)
    # Should return None because we can't determine fund slug from external URL
    assert groww_url is None or "groww.in" in groww_url


def test_determine_source_priority(mapper):
    """Test source URL prioritization."""
    chunk = {
        "source_url": "https://example.com/fund",
        "metadata": {},
    }

    # With Groww URL available
    query = "What is the expense ratio?"
    groww_url = "https://groww.in/mutual-funds/hdfc-equity"
    primary, secondary = mapper.determine_source_priority(query, chunk, groww_url)

    assert primary == groww_url
    assert secondary == "https://example.com/fund"

    # Without Groww URL
    primary, secondary = mapper.determine_source_priority(query, chunk, None)
    assert primary == "https://example.com/fund"
    assert secondary is None


def test_get_fallback_message(mapper):
    """Test fallback message generation."""
    # Groww URL
    message = mapper.get_fallback_message(
        "expense_ratio", "https://groww.in/mutual-funds/hdfc-equity"
    )
    assert "Groww" in message

    # External URL
    message = mapper.get_fallback_message("scheme_document", "https://example.com/doc")
    assert "official source" in message


def test_process_chunks_with_mapping(mapper):
    """Test processing multiple chunks with mapping."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "content": "Expense ratio is 1.5%",
            "source_url": "https://groww.in/mutual-funds/hdfc-equity",
            "metadata": {"amc_name": "HDFC Mutual Fund"},
        },
        {
            "chunk_id": "chunk-2",
            "content": "Minimum SIP is Rs. 500",
            "source_url": "https://groww.in/mutual-funds/sbi-bluechip",
            "metadata": {"amc_name": "SBI Mutual Fund"},
        },
    ]

    processed = mapper.process_chunks_with_mapping(chunks)

    assert len(processed) == 2
    assert all("groww_page_url" in chunk for chunk in processed)


def test_get_mapping_statistics(mapper):
    """Test getting mapping statistics."""
    chunks = [
        {
            "content": "Expense ratio is 1.5%",
            "source_url": "https://groww.in/mutual-funds/hdfc-equity",
            "groww_page_url": "https://groww.in/mutual-funds/hdfc-equity",
        },
        {
            "content": "Minimum SIP is Rs. 500",
            "source_url": "https://example.com",
            "groww_page_url": None,
        },
        {
            "content": "Returns are 12%",
            "source_url": "https://groww.in/mutual-funds/sbi-bluechip",
            "groww_page_url": "https://groww.in/mutual-funds/sbi-bluechip",
        },
    ]

    stats = mapper.get_mapping_statistics(chunks)

    assert stats["total_chunks"] == 3
    assert stats["chunks_with_groww_url"] == 2
    assert stats["chunks_from_groww_source"] == 2
    assert stats["mapping_rate"] > 0


def test_info_categories_coverage(mapper):
    """Test that all important info categories are covered."""
    expected_categories = [
        "expense_ratio",
        "exit_load",
        "minimum_sip",
        "returns",
        "nav",
        "download_statement",
    ]

    for category in expected_categories:
        assert category in mapper.info_categories


def test_amc_slug_mapping_coverage(mapper):
    """Test that all required AMCs are mapped."""
    expected_amcs = [
        "SBI Mutual Fund",
        "HDFC Mutual Fund",
        "ICICI Prudential Mutual Fund",
        "Axis Mutual Fund",
        "Nippon India Mutual Fund",
    ]

    for amc in expected_amcs:
        assert mapper.get_amc_slug(amc) is not None


def test_external_only_categories(mapper):
    """Test handling of categories that require external sources."""
    # Scheme document is not available on Groww
    category = "scheme_document"
    config = mapper.info_categories[category]

    assert config.get("groww_available", True) is False
    assert config.get("external_required", False) is True

    # Should not build Groww URL for this category
    url = mapper.build_groww_url(category, fund_slug="test-fund")
    assert url is None

