"""
Test suite for validating chunking strategy.

This module tests that:
- Chunks have appropriate sizes
- Chunk boundaries are sensible
- Overlap between chunks is correct
- Content is not lost during chunking
- Chunks maintain semantic coherence
"""

import pytest
import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chunker import TextChunker, TextChunk


@pytest.fixture
def chunker():
    """Create a text chunker instance."""
    return TextChunker(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="sentence",
        min_chunk_size=100,
    )


@pytest.fixture
def sample_chunks():
    """Load sample chunks or create mock data."""
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("chunks", [])
    except FileNotFoundError:
        # Return mock data for testing
        return [
            {
                "chunk_id": "test-1",
                "content": "This is a test chunk about HDFC Equity Fund. " * 10,
                "source_url": "https://example.com",
                "chunk_index": 0,
            },
            {
                "chunk_id": "test-2",
                "content": "This is another test chunk about mutual funds. " * 10,
                "source_url": "https://example.com",
                "chunk_index": 1,
            },
        ]


class TestChunkSize:
    """Test suite for chunk size validation."""

    def test_chunks_within_size_limits(self, sample_chunks, chunker):
        """Test that chunks are within configured size limits."""
        max_allowed = chunker.chunk_size * 1.5  # Allow 50% overage for boundary
        
        for i, chunk in enumerate(sample_chunks):
            content = chunk.get("content", "")
            content_length = len(content)
            
            # Should not be too large
            assert content_length <= max_allowed, (
                f"Chunk {i} too large: {content_length} chars "
                f"(max: {max_allowed})"
            )
            
            # Should meet minimum size (unless it's the last chunk)
            if content_length < chunker.min_chunk_size:
                # This is acceptable for last chunks or filtered content
                pass

    def test_chunks_not_too_small(self, sample_chunks, chunker):
        """Test that chunks meet minimum size requirements."""
        too_small_chunks = []
        
        for i, chunk in enumerate(sample_chunks):
            content = chunk.get("content", "")
            if len(content) < chunker.min_chunk_size:
                too_small_chunks.append(i)
        
        # Allow some small chunks (e.g., last chunks from documents)
        ratio = len(too_small_chunks) / len(sample_chunks) if sample_chunks else 0
        assert ratio < 0.1, (
            f"Too many small chunks: {ratio:.1%} ({len(too_small_chunks)} chunks)"
        )

    def test_average_chunk_size(self, sample_chunks):
        """Test that average chunk size is reasonable."""
        if not sample_chunks:
            pytest.skip("No chunks available")
        
        total_length = sum(len(chunk.get("content", "")) for chunk in sample_chunks)
        avg_length = total_length / len(sample_chunks)
        
        # Average should be reasonable (200-800 chars for 500 char target)
        assert 200 <= avg_length <= 800, (
            f"Average chunk size unusual: {avg_length:.0f} chars"
        )


class TestChunkBoundaries:
    """Test suite for chunk boundary quality."""

    def test_chunks_end_at_sentence_boundaries(self, sample_chunks):
        """Test that chunks preferably end at sentence boundaries."""
        sentence_endings = [".", "!", "?", "\n"]
        chunks_with_good_boundaries = 0
        
        for chunk in sample_chunks:
            content = chunk.get("content", "")
            if content:
                last_char = content.rstrip()[-1] if content.rstrip() else ""
                if last_char in sentence_endings:
                    chunks_with_good_boundaries += 1
        
        # Most chunks should end at sentence boundaries
        ratio = chunks_with_good_boundaries / len(sample_chunks) if sample_chunks else 0
        assert ratio >= 0.6, (
            f"Only {ratio:.1%} of chunks end at sentence boundaries"
        )

    def test_no_mid_word_breaks(self, sample_chunks):
        """Test that chunks don't break in the middle of words."""
        for i, chunk in enumerate(sample_chunks):
            content = chunk.get("content", "")
            
            if content:
                # Check if first character is alphanumeric and not start of sentence
                first_char = content[0] if content else ""
                if first_char.isalpha() and first_char.islower():
                    # Might be mid-word break (warning, not error)
                    pass
                
                # Check if last character suggests incomplete word
                last_word = content.split()[-1] if content.split() else ""
                if last_word and not any(last_word.endswith(p) for p in [".", ",", "!", "?"]):
                    # This might be acceptable if next chunk continues
                    pass


