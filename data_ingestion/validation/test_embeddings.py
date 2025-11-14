"""
Test suite for validating vector embeddings generation.

This module tests that:
- Embeddings are generated for all chunks
- Embedding dimensions are consistent
- Embeddings contain valid values
- Similar content produces similar embeddings
- Embedding quality meets requirements
"""

import pytest
import json
import numpy as np
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from embedder import EmbeddingGenerator


@pytest.fixture
def embedder():
    """Create an embedding generator instance."""
    return EmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",
        batch_size=32,
        normalize_embeddings=True,
    )


@pytest.fixture
def sample_chunks_with_embeddings():
    """Load sample chunks with embeddings or create mock data."""
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("chunks", [])
    except FileNotFoundError:
        # Return mock data for testing
        embedder = EmbeddingGenerator()
        
        chunks = [
            {
                "chunk_id": "test-1",
                "content": "HDFC Equity Fund has an expense ratio of 1.5%",
                "source_url": "https://example.com/1",
            },
            {
                "chunk_id": "test-2",
                "content": "The fund's expense ratio is 1.5 percent",
                "source_url": "https://example.com/2",
            },
            {
                "chunk_id": "test-3",
                "content": "Minimum SIP amount is Rs. 500 per month",
                "source_url": "https://example.com/3",
            },
        ]
        
        return embedder.embed_chunks(chunks)


class TestEmbeddingPresence:
    """Test suite for embedding presence and structure."""

    def test_all_chunks_have_embeddings(self, sample_chunks_with_embeddings):
        """Test that all chunks have embeddings."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            assert "embedding" in chunk, f"Chunk {i} missing embedding field"
            
            embedding = chunk.get("embedding")
            assert embedding is not None, f"Chunk {i} has None embedding"
            assert len(embedding) > 0, f"Chunk {i} has empty embedding"

    def test_embedding_data_type(self, sample_chunks_with_embeddings):
        """Test that embeddings are in correct data type."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding")
            
            # Should be a list or array
            assert isinstance(embedding, (list, tuple, np.ndarray)), (
                f"Chunk {i} embedding has invalid type: {type(embedding)}"
            )
            
            # Each element should be numeric
            if len(embedding) > 0:
                assert isinstance(embedding[0], (int, float)), (
                    f"Chunk {i} embedding contains non-numeric values"
                )

    def test_embedding_metadata_present(self, sample_chunks_with_embeddings):
        """Test that embedding metadata is present."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            assert "embedding_model" in chunk, (
                f"Chunk {i} missing embedding_model metadata"
            )
            assert "embedding_dimension" in chunk, (
                f"Chunk {i} missing embedding_dimension metadata"
            )


class TestEmbeddingDimensions:
    """Test suite for embedding dimensions consistency."""

    def test_consistent_dimensions(self, sample_chunks_with_embeddings):
        """Test that all embeddings have the same dimension."""
        dimensions = set()
        
        for chunk in sample_chunks_with_embeddings:
            embedding = chunk.get("embedding", [])
            dimensions.add(len(embedding))
        
        assert len(dimensions) == 1, (
            f"Inconsistent embedding dimensions found: {dimensions}"
        )

    def test_expected_dimension(self, sample_chunks_with_embeddings):
        """Test that embedding dimension matches expected value."""
        if not sample_chunks_with_embeddings:
            pytest.skip("No chunks available")
        
        first_chunk = sample_chunks_with_embeddings[0]
        embedding = first_chunk.get("embedding", [])
        expected_dim = first_chunk.get("embedding_dimension", 384)
        
        assert len(embedding) == expected_dim, (
            f"Embedding dimension {len(embedding)} doesn't match "
            f"expected {expected_dim}"
        )

    def test_dimension_matches_model(self, embedder, sample_chunks_with_embeddings):
        """Test that embedding dimension matches the model's output."""
        if not sample_chunks_with_embeddings:
            pytest.skip("No chunks available")
        
        first_chunk = sample_chunks_with_embeddings[0]
        embedding = first_chunk.get("embedding", [])
        
        assert len(embedding) == embedder.embedding_dimension, (
            f"Embedding dimension {len(embedding)} doesn't match "
            f"model dimension {embedder.embedding_dimension}"
        )


