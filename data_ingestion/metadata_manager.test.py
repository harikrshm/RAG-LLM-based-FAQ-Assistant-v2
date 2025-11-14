"""
Unit tests for the metadata_manager module
"""

import pytest
import os
import json
from metadata_manager import MetadataManager, ContentType


TEST_METADATA_FILE = "test_metadata_index.json"


@pytest.fixture
def manager():
    """Create a test metadata manager."""
    # Clean up any existing test file
    if os.path.exists(TEST_METADATA_FILE):
        os.remove(TEST_METADATA_FILE)

    mgr = MetadataManager(metadata_file=TEST_METADATA_FILE)

    yield mgr

    # Cleanup after tests
    if os.path.exists(TEST_METADATA_FILE):
        os.remove(TEST_METADATA_FILE)


def test_manager_initialization(manager):
    """Test metadata manager initialization."""
    assert manager.metadata_file == TEST_METADATA_FILE
    assert manager.source_registry == {}
    assert manager.chunk_registry == {}


def test_register_source(manager):
    """Test registering a source."""
    source_metadata = {
        "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
        "amc_name": "HDFC Mutual Fund",
        "amc_id": "hdfc",
        "title": "HDFC Mutual Funds",
    }

    manager.register_source(source_metadata)

    assert len(manager.source_registry) == 1
    assert "https://groww.in/mutual-funds/amc/hdfc-mutual-funds" in manager.source_registry


def test_register_chunk(manager):
    """Test registering a chunk."""
    chunk = {
        "chunk_id": "test-chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 0,
        "content": "This is test content",
        "metadata": {
            "amc_name": "HDFC Mutual Fund",
            "amc_id": "hdfc",
            "title": "Test Fund",
        },
    }

    manager.register_chunk(chunk)

    assert len(manager.chunk_registry) == 1
    assert "test-chunk-1" in manager.chunk_registry


def test_url_to_chunks_mapping(manager):
    """Test URL to chunks mapping."""
    chunk1 = {
        "chunk_id": "chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 0,
        "content": "Content 1",
        "metadata": {},
    }

    chunk2 = {
        "chunk_id": "chunk-2",
        "source_url": "https://example.com",
        "chunk_index": 1,
        "content": "Content 2",
        "metadata": {},
    }

    manager.register_chunk(chunk1)
    manager.register_chunk(chunk2)

    chunks = manager.get_chunks_by_url("https://example.com")
    assert len(chunks) == 2
    assert "chunk-1" in chunks
    assert "chunk-2" in chunks


def test_amc_to_chunks_mapping(manager):
    """Test AMC to chunks mapping."""
    chunk1 = {
        "chunk_id": "chunk-1",
        "source_url": "https://example.com/1",
        "chunk_index": 0,
        "content": "Content 1",
        "metadata": {"amc_name": "HDFC"},
    }

    chunk2 = {
        "chunk_id": "chunk-2",
        "source_url": "https://example.com/2",
        "chunk_index": 0,
        "content": "Content 2",
        "metadata": {"amc_name": "HDFC"},
    }

    manager.register_chunk(chunk1)
    manager.register_chunk(chunk2)

    chunks = manager.get_chunks_by_amc("HDFC")
    assert len(chunks) == 2
    assert "chunk-1" in chunks
    assert "chunk-2" in chunks


def test_register_groww_mapping(manager):
    """Test registering Groww page mapping."""
    chunk = {
        "chunk_id": "test-chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 0,
        "content": "Test content",
        "metadata": {},
    }

    manager.register_chunk(chunk)
    manager.register_groww_mapping("test-chunk-1", "https://groww.in/mutual-funds/hdfc-equity")

    chunk_meta = manager.get_chunk_metadata("test-chunk-1")
    assert chunk_meta["groww_page_url"] == "https://groww.in/mutual-funds/hdfc-equity"


def test_get_source_metadata(manager):
    """Test getting source metadata."""
    source_metadata = {
        "url": "https://example.com",
        "amc_name": "Test AMC",
        "title": "Test Fund",
    }

    manager.register_source(source_metadata)

    retrieved = manager.get_source_metadata("https://example.com")
    assert retrieved is not None
    assert retrieved["amc_name"] == "Test AMC"


def test_get_chunk_metadata(manager):
    """Test getting chunk metadata."""
    chunk = {
        "chunk_id": "test-chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 5,
        "content": "Test content",
        "metadata": {"amc_name": "Test AMC"},
    }

    manager.register_chunk(chunk)

    retrieved = manager.get_chunk_metadata("test-chunk-1")
    assert retrieved is not None
    assert retrieved["chunk_index"] == 5
    assert retrieved["amc_name"] == "Test AMC"