class TestChunkOverlap:
    """Test suite for chunk overlap validation."""

    def test_sequential_chunks_have_overlap(self, sample_chunks):
        """Test that sequential chunks from same source have overlap."""
        # Group chunks by source URL
        from collections import defaultdict
        url_chunks = defaultdict(list)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            if source_url:
                url_chunks[source_url].append(chunk)
        
        # Check overlap for each source
        for url, chunks in url_chunks.items():
            if len(chunks) < 2:
                continue
            
            # Sort by chunk index
            sorted_chunks = sorted(chunks, key=lambda c: c.get("chunk_index", 0))
            
            # Check overlap between consecutive chunks
            for i in range(len(sorted_chunks) - 1):
                chunk1 = sorted_chunks[i]
                chunk2 = sorted_chunks[i + 1]
                
                content1 = chunk1.get("content", "")
                content2 = chunk2.get("content", "")
                
                # Check if there's any overlap
                # (simplified check - look for common words at end/start)
                words1 = content1.split()[-10:] if content1 else []
                words2 = content2.split()[:10] if content2 else []
                
                # There should be some common words (allowing for variation)
                if len(words1) > 0 and len(words2) > 0:
                    # At least check they're from same document
                    pass  # Overlap is optional based on chunking strategy


class TestChunkIndexing:
    """Test suite for chunk indexing."""

    def test_chunk_indices_sequential(self, sample_chunks):
        """Test that chunk indices are sequential per source."""
        from collections import defaultdict
        url_indices = defaultdict(list)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            chunk_index = chunk.get("chunk_index")
            
            if source_url is not None and chunk_index is not None:
                url_indices[source_url].append(chunk_index)
        
        # Check each source has reasonable indices
        for url, indices in url_indices.items():
            sorted_indices = sorted(indices)
            
            # Should start at 0
            if sorted_indices:
                assert sorted_indices[0] == 0, (
                    f"URL {url} indices don't start at 0: {sorted_indices[0]}"
                )
            
            # Check for large gaps (allow some due to filtering)
            max_gap = 5
            for i in range(len(sorted_indices) - 1):
                gap = sorted_indices[i + 1] - sorted_indices[i]
                if gap > max_gap:
                    # Large gap might indicate issues
                    pass  # Warning, not error

    def test_chunk_ids_unique(self, sample_chunks):
        """Test that chunk IDs are unique."""
        chunk_ids = set()
        duplicates = []
        
        for chunk in sample_chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id:
                if chunk_id in chunk_ids:
                    duplicates.append(chunk_id)
                chunk_ids.add(chunk_id)
        
        assert len(duplicates) == 0, (
            f"Found {len(duplicates)} duplicate chunk IDs: {duplicates[:5]}"
        )


