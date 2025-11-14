"""
Test suite for validating scraped content quality.

This module tests the quality of scraped data including:
- Content completeness
- Content length validation
- Duplicate detection
- Data structure validation
- URL validity
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validator import DataValidator


@pytest.fixture
def validator():
    """Create a data validator instance."""
    return DataValidator(
        min_content_length=50,
        max_content_length=100000,
        duplicate_threshold=0.9,
    )


@pytest.fixture
def sample_scraped_data():
    """Load sample scraped data or create mock data."""
    try:
        with open("data/scraped_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("scraped_content", [])
    except FileNotFoundError:
        # Return mock data for testing
        return [
            {
                "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
                "amc_name": "HDFC Mutual Fund",
                "amc_id": "hdfc",
                "title": "HDFC Mutual Funds",
                "content": "HDFC Mutual Fund offers a wide range of mutual fund schemes. " * 20,
                "scraped_at": "2025-11-14",
            },
            {
                "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                "amc_name": "HDFC Mutual Fund",
                "amc_id": "hdfc",
                "title": "HDFC Equity Fund",
                "content": "HDFC Equity Fund is a large cap equity fund with expense ratio of 1.5%. " * 15,
                "scraped_at": "2025-11-14",
            },
        ]


class TestScrapedContentQuality:
    """Test suite for scraped content quality."""

    def test_scraped_data_structure(self, sample_scraped_data):
        """Test that scraped data has the correct structure."""
        assert isinstance(sample_scraped_data, list), "Scraped data should be a list"
        assert len(sample_scraped_data) > 0, "Scraped data should not be empty"

        for item in sample_scraped_data:
            assert isinstance(item, dict), "Each item should be a dictionary"
            assert "url" in item, "Each item should have a URL"
            assert "content" in item, "Each item should have content"

    def test_required_fields_present(self, sample_scraped_data, validator):
        """Test that all required fields are present in scraped data."""
        required_fields = ["url", "content", "amc_name"]

        for i, item in enumerate(sample_scraped_data):
            for field in required_fields:
                assert field in item, f"Item {i} missing required field: {field}"

    def test_content_length_validation(self, sample_scraped_data, validator):
        """Test that content length is within acceptable range."""
        for i, item in enumerate(sample_scraped_data):
            content = item.get("content", "")
            content_length = len(content)

            assert (
                content_length >= validator.min_content_length
            ), f"Item {i} content too short: {content_length} chars"

            assert (
                content_length <= validator.max_content_length
            ), f"Item {i} content too long: {content_length} chars"

    def test_url_validity(self, sample_scraped_data, validator):
        """Test that all URLs are valid."""
        for i, item in enumerate(sample_scraped_data):
            url = item.get("url")
            assert validator._validate_url(url), f"Item {i} has invalid URL: {url}"

    def test_no_empty_content(self, sample_scraped_data):
        """Test that no items have empty content."""
        for i, item in enumerate(sample_scraped_data):
            content = item.get("content", "")
            assert content.strip(), f"Item {i} has empty content"

    def test_duplicate_detection(self, sample_scraped_data, validator):
        """Test duplicate detection in scraped data."""
        duplicates = validator._detect_duplicates(sample_scraped_data)

        # Log duplicates for inspection
        if duplicates:
            print(f"\nFound {len(duplicates)} duplicate pairs:")
            for idx1, idx2 in duplicates:
                print(f"  - Items {idx1} and {idx2} are duplicates")

        # Assert no duplicates (or document why duplicates are acceptable)
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate documents"

    def test_content_quality(self, sample_scraped_data, validator):
        """Test that content is not low quality."""
        low_quality_items = []

        for i, item in enumerate(sample_scraped_data):
            content = item.get("content", "")
            if validator._is_low_quality_content(content):
                low_quality_items.append(i)

        assert len(low_quality_items) == 0, (
            f"Found {len(low_quality_items)} low quality items: {low_quality_items}"
        )

    def test_amc_name_consistency(self, sample_scraped_data):
        """Test that AMC names are consistent and valid."""
        expected_amcs = [
            "SBI Mutual Fund",
            "HDFC Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Nippon India Mutual Fund",
        ]

        amc_names = set()
        for item in sample_scraped_data:
            amc_name = item.get("amc_name")
            if amc_name:
                amc_names.add(amc_name)

        # Check that all AMC names are in the expected list
        for amc in amc_names:
            assert amc in expected_amcs, f"Unexpected AMC name: {amc}"

    def test_url_domain_validity(self, sample_scraped_data):
        """Test that all URLs are from expected domains."""
        expected_domains = ["groww.in", "amfiindia.com", "sebi.gov.in"]

        for i, item in enumerate(sample_scraped_data):
            url = item.get("url", "")
            domain_found = False

            for domain in expected_domains:
                if domain in url:
                    domain_found = True
                    break

            assert domain_found, f"Item {i} URL from unexpected domain: {url}"

    def test_timestamp_presence(self, sample_scraped_data):
        """Test that scraping timestamps are present."""
        for i, item in enumerate(sample_scraped_data):
            assert (
                "scraped_at" in item
            ), f"Item {i} missing scraped_at timestamp"

    def test_full_validation_passes(self, sample_scraped_data, validator):
        """Test that full validation returns acceptable results."""
        results = validator.validate_scraped_data(sample_scraped_data)

        # Check validation results
        assert results["total_documents"] == len(sample_scraped_data)
        assert results["valid_documents"] > 0, "No valid documents found"

        # Allow some issues but ensure majority are valid
        valid_ratio = results["valid_documents"] / results["total_documents"]
        assert valid_ratio >= 0.8, f"Only {valid_ratio:.1%} of documents are valid"


class TestContentExtraction:
    """Test suite for content extraction quality."""

    def test_title_extraction(self, sample_scraped_data):
        """Test that titles are extracted properly."""
        for i, item in enumerate(sample_scraped_data):
            title = item.get("title")
            assert title, f"Item {i} missing title"
            assert len(title) > 0, f"Item {i} has empty title"

    def test_content_not_just_html(self, sample_scraped_data):
        """Test that content doesn't contain raw HTML tags."""
        html_indicators = ["<html>", "<body>", "<div", "<script>", "<style>"]

        for i, item in enumerate(sample_scraped_data):
            content = item.get("content", "")

            for indicator in html_indicators:
                assert (
                    indicator not in content
                ), f"Item {i} contains HTML tag: {indicator}"

    def test_minimum_word_count(self, sample_scraped_data):
        """Test that content has minimum word count."""
        min_words = 20

        for i, item in enumerate(sample_scraped_data):
            content = item.get("content", "")
            words = content.split()

            assert len(words) >= min_words, (
                f"Item {i} has insufficient words: {len(words)} (minimum: {min_words})"
            )