class TestEmbeddingValidity:
    """Test suite for embedding value validity."""

    def test_no_nan_values(self, sample_chunks_with_embeddings):
        """Test that embeddings don't contain NaN values."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            assert not np.isnan(embedding_array).any(), (
                f"Chunk {i} embedding contains NaN values"
            )

    def test_no_infinite_values(self, sample_chunks_with_embeddings):
        """Test that embeddings don't contain infinite values."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            assert not np.isinf(embedding_array).any(), (
                f"Chunk {i} embedding contains infinite values"
            )

    def test_not_all_zeros(self, sample_chunks_with_embeddings):
        """Test that embeddings are not all zeros."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            assert not np.all(embedding_array == 0), (
                f"Chunk {i} embedding is all zeros"
            )

    def test_reasonable_value_range(self, sample_chunks_with_embeddings):
        """Test that embedding values are in reasonable range."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            # For normalized embeddings, values should be between -1 and 1
            # For non-normalized, should be reasonable (e.g., -10 to 10)
            max_value = np.max(np.abs(embedding_array))
            assert max_value <= 10, (
                f"Chunk {i} embedding has unreasonably large values: {max_value}"
            )

    def test_non_uniform_values(self, sample_chunks_with_embeddings):
        """Test that embeddings have varied values (not all same)."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            # Check that not all values are the same
            unique_values = np.unique(embedding_array)
            assert len(unique_values) > 1, (
                f"Chunk {i} embedding has all identical values"
            )


class TestEmbeddingNormalization:
    """Test suite for embedding normalization."""

    def test_embeddings_normalized(self, sample_chunks_with_embeddings):
        """Test that embeddings are normalized (if normalization is enabled)."""
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_array = np.array(embedding)
            
            # Calculate L2 norm
            norm = np.linalg.norm(embedding_array)
            
            # For normalized embeddings, norm should be close to 1
            # Allow some floating point tolerance
            if chunk.get("normalized", True):
                assert abs(norm - 1.0) < 0.01, (
                    f"Chunk {i} embedding not normalized: norm = {norm}"
                )


class TestEmbeddingSimilarity:
    """Test suite for embedding similarity properties."""

    def test_similar_content_similar_embeddings(self, embedder):
        """Test that similar content produces similar embeddings."""
        # Create similar content
        text1 = "The expense ratio of the fund is 1.5 percent"
        text2 = "The fund's expense ratio is 1.5%"
        text3 = "Minimum SIP amount is Rs. 500"
        
        # Generate embeddings
        emb1 = embedder.generate_embedding(text1)
        emb2 = embedder.generate_embedding(text2)
        emb3 = embedder.generate_embedding(text3)
        
        # Calculate similarities
        sim_12 = embedder.compute_similarity(emb1, emb2)
        sim_13 = embedder.compute_similarity(emb1, emb3)
        
        # Similar texts should have higher similarity
        assert sim_12 > sim_13, (
            f"Similar texts should have higher similarity: "
            f"sim(1,2)={sim_12:.3f} vs sim(1,3)={sim_13:.3f}"
        )
        
        # Similar texts should have high similarity (>0.7)
        assert sim_12 > 0.7, (
            f"Similar texts should have similarity > 0.7: {sim_12:.3f}"
        )

    def test_different_content_different_embeddings(self, embedder):
        """Test that different content produces different embeddings."""
        # Create different content
        text1 = "Expense ratio is 1.5%"
        text2 = "Minimum SIP amount is Rs. 500"
        
        # Generate embeddings
        emb1 = embedder.generate_embedding(text1)
        emb2 = embedder.generate_embedding(text2)
        
        # Embeddings should be different
        assert not np.array_equal(emb1, emb2), (
            "Different texts should produce different embeddings"
        )
        
        # Similarity should be moderate to low
        similarity = embedder.compute_similarity(emb1, emb2)
        assert similarity < 0.9, (
            f"Different texts should have lower similarity: {similarity:.3f}"
        )

    def test_identical_content_identical_embeddings(self, embedder):
        """Test that identical content produces identical embeddings."""
        text = "HDFC Equity Fund has an expense ratio of 1.5%"
        
        # Generate embeddings twice
        emb1 = embedder.generate_embedding(text)
        emb2 = embedder.generate_embedding(text)
        
        # Should be very similar (allowing for floating point precision)
        similarity = embedder.compute_similarity(emb1, emb2)
        assert similarity > 0.999, (
            f"Identical texts should have similarity > 0.999: {similarity:.3f}"
        )


class TestEmbeddingConsistency:
    """Test suite for embedding consistency."""

    def test_embedding_reproducibility(self, embedder):
        """Test that embeddings are reproducible."""
        text = "Test content for reproducibility"
        
        # Generate embeddings multiple times
        embeddings = [embedder.generate_embedding(text) for _ in range(3)]
        
        # All should be very similar
        for i in range(len(embeddings) - 1):
            similarity = embedder.compute_similarity(
                embeddings[i], embeddings[i + 1]
            )
            assert similarity > 0.999, (
                f"Embeddings not reproducible: similarity = {similarity:.3f}"
            )

    def test_model_consistency(self, sample_chunks_with_embeddings):
        """Test that all embeddings use the same model."""
        models = set()
        
        for chunk in sample_chunks_with_embeddings:
            model = chunk.get("embedding_model")
            if model:
                models.add(model)
        
        assert len(models) <= 1, (
            f"Multiple embedding models found: {models}"
        )


class TestEmbeddingQuality:
    """Test suite for overall embedding quality."""

    def test_embedding_distribution(self, sample_chunks_with_embeddings):
        """Test that embeddings have good statistical distribution."""
        if len(sample_chunks_with_embeddings) < 10:
            pytest.skip("Need at least 10 chunks for distribution test")
        
        embeddings = []
        for chunk in sample_chunks_with_embeddings[:100]:  # Test first 100
            embedding = chunk.get("embedding", [])
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings)
        
        # Check mean is close to 0 (for normalized embeddings)
        mean = np.mean(embeddings_array)
        assert abs(mean) < 0.5, (
            f"Embedding mean too far from 0: {mean}"
        )
        
        # Check standard deviation is reasonable
        std = np.std(embeddings_array)
        assert 0.1 < std < 1.0, (
            f"Embedding std deviation out of range: {std}"
        )

    def test_embedding_variance(self, sample_chunks_with_embeddings):
        """Test that embeddings have sufficient variance."""
        if len(sample_chunks_with_embeddings) < 5:
            pytest.skip("Need at least 5 chunks for variance test")
        
        embeddings = []
        for chunk in sample_chunks_with_embeddings[:50]:
            embedding = chunk.get("embedding", [])
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings)
        
        # Check variance per dimension
        variance = np.var(embeddings_array, axis=0)
        
        # Most dimensions should have non-zero variance
        non_zero_variance = np.sum(variance > 0.001)
        ratio = non_zero_variance / len(variance)
        
        assert ratio > 0.8, (
            f"Only {ratio:.1%} of dimensions have variance > 0.001"
        )

    def test_no_duplicate_embeddings(self, sample_chunks_with_embeddings):
        """Test that there are no identical embeddings (unlikely for real content)."""
        if len(sample_chunks_with_embeddings) < 2:
            pytest.skip("Need at least 2 chunks")
        
        seen_embeddings = set()
        duplicates = []
        
        for i, chunk in enumerate(sample_chunks_with_embeddings):
            embedding = chunk.get("embedding", [])
            embedding_tuple = tuple(embedding)
            
            if embedding_tuple in seen_embeddings:
                duplicates.append(i)
            else:
                seen_embeddings.add(embedding_tuple)
        
        # Allow a few duplicates (might be legitimate for very similar content)
        duplicate_ratio = len(duplicates) / len(sample_chunks_with_embeddings)
        assert duplicate_ratio < 0.05, (
            f"Too many duplicate embeddings: {duplicate_ratio:.1%}"
        )


class TestEmbeddingPerformance:
    """Test suite for embedding performance characteristics."""

    def test_batch_generation_consistency(self, embedder):
        """Test that batch generation produces same results as individual."""
        texts = [
            "Test content one",
            "Test content two",
            "Test content three",
        ]
        
        # Generate individually
        individual_embeddings = [embedder.generate_embedding(text) for text in texts]
        
        # Generate in batch
        batch_embeddings = embedder.generate_embeddings_batch(texts)
        
        # Compare
        for i in range(len(texts)):
            similarity = embedder.compute_similarity(
                individual_embeddings[i],
                batch_embeddings[i]
            )
            assert similarity > 0.999, (
                f"Batch embedding {i} differs from individual: "
                f"similarity = {similarity:.3f}"
            )

    def test_empty_text_handling(self, embedder):
        """Test that empty text is handled gracefully."""
        embedding = embedder.generate_embedding("")
        
        # Should still produce an embedding
        assert len(embedding) == embedder.embedding_dimension
        assert not np.isnan(embedding).any()


def test_embedding_integration():
    """Integration test for complete embedding workflow."""
    # Create embedder
    embedder = EmbeddingGenerator()
    
    # Create sample chunks
    chunks = [
        {
            "chunk_id": f"test-{i}",
            "content": f"Test content about mutual funds {i}",
            "source_url": f"https://example.com/{i}",
        }
        for i in range(10)
    ]
    
    # Generate embeddings
    chunks_with_embeddings = embedder.embed_chunks(chunks)
    
    # Validate
    assert len(chunks_with_embeddings) == 10
    
    for chunk in chunks_with_embeddings:
        assert "embedding" in chunk
        assert "embedding_model" in chunk
        assert "embedding_dimension" in chunk
        
        embedding = chunk["embedding"]
        assert len(embedding) == embedder.embedding_dimension
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

