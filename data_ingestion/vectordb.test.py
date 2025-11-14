"""
Unit tests for the vectordb module
"""

import pytest
import os
import shutil
from vectordb import VectorDatabase


# Test database directory
TEST_DB_DIR = "./test_vectordb"


@pytest.fixture
def vectordb():
    """Create a test vector database."""
    # Clean up any existing test database
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

    # Create test database
    db = VectorDatabase(persist_directory=TEST_DB_DIR, collection_name="test_collection")

    yield db

    # Cleanup after tests
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)


def test_vectordb_initialization(vectordb):
    """Test vector database initialization."""
    assert vectordb.persist_directory == TEST_DB_DIR
    assert vectordb.collection_name == "test_collection"
    assert vectordb.collection is not None


def test_add_chunks(vectordb):
    """Test adding chunks to the database."""
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "This is a test chunk about expense ratio",
            "embedding": [0.1] * 384,  # Dummy embedding
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {
                "amc_name": "Test AMC",
                "title": "Test Fund",
            },
        },
        {
            "chunk_id": "test-2",
            "content": "This is another test chunk about minimum SIP",
            "embedding": [0.2] * 384,
            "source_url": "https://example.com/2",
            "chunk_index": 1,
            "metadata": {
                "amc_name": "Test AMC",
                "title": "Test Fund 2",
            },
        },
    ]

    vectordb.add_chunks(chunks)

    # Check count
    count = vectordb.count()
    assert count == 2


def test_query_by_text(vectordb):
    """Test querying by text."""
    # Add test data
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "The expense ratio of the fund is 1.5%",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "Test AMC"},
        },
    ]
    vectordb.add_chunks(chunks)

    # Query
    results = vectordb.query(query_text="What is the expense ratio?", n_results=1)

    assert "documents" in results
    assert len(results["documents"][0]) == 1


def test_query_by_embedding(vectordb):
    """Test querying by embedding."""
    # Add test data
    query_embedding = [0.15] * 384
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "Test content",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "Test AMC"},
        },
    ]
    vectordb.add_chunks(chunks)

    # Query with embedding
    results = vectordb.query(
        query_text="dummy",  # Text is required but not used
        query_embedding=query_embedding,
        n_results=1,
    )

    assert "documents" in results
    assert len(results["documents"][0]) == 1


def test_get_by_id(vectordb):
    """Test retrieving chunks by ID."""
    chunks = [
        {
            "chunk_id": "test-123",
            "content": "Test content",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "Test AMC"},
        },
    ]
    vectordb.add_chunks(chunks)

    # Get by ID
    results = vectordb.get_by_id(["test-123"])

    assert "documents" in results
    assert len(results["documents"]) == 1
    assert results["documents"][0] == "Test content"


def test_filter_by_metadata(vectordb):
    """Test filtering by metadata."""
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "HDFC fund content",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "HDFC"},
        },
        {
            "chunk_id": "test-2",
            "content": "SBI fund content",
            "embedding": [0.2] * 384,
            "source_url": "https://example.com/2",
            "chunk_index": 0,
            "metadata": {"amc_name": "SBI"},
        },
    ]
    vectordb.add_chunks(chunks)

    # Filter by AMC
    results = vectordb.filter_by_metadata({"amc_name": "HDFC"})

    assert "documents" in results
    assert len(results["documents"]) == 1
    assert "HDFC" in results["documents"][0]


def test_count(vectordb):
    """Test counting chunks."""
    initial_count = vectordb.count()
    assert initial_count == 0

    # Add chunks
    chunks = [
        {
            "chunk_id": f"test-{i}",
            "content": f"Test content {i}",
            "embedding": [0.1 * i] * 384,
            "source_url": f"https://example.com/{i}",
            "chunk_index": i,
            "metadata": {"amc_name": "Test AMC"},
        }
        for i in range(5)
    ]
    vectordb.add_chunks(chunks)

    count = vectordb.count()
    assert count == 5


def test_get_collection_info(vectordb):
    """Test getting collection info."""
    info = vectordb.get_collection_info()

    assert "name" in info
    assert "count" in info
    assert "persist_directory" in info
    assert info["name"] == "test_collection"


def test_reset(vectordb):
    """Test resetting the database."""
    # Add some data
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "Test content",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "Test AMC"},
        },
    ]
    vectordb.add_chunks(chunks)

    assert vectordb.count() == 1

    # Reset
    vectordb.reset()

    # Check count is zero
    assert vectordb.count() == 0


def test_metadata_preparation(vectordb):
    """Test metadata preparation for ChromaDB."""
    chunk = {
        "chunk_id": "test-1",
        "content": "Test content",
        "source_url": "https://example.com",
        "chunk_index": 5,
        "metadata": {
            "amc_name": "HDFC",
            "amc_id": "hdfc",
            "title": "Test Fund",
            "structured_info": {
                "expense_ratio": "1.5%",
                "minimum_sip": "500",
            },
        },
    }

    metadata = vectordb._prepare_metadata(chunk)

    assert "source_url" in metadata
    assert "chunk_index" in metadata
    assert "amc_name" in metadata
    assert "amc_id" in metadata
    assert "title" in metadata
    assert "structured_info_json" in metadata
    assert metadata["chunk_index"] == 5


def test_batch_addition(vectordb):
    """Test adding chunks in batches."""
    # Create 150 chunks to test batch processing
    chunks = [
        {
            "chunk_id": f"test-{i}",
            "content": f"Test content {i}",
            "embedding": [0.01 * i] * 384,
            "source_url": f"https://example.com/{i}",
            "chunk_index": i,
            "metadata": {"amc_name": "Test AMC"},
        }
        for i in range(150)
    ]

    vectordb.add_chunks(chunks)

    count = vectordb.count()
    assert count == 150


def test_query_with_filters(vectordb):
    """Test querying with metadata filters."""
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "HDFC fund with high returns",
            "embedding": [0.1] * 384,
            "source_url": "https://example.com/1",
            "chunk_index": 0,
            "metadata": {"amc_name": "HDFC"},
        },
        {
            "chunk_id": "test-2",
            "content": "SBI fund with moderate returns",
            "embedding": [0.2] * 384,
            "source_url": "https://example.com/2",
            "chunk_index": 0,
            "metadata": {"amc_name": "SBI"},
        },
    ]
    vectordb.add_chunks(chunks)

    # Query with filter
    results = vectordb.query(
        query_text="fund returns",
        n_results=5,
        where={"amc_name": "HDFC"},
    )

    assert len(results["documents"][0]) == 1
    assert "HDFC" in results["metadatas"][0][0]["amc_name"]

