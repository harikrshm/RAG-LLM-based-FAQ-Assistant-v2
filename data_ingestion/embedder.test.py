"""
Unit tests for the embedder module
"""

import pytest
import numpy as np
from embedder import EmbeddingGenerator


@pytest.fixture
def embedder():
    """Create an embedding generator."""
    # Use a small model for testing
    return EmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",
        batch_size=8,
        normalize_embeddings=True,
    )


def test_embedder_initialization(embedder):
    """Test embedder initialization."""
    assert embedder.model_name == "all-MiniLM-L6-v2"
    assert embedder.batch_size == 8
    assert embedder.normalize_embeddings is True
    assert embedder.embedding_dimension > 0


def test_generate_single_embedding(embedder):
    """Test generating a single embedding."""
    text = "This is a test sentence about mutual funds."
    embedding = embedder.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == embedder.embedding_dimension
    assert not np.isnan(embedding).any()


def test_generate_batch_embeddings(embedder):
    """Test generating batch embeddings."""
    texts = [
        "Expense ratio is 1.5%",
        "Minimum SIP amount is Rs. 500",
        "This is an equity fund",
    ]
    
    embeddings = embedder.generate_embeddings_batch(texts)
    
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] == embedder.embedding_dimension
    assert not np.isnan(embeddings).any()


def test_embedding_normalization(embedder):
    """Test that embeddings are normalized."""
    text = "Test normalization"
    embedding = embedder.generate_embedding(text)
    
    # Check that norm is approximately 1
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 0.01


def test_embed_chunks(embedder):
    """Test embedding multiple chunks."""
    chunks = [
        {
            "content": "HDFC Equity Fund has an expense ratio of 1.5%",
            "chunk_id": "chunk-1",
            "source_url": "https://example.com/1",
        },
        {
            "content": "Minimum SIP amount is Rs. 500 per month",
            "chunk_id": "chunk-2",
            "source_url": "https://example.com/2",
        },
    ]
    
    chunks_with_embeddings = embedder.embed_chunks(chunks)
    
    assert len(chunks_with_embeddings) == 2
    assert all("embedding" in chunk for chunk in chunks_with_embeddings)
    assert all("embedding_model" in chunk for chunk in chunks_with_embeddings)
    assert all("embedding_dimension" in chunk for chunk in chunks_with_embeddings)
    
    # Check embedding structure
    for chunk in chunks_with_embeddings:
        assert isinstance(chunk["embedding"], list)
        assert len(chunk["embedding"]) == embedder.embedding_dimension


def test_compute_similarity(embedder):
    """Test computing similarity between embeddings."""
    text1 = "Expense ratio of the fund"
    text2 = "The fund's expense ratio"
    text3 = "Minimum investment amount"
    
    emb1 = embedder.generate_embedding(text1)
    emb2 = embedder.generate_embedding(text2)
    emb3 = embedder.generate_embedding(text3)
    
    # Similar texts should have high similarity
    sim_high = embedder.compute_similarity(emb1, emb2)
    assert sim_high > 0.5
    
    # Different texts should have lower similarity
    sim_low = embedder.compute_similarity(emb1, emb3)
    assert sim_low < sim_high


def test_find_similar_chunks(embedder):
    """Test finding similar chunks."""
    chunks = [
        {
            "content": "The expense ratio is 1.5% per annum",
            "chunk_id": "chunk-1",
            "embedding": embedder.generate_embedding(
                "The expense ratio is 1.5% per annum"
            ).tolist(),
        },
        {
            "content": "Minimum SIP is Rs. 500",
            "chunk_id": "chunk-2",
            "embedding": embedder.generate_embedding("Minimum SIP is Rs. 500").tolist(),
        },
        {
            "content": "This is a large cap equity fund",
            "chunk_id": "chunk-3",
            "embedding": embedder.generate_embedding(
                "This is a large cap equity fund"
            ).tolist(),
        },
    ]
    
    query = "What is the expense ratio?"
    results = embedder.find_similar_chunks(query, chunks, top_k=2)
    
    assert len(results) == 2
    assert all("chunk" in result for result in results)
    assert all("similarity_score" in result for result in results)
    
    # The first result should be about expense ratio
    assert "expense ratio" in results[0]["chunk"]["content"].lower()
    
    # Scores should be in descending order
    assert results[0]["similarity_score"] >= results[1]["similarity_score"]


def test_get_model_info(embedder):
    """Test getting model information."""
    info = embedder.get_model_info()
    
    assert "model_name" in info
    assert "embedding_dimension" in info
    assert "batch_size" in info
    assert "normalize_embeddings" in info
    
    assert info["model_name"] == "all-MiniLM-L6-v2"
    assert info["embedding_dimension"] > 0


def test_embedding_consistency(embedder):
    """Test that same text produces same embedding."""
    text = "This is a test for consistency"
    
    emb1 = embedder.generate_embedding(text)
    emb2 = embedder.generate_embedding(text)
    
    # Should be very similar (allowing for minor floating point differences)
    similarity = embedder.compute_similarity(emb1, emb2)
    assert similarity > 0.99


def test_empty_text_embedding(embedder):
    """Test embedding empty text."""
    text = ""
    embedding = embedder.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == embedder.embedding_dimension


def test_long_text_embedding(embedder):
    """Test embedding very long text."""
    text = "This is a sentence. " * 100  # Very long text
    embedding = embedder.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == embedder.embedding_dimension


def test_special_characters_embedding(embedder):
    """Test embedding text with special characters."""
    text = "Expense ratio: 1.5% | Min. SIP: ₹500 | NAV: $50.25"
    embedding = embedder.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert not np.isnan(embedding).any()

