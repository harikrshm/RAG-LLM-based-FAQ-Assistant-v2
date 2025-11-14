"""
Unit tests for the source_tracker module
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from source_tracker import SourceURLTracker


@pytest.fixture
def tracker(tmp_path):
    """Create a source tracker with temporary storage."""
    storage_file = tmp_path / "source_tracking.json"
    return SourceURLTracker(storage_file=str(storage_file))


def test_tracker_initialization(tracker):
    """Test tracker initialization."""
    assert tracker.sources == {}
    assert tracker.url_to_id == {}
    assert tracker.content_to_sources == {}


def test_add_source(tracker):
    """Test adding a source."""
    url = "https://groww.in/mutual-funds/test-fund"
    source_id = tracker.add_source(
        url=url,
        amc_name="Test AMC",
        title="Test Fund",
        source_type="groww",
    )

    assert source_id in tracker.sources
    assert tracker.sources[source_id]["url"] == url
    assert tracker.sources[source_id]["amc_name"] == "Test AMC"
    assert tracker.url_to_id[url] == source_id


def test_add_duplicate_source(tracker):
    """Test adding duplicate source."""
    url = "https://groww.in/mutual-funds/test-fund"
    
    source_id1 = tracker.add_source(url=url, amc_name="Test AMC")
    source_id2 = tracker.add_source(url=url, amc_name="Test AMC")
    
    assert source_id1 == source_id2
    assert len(tracker.sources) == 1


def test_link_content_to_source(tracker):
    """Test linking content to source."""
    url = "https://groww.in/mutual-funds/test-fund"
    source_id = tracker.add_source(url=url, amc_name="Test AMC")
    
    content_id = "content_123"
    tracker.link_content_to_source(content_id, url)
    
    assert content_id in tracker.content_to_sources
    assert source_id in tracker.content_to_sources[content_id]


def test_get_source_by_url(tracker):
    """Test getting source by URL."""
    url = "https://groww.in/mutual-funds/test-fund"
    tracker.add_source(url=url, amc_name="Test AMC", title="Test Fund")
    
    source = tracker.get_source_by_url(url)
    
    assert source is not None
    assert source["url"] == url
    assert source["title"] == "Test Fund"


def test_get_sources_for_content(tracker):
    """Test getting sources for content."""
    url1 = "https://groww.in/mutual-funds/test-fund-1"
    url2 = "https://groww.in/mutual-funds/test-fund-2"
    
    tracker.add_source(url=url1, amc_name="Test AMC")
    tracker.add_source(url=url2, amc_name="Test AMC")
    
    content_id = "content_123"
    tracker.link_content_to_source(content_id, url1)
    tracker.link_content_to_source(content_id, url2)
    
    sources = tracker.get_sources_for_content(content_id)
    
    assert len(sources) == 2
    assert any(s["url"] == url1 for s in sources)
    assert any(s["url"] == url2 for s in sources)


@patch("source_tracker.requests.head")
def test_validate_source_success(mock_head, tracker):
    """Test successful source validation."""
    url = "https://groww.in/mutual-funds/test-fund"
    source_id = tracker.add_source(url=url, amc_name="Test AMC")
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_head.return_value = mock_response
    
    is_accessible = tracker.validate_source(source_id)
    
    assert is_accessible is True
    assert tracker.sources[source_id]["validated"] is True
    assert tracker.sources[source_id]["is_accessible"] is True


@patch("source_tracker.requests.head")
def test_validate_source_failure(mock_head, tracker):
    """Test failed source validation."""
    url = "https://groww.in/mutual-funds/test-fund"
    source_id = tracker.add_source(url=url, amc_name="Test AMC")
    
    # Mock failed response
    mock_head.side_effect = Exception("Connection error")
    
    is_accessible = tracker.validate_source(source_id)
    
    assert is_accessible is False
    assert tracker.sources[source_id]["validated"] is True
    assert tracker.sources[source_id]["is_accessible"] is False


def test_get_sources_by_amc(tracker):
    """Test getting sources by AMC."""
    tracker.add_source(url="https://example.com/fund1", amc_name="AMC 1")
    tracker.add_source(url="https://example.com/fund2", amc_name="AMC 1")
    tracker.add_source(url="https://example.com/fund3", amc_name="AMC 2")
    
    amc1_sources = tracker.get_sources_by_amc("AMC 1")
    
    assert len(amc1_sources) == 2
    assert all(s["amc_name"] == "AMC 1" for s in amc1_sources)


def test_get_statistics(tracker):
    """Test getting statistics."""
    tracker.add_source(url="https://example.com/fund1", amc_name="AMC 1", source_type="groww")
    tracker.add_source(url="https://example.com/fund2", amc_name="AMC 2", source_type="groww")
    
    stats = tracker.get_statistics()
    
    assert stats["total_sources"] == 2
    assert stats["unique_amcs"] == 2
    assert stats["sources_by_type"]["groww"] == 2


def test_save_and_load_tracking_data(tmp_path):
    """Test saving and loading tracking data."""
    storage_file = tmp_path / "source_tracking.json"
    
    # Create tracker and add source
    tracker1 = SourceURLTracker(storage_file=str(storage_file))
    url = "https://example.com/fund1"
    tracker1.add_source(url=url, amc_name="Test AMC")
    tracker1.save_tracking_data()
    
    # Load in new tracker instance
    tracker2 = SourceURLTracker(storage_file=str(storage_file))
    
    assert len(tracker2.sources) == 1
    assert tracker2.get_source_by_url(url) is not None