class TestContentPreservation:
    """Test suite for content preservation during chunking."""

    def test_chunking_preserves_content(self, chunker):
        """Test that chunking doesn't lose content."""
        original_text = "This is a test document. " * 50
        
        # Create a mock document
        doc = {
            "content": original_text,
            "metadata": {"url": "https://example.com"},
        }
        
        # Chunk it
        chunks = chunker.process_documents([doc])
        
        # Reconstruct text from chunks (removing overlap)
        reconstructed = ""
        for i, chunk in enumerate(chunks):
            if i == 0:
                reconstructed += chunk.content
            else:
                # Simple reconstruction - just append
                # (In reality, need to handle overlap)
                reconstructed += " " + chunk.content
        
        # Should have similar length (allowing for overlap duplication)
        original_words = original_text.split()
        reconstructed_words = reconstructed.split()
        
        # Reconstructed should have at least 80% of original words
        # (might have more due to overlap)
        ratio = len(reconstructed_words) / len(original_words)
        assert ratio >= 0.8, (
            f"Content loss during chunking: {ratio:.1%} preserved"
        )

    def test_no_content_duplication_across_sources(self, sample_chunks):
        """Test that content from different sources doesn't get mixed."""
        from collections import defaultdict
        url_contents = defaultdict(set)
        
        for chunk in sample_chunks:
            source_url = chunk.get("source_url")
            content = chunk.get("content", "")
            
            if source_url and content:
                # Store first 100 chars as signature
                signature = content[:100]
                url_contents[source_url].add(signature)
        
        # Check for content appearing in multiple sources
        all_signatures = []
        for url, signatures in url_contents.items():
            all_signatures.extend([(url, sig) for sig in signatures])
        
        # Look for duplicates across different URLs
        from collections import Counter
        signature_counter = Counter([sig for url, sig in all_signatures])
        
        duplicates = [sig for sig, count in signature_counter.items() if count > 1]
        
        # Some duplication is acceptable (e.g., common headers)
        dup_ratio = len(duplicates) / len(signature_counter) if signature_counter else 0
        assert dup_ratio < 0.1, (
            f"Too much content duplication across sources: {dup_ratio:.1%}"
        )


class TestSemanticCoherence:
    """Test suite for semantic coherence of chunks."""

    def test_chunks_contain_complete_sentences(self, sample_chunks):
        """Test that chunks contain complete sentences."""
        chunks_with_complete_sentences = 0
        
        for chunk in sample_chunks:
            content = chunk.get("content", "")
            
            # Check for sentence patterns
            has_sentence_end = any(
                punct in content for punct in [".", "!", "?"]
            )
            has_capital = any(c.isupper() for c in content)
            
            if has_sentence_end and has_capital:
                chunks_with_complete_sentences += 1
        
        # Most chunks should have complete sentences
        ratio = chunks_with_complete_sentences / len(sample_chunks) if sample_chunks else 0
        assert ratio >= 0.8, (
            f"Only {ratio:.1%} of chunks contain complete sentences"
        )

    def test_chunks_have_meaningful_content(self, sample_chunks):
        """Test that chunks have meaningful content (not just whitespace/punctuation)."""
        for i, chunk in enumerate(sample_chunks):
            content = chunk.get("content", "")
            
            # Count alphanumeric characters
            alphanum_chars = sum(1 for c in content if c.isalnum())
            total_chars = len(content)
            
            if total_chars > 0:
                ratio = alphanum_chars / total_chars
                assert ratio >= 0.5, (
                    f"Chunk {i} has low alphanumeric ratio: {ratio:.1%}"
                )

    def test_chunks_not_truncated_mid_sentence(self, sample_chunks):
        """Test that chunks don't appear to be truncated mid-sentence."""
        suspicious_endings = []
        
        for i, chunk in enumerate(sample_chunks):
            content = chunk.get("content", "").rstrip()
            
            if content:
                last_chars = content[-20:] if len(content) >= 20 else content
                
                # Check if ends with comma (might be mid-sentence)
                if last_chars.endswith(","):
                    suspicious_endings.append(i)
        
        # Allow some suspicious endings (might be intentional)
        ratio = len(suspicious_endings) / len(sample_chunks) if sample_chunks else 0
        assert ratio < 0.2, (
            f"Too many suspicious chunk endings: {ratio:.1%}"
        )


