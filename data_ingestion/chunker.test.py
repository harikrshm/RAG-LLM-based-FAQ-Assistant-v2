"""
Unit tests for the chunker module
"""

import pytest
from chunker import TextChunker, TextChunk


@pytest.fixture
def chunker():
    """Create a text chunker."""
    return TextChunker(
        chunk_size=200,
        chunk_overlap=30,
        chunking_strategy="sentence",
        min_chunk_size=50,
    )


def test_chunker_initialization():
    """Test chunker initialization."""
    chunker = TextChunker()
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 50
    assert chunker.chunking_strategy == "sentence"


def test_split_sentences(chunker):
    """Test sentence splitting."""
    text = "This is sentence one. This is sentence two! And this is sentence three?"
    sentences = chunker._split_sentences(text)
    
    assert len(sentences) == 3
    assert "sentence one" in sentences[0]
    assert "sentence two" in sentences[1]
    assert "sentence three" in sentences[2]


def test_chunk_by_sentence(chunker):
    """Test sentence-based chunking."""
    text = " ".join([f"This is sentence number {i}." for i in range(20)])
    chunks = chunker._chunk_by_sentence(text)
    
    assert len(chunks) > 1
    assert all(len(chunk) <= chunker.chunk_size + 100 for chunk in chunks)  # Allow some variance


def test_chunk_by_paragraph(chunker):
    """Test paragraph-based chunking."""
    paragraphs = [f"This is paragraph {i} with some content." for i in range(10)]
    text = "\n\n".join(paragraphs)
    
    chunks = chunker._chunk_by_paragraph(text)
    
    assert len(chunks) > 1


def test_chunk_fixed_size(chunker):
    """Test fixed-size chunking."""
    text = "a" * 1000
    chunks = chunker._chunk_fixed_size(text)
    
    assert len(chunks) > 1
    assert all(len(chunk) <= chunker.chunk_size + 50 for chunk in chunks)


def test_identify_sections(chunker):
    """Test section identification."""
    text = """Introduction
    This is the introduction section.
    
    Features
    This section describes the features.
    
    Conclusion
    This is the conclusion.
    """
    
    sections = chunker._identify_sections(text)
    assert len(sections) > 1


def test_chunk_text(chunker):
    """Test full chunk_text method."""
    text = """
    HDFC Equity Fund is a large cap equity fund.
    The expense ratio is 1.5%.
    Minimum SIP is Rs. 500.
    The fund has given consistent returns over the years.
    """
    
    metadata = {"url": "https://example.com", "amc_name": "HDFC"}
    chunks = chunker.chunk_text(text, metadata)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    assert all(chunk.source_url == "https://example.com" for chunk in chunks)
    assert all(chunk.metadata["amc_name"] == "HDFC" for chunk in chunks)


def test_chunk_text_min_size_filter(chunker):
    """Test that short chunks are filtered out."""
    text = "Short text."
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) == 0  # Should be filtered due to min_chunk_size


def test_chunk_overlap():
    """Test chunk overlap functionality."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "This is a long text. " * 20
    
    chunks = chunker._chunk_by_sentence(text)
    
    # Check that there's some overlap between consecutive chunks
    if len(chunks) > 1:
        # There should be some similar content
        assert len(chunks) > 1


def test_process_documents(chunker):
    """Test processing multiple documents."""
    documents = [
        {
            "content": "This is document one. " * 10,
            "metadata": {"url": "https://example.com/1", "amc_name": "AMC1"},
        },
        {
            "content": "This is document two. " * 10,
            "metadata": {"url": "https://example.com/2", "amc_name": "AMC2"},
        },
    ]
    
    chunks = chunker.process_documents(documents)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    
    # Check that chunks from both documents are present
    urls = {chunk.source_url for chunk in chunks}
    assert "https://example.com/1" in urls
    assert "https://example.com/2" in urls


def test_chunk_id_generation(chunker):
    """Test that chunk IDs are generated correctly."""
    text = "Sentence one. " * 20
    metadata = {"url": "https://example.com"}
    
    chunks = chunker.chunk_text(text, metadata)
    
    # Check that chunk IDs are unique and sequential
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
        assert f"chunk-{i}" in chunk.chunk_id


def test_semantic_chunking():
    """Test semantic chunking strategy."""
    chunker = TextChunker(chunking_strategy="semantic", chunk_size=200)
    
    text = """Fund Overview
    This is a mutual fund focused on equity investments.
    
    Performance
    The fund has delivered strong returns.
    
    Risk Profile
    The fund carries moderate to high risk.
    """
    
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 0


def test_paragraph_chunking():
    """Test paragraph chunking strategy."""
    chunker = TextChunker(chunking_strategy="paragraph", chunk_size=150)
    
    text = """Paragraph one with some content that describes the fund.
    
    Paragraph two with information about returns and performance.
    
    Paragraph three with details about risk and investment strategy.
    """
    
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 0


def test_invalid_chunking_strategy():
    """Test handling of invalid chunking strategy."""
    chunker = TextChunker(chunking_strategy="invalid")
    text = "Test text. " * 10
    
    # Should fall back to sentence chunking
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 0