class TestDataCompleteness:
    """Test suite for data completeness."""

    def test_all_amcs_represented(self, sample_scraped_data):
        """Test that all expected AMCs have data."""
        expected_amcs = [
            "SBI Mutual Fund",
            "HDFC Mutual Fund",
            "ICICI Prudential Mutual Fund",
            "Axis Mutual Fund",
            "Nippon India Mutual Fund",
        ]

        found_amcs = set()
        for item in sample_scraped_data:
            amc_name = item.get("amc_name")
            if amc_name:
                found_amcs.add(amc_name)

        # Check that we have data for most AMCs
        coverage = len(found_amcs) / len(expected_amcs)
        assert coverage >= 0.8, (
            f"Only {coverage:.1%} of AMCs have data. "
            f"Missing: {set(expected_amcs) - found_amcs}"
        )

    def test_minimum_documents_per_amc(self, sample_scraped_data):
        """Test that each AMC has minimum number of documents."""
        min_docs_per_amc = 1
        amc_counts = {}

        for item in sample_scraped_data:
            amc_name = item.get("amc_name")
            if amc_name:
                amc_counts[amc_name] = amc_counts.get(amc_name, 0) + 1

        for amc, count in amc_counts.items():
            assert count >= min_docs_per_amc, (
                f"AMC '{amc}' has only {count} documents "
                f"(minimum: {min_docs_per_amc})"
            )


def test_validation_results_structure(validator):
    """Test that validation results have expected structure."""
    # Create minimal test data
    test_data = [
        {
            "url": "https://example.com",
            "content": "Test content with sufficient length to pass validation checks.",
            "amc_name": "Test AMC",
        }
    ]

    results = validator.validate_scraped_data(test_data)

    # Check result structure
    assert "total_documents" in results
    assert "valid_documents" in results
    assert "issues" in results
    assert "duplicates" in results
    assert "duplicate_count" in results

    assert isinstance(results["total_documents"], int)
    assert isinstance(results["valid_documents"], int)
    assert isinstance(results["issues"], list)
    assert isinstance(results["duplicates"], list)


def test_error_reporting(validator):
    """Test that validation properly reports errors."""
    # Create data with known issues
    bad_data = [
        {
            "url": "invalid-url",  # Invalid URL
            "content": "short",  # Too short
            "amc_name": "Test",
        },
        {
            "url": "https://example.com",
            "content": "",  # Empty content
        },
    ]

    results = validator.validate_scraped_data(bad_data)

    # Should detect issues
    assert len(results["issues"]) > 0, "Validator should detect issues in bad data"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