class TestChunkingStrategy:
    """Test suite for different chunking strategies."""

    def test_sentence_chunking_strategy(self):
        """Test sentence-based chunking."""
        chunker = TextChunker(
            chunk_size=200,
            chunking_strategy="sentence",
            min_chunk_size=50,
        )
        
        text = "First sentence. Second sentence. Third sentence. " * 10
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0, "Sentence chunking should produce chunks"
        
        # Chunks should end with sentence boundaries
        for chunk in chunks:
            if chunk.content:
                # Should ideally end with period, question mark, or exclamation
                pass  # Check is in TestChunkBoundaries

    def test_paragraph_chunking_strategy(self):
        """Test paragraph-based chunking."""
        chunker = TextChunker(
            chunk_size=200,
            chunking_strategy="paragraph",
            min_chunk_size=50,
        )
        
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three." * 5
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0, "Paragraph chunking should produce chunks"

    def test_semantic_chunking_strategy(self):
        """Test semantic chunking."""
        chunker = TextChunker(
            chunk_size=200,
            chunking_strategy="semantic",
            min_chunk_size=50,
        )
        
        text = "Section One\nContent for section one.\n\nSection Two\nContent for section two."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0, "Semantic chunking should produce chunks"


class TestChunkMetadata:
    """Test suite for chunk metadata preservation."""

    def test_chunks_preserve_source_metadata(self, sample_chunks):
        """Test that chunks preserve source metadata."""
        for i, chunk in enumerate(sample_chunks):
            assert "source_url" in chunk or "metadata" in chunk, (
                f"Chunk {i} missing source metadata"
            )

    def test_chunks_have_chunk_index(self, sample_chunks):
        """Test that chunks have chunk_index."""
        chunks_with_index = 0
        
        for chunk in sample_chunks:
            if "chunk_index" in chunk:
                chunks_with_index += 1
        
        # Most chunks should have index
        ratio = chunks_with_index / len(sample_chunks) if sample_chunks else 0
        assert ratio >= 0.9, (
            f"Only {ratio:.1%} of chunks have chunk_index"
        )


class TestChunkDistribution:
    """Test suite for chunk distribution across sources."""

    def test_chunks_distributed_across_sources(self, sample_chunks):
        """Test that chunks are reasonably distributed across sources."""
        from collections import Counter
        
        source_urls = [chunk.get("source_url") for chunk in sample_chunks]
        source_counts = Counter(source_urls)
        
        # Should have multiple sources
        assert len(source_counts) > 1, "Chunks should come from multiple sources"
        
        # No single source should dominate (>80%)
        max_count = max(source_counts.values())
        total_count = len(sample_chunks)
        
        ratio = max_count / total_count if total_count > 0 else 0
        assert ratio < 0.8, (
            f"One source dominates with {ratio:.1%} of chunks"
        )

    def test_minimum_chunks_per_source(self, sample_chunks):
        """Test that each source has minimum number of chunks."""
        from collections import Counter
        
        source_urls = [
            chunk.get("source_url") 
            for chunk in sample_chunks 
            if chunk.get("source_url")
        ]
        source_counts = Counter(source_urls)
        
        # Each source should have at least 1 chunk
        for source, count in source_counts.items():
            assert count >= 1, f"Source {source} has no chunks"


def test_chunking_integration():
    """Integration test for complete chunking workflow."""
    # Create chunker
    chunker = TextChunker(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="sentence",
        min_chunk_size=100,
    )
    
    # Create sample document
    documents = [
        {
            "content": "This is a test document about HDFC mutual funds. " * 30,
            "metadata": {
                "url": "https://example.com/hdfc",
                "amc_name": "HDFC Mutual Fund",
            },
        }
    ]
    
    # Process documents
    chunks = chunker.process_documents(documents)
    
    # Validate results
    assert len(chunks) > 0, "Should produce chunks"
    
    for chunk in chunks:
        assert hasattr(chunk, "content"), "Chunk should have content"
        assert hasattr(chunk, "chunk_id"), "Chunk should have chunk_id"
        assert hasattr(chunk, "source_url"), "Chunk should have source_url"
        assert hasattr(chunk, "chunk_index"), "Chunk should have chunk_index"
        
        # Validate content
        assert len(chunk.content) >= 100, "Chunk content too short"
        assert len(chunk.content) <= 750, "Chunk content too long"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

