"""
Unit tests for the scraper module
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scraper import MutualFundScraper


@pytest.fixture
def sample_source_urls(tmp_path):
    """Create a sample source URLs file for testing."""
    source_file = tmp_path / "source_urls.json"
    data = {
        "amcs": [
            {
                "name": "Test AMC",
                "amc_id": "test-amc",
                "urls": ["https://example.com/test-fund"]
            }
        ],
        "metadata": {
            "total_amcs": 1,
            "total_urls": 1
        }
    }
    
    with open(source_file, "w") as f:
        json.dump(data, f)
    
    return str(source_file)


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head>
            <title>Test Mutual Fund</title>
            <meta name="description" content="Test fund description">
        </head>
        <body>
            <main class="content">
                <h1>Test Fund</h1>
                <p>Expense Ratio: 1.5%</p>
                <p>Minimum SIP: Rs. 500</p>
            </main>
        </body>
    </html>
    """


def test_scraper_initialization(sample_source_urls):
    """Test scraper initialization."""
    scraper = MutualFundScraper(source_urls_file=sample_source_urls)
    
    assert scraper.source_urls is not None
    assert len(scraper.source_urls["amcs"]) == 1
    assert scraper.timeout == 30
    assert scraper.retry_attempts == 3


def test_load_source_urls(sample_source_urls):
    """Test loading source URLs from file."""
    scraper = MutualFundScraper(source_urls_file=sample_source_urls)
    
    assert "amcs" in scraper.source_urls
    assert "metadata" in scraper.source_urls
    assert scraper.source_urls["metadata"]["total_amcs"] == 1


@patch("scraper.requests.Session.get")
def test_scrape_url_success(mock_get, sample_source_urls, sample_html):
    """Test successful URL scraping."""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = sample_html.encode("utf-8")
    mock_get.return_value = mock_response
    
    scraper = MutualFundScraper(source_urls_file=sample_source_urls)
    result = scraper.scrape_url("https://example.com/test", "Test AMC")
    
    assert result is not None
    assert result["url"] == "https://example.com/test"
    assert result["amc_name"] == "Test AMC"
    assert "Test Fund" in result["content"]
    assert "Expense Ratio" in result["content"]


@patch("scraper.requests.Session.get")
def test_scrape_url_failure(mock_get, sample_source_urls):
    """Test URL scraping failure."""
    # Mock failed response
    mock_get.side_effect = Exception("Connection error")
    
    scraper = MutualFundScraper(source_urls_file=sample_source_urls, retry_attempts=1)
    result = scraper.scrape_url("https://example.com/test", "Test AMC")
    
    assert result is None


def test_save_scraped_content(sample_source_urls, tmp_path):
    """Test saving scraped content."""
    scraper = MutualFundScraper(source_urls_file=sample_source_urls)
    
    content = [
        {
            "url": "https://example.com/test",
            "amc_name": "Test AMC",
            "content": "Test content"
        }
    ]
    
    output_file = tmp_path / "scraped_content.json"
    scraper.save_scraped_content(content, str(output_file))
    
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        saved_data = json.load(f)
    
    assert "scraped_content" in saved_data
    assert len(saved_data["scraped_content"]) == 1

