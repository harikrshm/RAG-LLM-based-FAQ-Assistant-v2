"""
Text Chunking Module

This module implements various text chunking strategies for preparing content
for vector embedding and retrieval.
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    content: str
    chunk_id: str
    source_url: str
    chunk_index: int
    metadata: Dict
    overlap_with_previous: Optional[str] = None
    overlap_with_next: Optional[str] = None


class TextChunker:
    """
    Implements various text chunking strategies.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        chunking_strategy: str = "sentence",
        min_chunk_size: int = 100,
    ):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Number of characters to overlap between chunks
            chunking_strategy: Strategy to use ('sentence', 'paragraph', 'semantic', 'fixed')
            min_chunk_size: Minimum chunk size (discard smaller chunks)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunking_strategy = chunking_strategy
        self.min_chunk_size = min_chunk_size

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """
        Chunk text using the configured strategy.

        Args:
            text: Text content to chunk
            metadata: Metadata for the text

        Returns:
            List of TextChunk objects
        """
        metadata = metadata or {}

        # Select chunking strategy
        if self.chunking_strategy == "sentence":
            chunks = self._chunk_by_sentence(text)
        elif self.chunking_strategy == "paragraph":
            chunks = self._chunk_by_paragraph(text)
        elif self.chunking_strategy == "semantic":
            chunks = self._chunk_semantically(text)
        elif self.chunking_strategy == "fixed":
            chunks = self._chunk_fixed_size(text)
        else:
            logger.warning(f"Unknown strategy '{self.chunking_strategy}', using sentence-based")
            chunks = self._chunk_by_sentence(text)

        # Filter short chunks
        chunks = [c for c in chunks if len(c) >= self.min_chunk_size]

        # Create TextChunk objects with metadata
        text_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = TextChunk(
                content=chunk_text,
                chunk_id=f"{metadata.get('url', 'unknown')}#chunk-{i}",
                source_url=metadata.get("url", ""),
                chunk_index=i,
                metadata=metadata,
            )
            text_chunks.append(chunk)

        # Add overlap information
        for i in range(len(text_chunks)):
            if i > 0:
                text_chunks[i].overlap_with_previous = self._get_overlap(
                    text_chunks[i - 1].content, text_chunks[i].content
                )
            if i < len(text_chunks) - 1:
                text_chunks[i].overlap_with_next = self._get_overlap(
                    text_chunks[i].content, text_chunks[i + 1].content
                )

        logger.debug(f"Created {len(text_chunks)} chunks from text")
        return text_chunks

    def _chunk_by_sentence(self, text: str) -> List[str]:
        """
        Chunk text by sentences, respecting chunk size and overlap.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # Split into sentences
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # If adding this sentence exceeds chunk size, save current chunk
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = self._get_overlap_sentences(current_chunk)
                current_chunk = [overlap_text] if overlap_text else []
                current_size = len(overlap_text)

            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 for space

        # Add last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _chunk_by_paragraph(self, text: str) -> List[str]:
        """
        Chunk text by paragraphs.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # Split into paragraphs
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_size = 0

        for paragraph in paragraphs:
            para_size = len(paragraph)

            # If paragraph alone exceeds chunk size, split it further
            if para_size > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

                # Split large paragraph by sentences
                para_chunks = self._chunk_by_sentence(paragraph)
                chunks.extend(para_chunks)
            else:
                # If adding this paragraph exceeds chunk size, save current chunk
                if current_size + para_size > self.chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

                current_chunk.append(paragraph)
                current_size += para_size + 2  # +2 for \n\n

        # Add last chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _chunk_semantically(self, text: str) -> List[str]:
        """
        Chunk text semantically (by topics/sections).

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # Look for section headers and topic changes
        sections = self._identify_sections(text)

        if len(sections) > 1:
            chunks = []
            for section in sections:
                # If section is too large, split it further
                if len(section) > self.chunk_size * 1.5:
                    section_chunks = self._chunk_by_paragraph(section)
                    chunks.extend(section_chunks)
                else:
                    chunks.append(section)
            return chunks
        else:
            # Fall back to paragraph-based chunking
            return self._chunk_by_paragraph(text)

    def _chunk_fixed_size(self, text: str) -> List[str]:
        """
        Chunk text into fixed-size chunks with overlap.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at sentence or word boundary
            if end < text_length:
                # Look for sentence end
                last_period = chunk.rfind(". ")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > self.chunk_size // 2:
                    chunk = chunk[: break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - self.chunk_overlap

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLTK or spaCy)
        # Handle common abbreviations
        text = re.sub(r"\bMr\.", "Mr", text)
        text = re.sub(r"\bMrs\.", "Mrs", text)
        text = re.sub(r"\bDr\.", "Dr", text)
        text = re.sub(r"\bRs\.", "Rs", text)

        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _identify_sections(self, text: str) -> List[str]:
        """
        Identify sections in text based on headers and topic changes.

        Args:
            text: Text to analyze

        Returns:
            List of text sections
        """
        # Look for common section headers
        section_pattern = r"^([A-Z][A-Za-z\s]+):?\n"
        parts = re.split(section_pattern, text, flags=re.MULTILINE)

        if len(parts) <= 1:
            return [text]

        sections = []
        current_section = ""

        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Content part
                current_section += part
            else:
                # Header part
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = part + "\n"

        # Add last section
        if current_section.strip():
            sections.append(current_section.strip())

        return sections

    def _get_overlap_sentences(self, sentences: List[str]) -> str:
        """
        Get overlap text from the end of a chunk.

        Args:
            sentences: List of sentences in the chunk

        Returns:
            Overlap text
        """
        overlap_text = ""
        overlap_size = 0

        # Take sentences from the end until we reach overlap size
        for sentence in reversed(sentences):
            if overlap_size + len(sentence) > self.chunk_overlap:
                break
            overlap_text = sentence + " " + overlap_text
            overlap_size += len(sentence) + 1

        return overlap_text.strip()

    def _get_overlap(self, text1: str, text2: str) -> str:
        """
        Find overlapping text between two chunks.

        Args:
            text1: First text chunk
            text2: Second text chunk

        Returns:
            Overlapping text
        """
        # Find longest common substring at the end of text1 and start of text2
        min_length = min(len(text1), len(text2), self.chunk_overlap)

        for length in range(min_length, 0, -1):
            end_of_text1 = text1[-length:]
            start_of_text2 = text2[:length]

            if end_of_text1 == start_of_text2:
                return end_of_text1

        return ""

    def process_documents(self, documents: List[Dict]) -> List[TextChunk]:
        """
        Process multiple documents and create chunks.

        Args:
            documents: List of processed document dictionaries

        Returns:
            List of TextChunk objects
        """
        logger.info(f"Chunking {len(documents)} documents")

        all_chunks = []

        for i, doc in enumerate(documents):
            try:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})

                # Add structured info to metadata
                if "structured_info" in doc:
                    metadata["structured_info"] = doc["structured_info"]

                # Create chunks
                chunks = self.chunk_text(content, metadata)
                all_chunks.extend(chunks)

                if (i + 1) % 10 == 0:
                    logger.info(f"Chunked {i + 1}/{len(documents)} documents")

            except Exception as e:
                logger.error(f"Error chunking document {i}: {e}")
                continue

        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks


