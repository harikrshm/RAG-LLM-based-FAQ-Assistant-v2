"""
Vector Embedding Generation Module

This module generates vector embeddings from text chunks using sentence transformers.
"""

import logging
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates vector embeddings using sentence transformers.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 32,
        normalize_embeddings: bool = True,
    ):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence transformer model to use
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to normalize embeddings to unit length
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings

        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(
                f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}"
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed

        Returns:
            Array of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=True,
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of chunk dictionaries with 'content' field

        Returns:
            List of chunks with added 'embedding' field
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        # Extract text content
        texts = [chunk.get("content", "") for chunk in chunks]

        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(texts)

        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()  # Convert to list for JSON serialization
            chunk["embedding_model"] = self.model_name
            chunk["embedding_dimension"] = self.embedding_dimension

        logger.info(f"Successfully generated embeddings for {len(chunks)} chunks")
        return chunks

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        # Normalize if not already normalized
        if not self.normalize_embeddings:
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)

        similarity = np.dot(embedding1, embedding2)
        return float(similarity)

    def find_similar_chunks(
        self, query: str, chunk_embeddings: List[Dict], top_k: int = 5
    ) -> List[Dict]:
        """
        Find most similar chunks to a query.

        Args:
            query: Query text
            chunk_embeddings: List of chunks with embeddings
            top_k: Number of top results to return

        Returns:
            List of top k similar chunks with similarity scores
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Compute similarities
        similarities = []
        for chunk in chunk_embeddings:
            chunk_embedding = np.array(chunk["embedding"])
            similarity = self.compute_similarity(query_embedding, chunk_embedding)
            similarities.append((chunk, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [
            {"chunk": chunk, "similarity_score": score}
            for chunk, score in similarities[:top_k]
        ]

        return results

    def get_model_info(self) -> Dict:
        """
        Get information about the embedding model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "batch_size": self.batch_size,
            "normalize_embeddings": self.normalize_embeddings,
        }


def main():
    """Main function for testing embedder."""
    import json

    # Initialize embedder
    embedder = EmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",
        batch_size=32,
        normalize_embeddings=True,
    )

    # Load chunks
    try:
        with open("data/chunks.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        logger.error("Chunks file not found. Run chunker first.")
        return

    # Generate embeddings
    chunks_with_embeddings = embedder.embed_chunks(chunks)

    # Save chunks with embeddings
    output_data = {
        "chunks": chunks_with_embeddings,
        "metadata": {
            "total_chunks": len(chunks_with_embeddings),
            "embedding_model": embedder.model_name,
            "embedding_dimension": embedder.embedding_dimension,
        },
    }

    with open("data/chunks_with_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(chunks_with_embeddings)} chunks with embeddings")

    # Print statistics
    print("\nEmbedding Statistics:")
    print(f"Total chunks: {len(chunks_with_embeddings)}")
    print(f"Model: {embedder.model_name}")
    print(f"Embedding dimension: {embedder.embedding_dimension}")

    # Test similarity search
    if chunks_with_embeddings:
        query = "What is the expense ratio?"
        print(f"\nTesting similarity search for query: '{query}'")

        similar_chunks = embedder.find_similar_chunks(
            query, chunks_with_embeddings, top_k=3
        )

        print("\nTop 3 similar chunks:")
        for i, result in enumerate(similar_chunks):
            chunk = result["chunk"]
            score = result["similarity_score"]
            content_preview = chunk["content"][:100]
            print(f"\n{i+1}. Similarity: {score:.4f}")
            print(f"   Source: {chunk.get('source_url', 'Unknown')}")
            print(f"   Content: {content_preview}...")


if __name__ == "__main__":
    main()

