"""
Unit tests for the validator module
"""

import pytest
from validator import DataValidator


@pytest.fixture
def validator():
    """Create a data validator."""
    return DataValidator(
        min_content_length=50,
        max_content_length=100000,
        duplicate_threshold=0.9,
    )


def test_validator_initialization(validator):
    """Test validator initialization."""
    assert validator.min_content_length == 50
    assert validator.max_content_length == 100000
    assert validator.duplicate_threshold == 0.9


def test_validate_required_fields(validator):
    """Test required fields validation."""
    item = {"url": "https://example.com", "content": "Test"}
    assert validator._validate_required_fields(item, ["url", "content"]) is True

    item = {"url": "https://example.com"}
    assert validator._validate_required_fields(item, ["url", "content"]) is False


def test_validate_url(validator):
    """Test URL validation."""
    # Valid URLs
    assert validator._validate_url("https://example.com") is True
    assert validator._validate_url("http://groww.in/mutual-funds") is True

    # Invalid URLs
    assert validator._validate_url("not-a-url") is False
    assert validator._validate_url("") is False
    assert validator._validate_url(None) is False


def test_validate_content_length(validator):
    """Test content length validation."""
    # Valid content
    assert validator._validate_content_length("a" * 100) is True

    # Too short
    assert validator._validate_content_length("short") is False

    # Too long
    assert validator._validate_content_length("a" * 200000) is False


def test_is_low_quality_content(validator):
    """Test low quality content detection."""
    # Good quality
    assert validator._is_low_quality_content("This is good quality content with variety") is False

    # Empty
    assert validator._is_low_quality_content("") is True

    # Mostly whitespace
    assert validator._is_low_quality_content("   \n\n   \n  ") is True

    # Very repetitive
    assert validator._is_low_quality_content("test " * 100) is True


def test_compute_content_hash(validator):
    """Test content hash computation."""
    content1 = "This is test content"
    content2 = "This is test content"
    content3 = "Different content"

    hash1 = validator._compute_content_hash(content1)
    hash2 = validator._compute_content_hash(content2)
    hash3 = validator._compute_content_hash(content3)

    # Same content should have same hash
    assert hash1 == hash2

    # Different content should have different hash
    assert hash1 != hash3


def test_detect_duplicates(validator):
    """Test duplicate detection."""
    documents = [
        {"url": "https://example.com/1", "content": "Test content one"},
        {"url": "https://example.com/2", "content": "Test content two"},
        {"url": "https://example.com/3", "content": "Test content one"},  # Duplicate
    ]

    duplicates = validator._detect_duplicates(documents)

    assert len(duplicates) == 1
    assert duplicates[0] == (0, 2)


def test_validate_scraped_data(validator):
    """Test scraped data validation."""
    scraped_data = [
        {
            "url": "https://example.com",
            "content": "This is valid content with sufficient length to pass validation",
            "amc_name": "Test AMC",
        },
        {
            "url": "https://example.com/2",
            "content": "Short",  # Too short
            "amc_name": "Test AMC",
        },
    ]

    results = validator.validate_scraped_data(scraped_data)

    assert results["total_documents"] == 2
    assert len(results["issues"]) > 0


def test_validate_processed_documents(validator):
    """Test processed documents validation."""
    processed_docs = [
        {
            "content": "This is processed content with sufficient length",
            "metadata": {"url": "https://example.com"},
            "structured_info": {"expense_ratio": "1.5%"},
        },
        {
            "content": "Short",  # Insufficient content
            "metadata": {},
        },
    ]

    results = validator.validate_processed_documents(processed_docs)

    assert results["total_documents"] == 2
    assert len(results["issues"]) > 0