def main():
    """Main function for testing chunker."""
    import json

    # Initialize chunker
    chunker = TextChunker(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="sentence",
        min_chunk_size=100,
    )

    # Load processed content
    try:
        with open("data/processed_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            processed_docs = data.get("processed_documents", [])
    except FileNotFoundError:
        logger.error("Processed content file not found. Run processor first.")
        return

    # Create chunks
    chunks = chunker.process_documents(processed_docs)

    # Save chunks
    chunks_data = [
        {
            "content": chunk.content,
            "chunk_id": chunk.chunk_id,
            "source_url": chunk.source_url,
            "chunk_index": chunk.chunk_index,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]

    output_data = {
        "chunks": chunks_data,
        "metadata": {
            "total_chunks": len(chunks),
            "chunking_strategy": chunker.chunking_strategy,
            "chunk_size": chunker.chunk_size,
            "chunk_overlap": chunker.chunk_overlap,
        },
    }

    with open("data/chunks.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(chunks)} chunks")

    # Print statistics
    print("\nChunking Statistics:")
    print(f"Total chunks: {len(chunks)}")
    print(f"Average chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")
    print(f"Strategy: {chunker.chunking_strategy}")

    # Show sample chunks
    if chunks:
        print("\nSample chunks:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Source: {chunk.source_url}")
            print(f"  Size: {len(chunk.content)} chars")
            print(f"  Preview: {chunk.content[:150]}...")


if __name__ == "__main__":
    main()

