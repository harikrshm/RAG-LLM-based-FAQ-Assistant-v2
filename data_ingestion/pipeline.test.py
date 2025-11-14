"""
Unit tests for the pipeline module
"""

import pytest
import os
import shutil
from pipeline import IngestionPipeline


TEST_OUTPUT_DIR = "test_pipeline_output"
TEST_VECTORDB_DIR = "test_pipeline_vectordb"


@pytest.fixture
def pipeline():
    """Create a test ingestion pipeline."""
    # Clean up any existing test directories
    for dir_path in [TEST_OUTPUT_DIR, TEST_VECTORDB_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    # Create test pipeline
    pipeline = IngestionPipeline(
        source_urls_file="data/source_urls.json",
        output_dir=TEST_OUTPUT_DIR,
        vectordb_dir=TEST_VECTORDB_DIR,
        collection_name="test_collection",
    )

    yield pipeline

    # Cleanup after tests
    for dir_path in [TEST_OUTPUT_DIR, TEST_VECTORDB_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


def test_pipeline_initialization(pipeline):
    """Test pipeline initialization."""
    assert pipeline.source_urls_file == "data/source_urls.json"
    assert pipeline.output_dir == TEST_OUTPUT_DIR
    assert pipeline.vectordb_dir == TEST_VECTORDB_DIR
    assert pipeline.collection_name == "test_collection"

    # Check components are initialized
    assert pipeline.scraper is not None
    assert pipeline.processor is not None
    assert pipeline.chunker is not None
    assert pipeline.embedder is not None
    assert pipeline.vectordb is not None
    assert pipeline.metadata_manager is not None
    assert pipeline.groww_mapper is not None


def test_pipeline_stats_initialization(pipeline):
    """Test that pipeline statistics are initialized correctly."""
    stats = pipeline.stats

    assert stats["start_time"] is None
    assert stats["end_time"] is None
    assert stats["duration_seconds"] == 0
    assert stats["urls_processed"] == 0
    assert stats["documents_scraped"] == 0
    assert stats["documents_processed"] == 0
    assert stats["chunks_created"] == 0
    assert stats["chunks_embedded"] == 0
    assert stats["chunks_stored"] == 0
    assert stats["chunks_mapped_to_groww"] == 0
    assert stats["errors"] == []


def test_load_scraped_data(pipeline):
    """Test loading previously scraped data."""
    # Create mock scraped data
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    mock_data = {
        "scraped_content": [
            {
                "url": "https://example.com",
                "content": "Test content",
                "amc_name": "Test AMC",
            }
        ]
    }

    import json

    with open(os.path.join(TEST_OUTPUT_DIR, "scraped_content.json"), "w") as f:
        json.dump(mock_data, f)

    # Load data
    scraped_data = pipeline._load_scraped_data()

    assert len(scraped_data) == 1
    assert scraped_data[0]["url"] == "https://example.com"


def test_process_documents(pipeline):
    """Test document processing."""
    scraped_data = [
        {
            "url": "https://example.com",
            "content": "<html><body><p>This is test content about expense ratio of 1.5%</p></body></html>",
            "amc_name": "Test AMC",
            "amc_id": "test",
            "title": "Test Fund",
            "scraped_at": "2025-11-14",
        }
    ]

    processed_docs = pipeline._process_documents(scraped_data)

    assert len(processed_docs) > 0
    assert "content" in processed_docs[0]
    assert "structured_info" in processed_docs[0]


def test_create_chunks(pipeline):
    """Test chunk creation."""
    processed_docs = [
        {
            "content": "This is a test document. " * 50,  # Long enough to create multiple chunks
            "metadata": {
                "url": "https://example.com",
                "amc_name": "Test AMC",
            },
        }
    ]

    chunks = pipeline._create_chunks(processed_docs)

    assert len(chunks) > 0
    # Chunks should be TextChunk objects with required attributes
    assert hasattr(chunks[0], "content")
    assert hasattr(chunks[0], "chunk_id")
    assert hasattr(chunks[0], "source_url")


def test_generate_embeddings(pipeline):
    """Test embedding generation."""
    from chunker import TextChunk

    # Create mock chunks
    chunks = [
        TextChunk(
            content="This is test content about mutual funds",
            chunk_id="test-1",
            source_url="https://example.com",
            chunk_index=0,
            metadata={"amc_name": "Test AMC"},
        )
    ]

    chunks_with_embeddings = pipeline._generate_embeddings(chunks)

    assert len(chunks_with_embeddings) > 0
    assert "embedding" in chunks_with_embeddings[0]
    assert "embedding_model" in chunks_with_embeddings[0]


def test_map_to_groww(pipeline):
    """Test Groww mapping."""
    chunks = [
        {
            "chunk_id": "test-1",
            "content": "Expense ratio is 1.5%",
            "source_url": "https://groww.in/mutual-funds/hdfc-equity",
            "chunk_index": 0,
            "metadata": {"amc_name": "HDFC Mutual Fund"},
        }
    ]

    chunks_with_mappings = pipeline._map_to_groww(chunks)

    assert len(chunks_with_mappings) > 0
    assert "groww_page_url" in chunks_with_mappings[0]


def test_save_outputs(pipeline):
    """Test saving outputs."""
    scraped_data = [{"url": "https://example.com", "content": "Test"}]
    processed_docs = [{"content": "Processed test", "metadata": {}}]
    chunks_with_embeddings = [
        {
            "chunk_id": "test-1",
            "content": "Test chunk",
            "embedding": [0.1] * 384,
        }
    ]
    chunks_with_mappings = [
        {
            "chunk_id": "test-1",
            "content": "Test chunk",
            "embedding": [0.1] * 384,
            "groww_page_url": None,
        }
    ]

    pipeline._save_outputs(
        scraped_data, processed_docs, chunks_with_embeddings, chunks_with_mappings
    )

    # Check that files were created
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "scraped_content.json"))
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "processed_content.json"))
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "chunks_with_embeddings.json"))
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "chunks_final.json"))


def test_output_directory_creation(pipeline):
    """Test that output directory is created."""
    assert os.path.exists(TEST_OUTPUT_DIR)


def test_pipeline_components_integration(pipeline):
    """Test that all pipeline components are properly integrated."""
    # Check that components can access each other's outputs
    assert pipeline.scraper is not None
    assert pipeline.processor is not None
    assert pipeline.chunker is not None
    assert pipeline.embedder is not None
    assert pipeline.vectordb is not None
    assert pipeline.metadata_manager is not None
    assert pipeline.groww_mapper is not None

    # Check that components have correct configuration
    assert pipeline.chunker.chunk_size == 500
    assert pipeline.chunker.chunk_overlap == 50
    assert pipeline.embedder.model_name == "all-MiniLM-L6-v2"


def test_statistics_tracking(pipeline):
    """Test that statistics are tracked correctly."""
    # Initially all zeros
    assert pipeline.stats["documents_scraped"] == 0
    assert pipeline.stats["chunks_created"] == 0

    # After setting values
    pipeline.stats["documents_scraped"] = 5
    pipeline.stats["chunks_created"] = 50

    assert pipeline.stats["documents_scraped"] == 5
    assert pipeline.stats["chunks_created"] == 50


def test_error_tracking(pipeline):
    """Test error tracking in statistics."""
    assert len(pipeline.stats["errors"]) == 0

    # Add error
    pipeline.stats["errors"].append("Test error")

    assert len(pipeline.stats["errors"]) == 1
    assert pipeline.stats["errors"][0] == "Test error"