def test_validate_chunks(validator):
    """Test chunks validation."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "content": "This is a valid chunk with sufficient content",
            "source_url": "https://example.com",
        },
        {
            "chunk_id": "chunk-2",
            "content": "",  # Empty content
            "source_url": "https://example.com",
        },
    ]

    results = validator.validate_chunks(chunks)

    assert results["total_chunks"] == 2
    assert len(results["issues"]) > 0


def test_validate_embeddings(validator):
    """Test embeddings validation."""
    chunks_with_embeddings = [
        {
            "chunk_id": "chunk-1",
            "content": "Test",
            "embedding": [0.1, 0.2, 0.3] * 128,  # Valid embedding
        },
        {
            "chunk_id": "chunk-2",
            "content": "Test",
            "embedding": [0.0] * 384,  # All zeros
        },
        {
            "chunk_id": "chunk-3",
            "content": "Test",
            # Missing embedding
        },
    ]

    results = validator.validate_embeddings(chunks_with_embeddings)

    assert results["total_chunks"] == 3
    assert len(results["issues"]) >= 2


def test_validate_metadata(validator):
    """Test metadata validation."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "content": "Test",
            "source_url": "https://example.com",
            "metadata": {"amc_name": "Test AMC"},
        },
        {
            "chunk_id": "chunk-2",
            "content": "Test",
            "source_url": "https://example.com/2",
            "metadata": {},  # No AMC name
        },
        {
            "chunk_id": "chunk-3",
            "content": "Test",
            # No source URL
            "metadata": {"amc_name": "Test AMC 2"},
        },
    ]

    results = validator.validate_metadata(chunks)

    assert results["total_chunks"] == 3
    assert results["unique_sources"] >= 1
    assert results["unique_amcs"] >= 1
    assert len(results["issues"]) > 0


def test_validate_source_urls(validator):
    """Test source URLs validation."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "source_url": "https://example.com",
            "content": "Test",
        },
        {
            "chunk_id": "chunk-2",
            "source_url": "invalid-url",
            "content": "Test",
        },
        {
            "chunk_id": "chunk-3",
            "source_url": None,
            "content": "Test",
        },
    ]

    results = validator.validate_source_urls(chunks)

    assert results["total_chunks"] == 3
    assert len(results["issues"]) >= 2


def test_validate_groww_mappings(validator):
    """Test Groww mappings validation."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "source_url": "https://groww.in/mutual-funds/fund1",
            "groww_page_url": "https://groww.in/mutual-funds/fund1",
            "content": "Test",
        },
        {
            "chunk_id": "chunk-2",
            "source_url": "https://external.com",
            "groww_page_url": None,
            "content": "Test",
        },
        {
            "chunk_id": "chunk-3",
            "source_url": "https://example.com",
            "groww_page_url": "invalid-url",
            "content": "Test",
        },
    ]

    results = validator.validate_groww_mappings(chunks)

    assert results["total_chunks"] == 3
    assert results["chunks_with_mapping"] >= 1
    assert results["chunks_from_groww_source"] >= 1


def test_detect_duplicate_chunks(validator):
    """Test duplicate chunks detection."""
    chunks = [
        {
            "chunk_id": "chunk-1",
            "content": "This is unique content",
        },
        {
            "chunk_id": "chunk-2",
            "content": "This is unique content",  # Duplicate
        },
        {
            "chunk_id": "chunk-3",
            "content": "This is different content",
        },
    ]

    duplicates = validator._detect_duplicate_chunks(chunks)

    assert len(duplicates) == 1
    assert duplicates[0][0] == "chunk-1"
    assert duplicates[0][1] == "chunk-2"


def test_run_full_validation(validator):
    """Test full validation pipeline."""
    scraped_data = [
        {
            "url": "https://example.com",
            "content": "Valid scraped content with sufficient length",
        }
    ]

    processed_docs = [
        {
            "content": "Valid processed content",
            "metadata": {"url": "https://example.com"},
        }
    ]

    chunks = [
        {
            "chunk_id": "chunk-1",
            "content": "Valid chunk content",
            "source_url": "https://example.com",
            "metadata": {"amc_name": "Test AMC"},
            "embedding": [0.1] * 384,
            "groww_page_url": "https://groww.in/mutual-funds/test",
        }
    ]

    results = validator.run_full_validation(
        scraped_data=scraped_data,
        processed_docs=processed_docs,
        chunks=chunks,
        chunks_with_embeddings=chunks,
    )

    assert "scraped_data" in results
    assert "processed_docs" in results
    assert "chunks" in results
    assert "metadata" in results
    assert "embeddings" in results
    assert "groww_mappings" in results


def test_validation_results_structure(validator):
    """Test validation results structure."""
    assert "total_items_validated" in validator.validation_results
    assert "passed_validations" in validator.validation_results
    assert "failed_validations" in validator.validation_results
    assert "warnings" in validator.validation_results
    assert "errors" in validator.validation_results