def test_save_and_load_metadata(manager):
    """Test saving and loading metadata."""
    # Register some data
    source = {
        "url": "https://example.com",
        "amc_name": "Test AMC",
    }
    manager.register_source(source)

    chunk = {
        "chunk_id": "test-chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 0,
        "content": "Test",
        "metadata": {},
    }
    manager.register_chunk(chunk)

    # Save
    manager.save_metadata()

    # Create new manager and load
    new_manager = MetadataManager(metadata_file=TEST_METADATA_FILE)

    assert len(new_manager.source_registry) == 1
    assert len(new_manager.chunk_registry) == 1


def test_get_statistics(manager):
    """Test getting statistics."""
    # Register sources and chunks
    for i in range(3):
        source = {
            "url": f"https://example.com/{i}",
            "amc_name": f"AMC {i}",
        }
        manager.register_source(source)

        for j in range(2):
            chunk = {
                "chunk_id": f"chunk-{i}-{j}",
                "source_url": f"https://example.com/{i}",
                "chunk_index": j,
                "content": "Test",
                "metadata": {"amc_name": f"AMC {i}"},
            }
            manager.register_chunk(chunk)

    stats = manager.get_statistics()

    assert stats["total_sources"] == 3
    assert stats["total_chunks"] == 6
    assert stats["total_amcs"] == 3
    assert stats["avg_chunks_per_source"] == 2.0


def test_determine_content_type(manager):
    """Test content type determination."""
    # AMC page
    amc_url = "https://groww.in/mutual-funds/amc/hdfc-mutual-funds"
    content_type = manager._determine_content_type(amc_url, {})
    assert content_type == ContentType.AMC_PAGE.value

    # Fund page
    fund_url = "https://groww.in/mutual-funds/hdfc-equity-fund"
    content_type = manager._determine_content_type(fund_url, {})
    assert content_type == ContentType.FUND_PAGE.value

    # Comparison page
    comp_url = "https://groww.in/mutual-funds/top/best-hdfc-funds"
    content_type = manager._determine_content_type(comp_url, {})
    assert content_type == ContentType.COMPARISON_PAGE.value

    # Blog post
    blog_url = "https://groww.in/blog/best-mutual-funds"
    content_type = manager._determine_content_type(blog_url, {})
    assert content_type == ContentType.BLOG_POST.value


def test_extract_domain(manager):
    """Test domain extraction."""
    url = "https://groww.in/mutual-funds/hdfc-equity"
    domain = manager._extract_domain(url)
    assert domain == "groww.in"


def test_validate_metadata(manager):
    """Test metadata validation."""
    # Register a valid source and chunk
    source = {
        "url": "https://example.com",
        "amc_name": "Test AMC",
    }
    manager.register_source(source)

    chunk = {
        "chunk_id": "chunk-1",
        "source_url": "https://example.com",
        "chunk_index": 0,
        "content": "Test",
        "metadata": {"amc_name": "Test AMC"},
    }
    manager.register_chunk(chunk)

    validation = manager.validate_metadata()
    assert validation["valid"] is True
    assert validation["total_issues"] == 0


def test_validate_metadata_with_orphaned_chunk(manager):
    """Test validation with orphaned chunk."""
    # Register a chunk without registering its source
    chunk = {
        "chunk_id": "orphan-chunk",
        "source_url": "https://missing.com",
        "chunk_index": 0,
        "content": "Test",
        "metadata": {},
    }
    manager.register_chunk(chunk)

    validation = manager.validate_metadata()
    assert validation["valid"] is False
    assert validation["total_issues"] > 0


def test_get_all_sources(manager):
    """Test getting all sources."""
    for i in range(3):
        source = {
            "url": f"https://example.com/{i}",
            "amc_name": f"AMC {i}",
        }
        manager.register_source(source)

    sources = manager.get_all_sources()
    assert len(sources) == 3


def test_get_all_chunks(manager):
    """Test getting all chunks."""
    for i in range(5):
        chunk = {
            "chunk_id": f"chunk-{i}",
            "source_url": "https://example.com",
            "chunk_index": i,
            "content": "Test",
            "metadata": {},
        }
        manager.register_chunk(chunk)

    chunks = manager.get_all_chunks()
    assert len(chunks) == 5

