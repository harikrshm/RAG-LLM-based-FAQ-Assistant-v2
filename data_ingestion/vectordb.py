"""
Vector Database Module

This module sets up and manages the ChromaDB vector database for storing
and retrieving document chunks with embeddings.
"""

import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Manages ChromaDB vector database operations.
    """

    def __init__(
        self,
        persist_directory: str = "./data/vectordb",
        collection_name: str = "mutual_funds_faq",
    ):
        """
        Initialize the vector database.

        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB in {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Get or create collection
        self.collection = self._get_or_create_collection()
        logger.info(f"Collection '{collection_name}' ready")

    def _get_or_create_collection(self):
        """
        Get existing collection or create a new one.

        Returns:
            ChromaDB collection
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except Exception:
            # Create new collection
            logger.info(f"Creating new collection: {self.collection_name}")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Mutual Funds FAQ Assistant Knowledge Base",
                    "hnsw:space": "cosine",  # Use cosine similarity
                },
            )

        return collection

    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add chunks with embeddings to the vector database.

        Args:
            chunks: List of chunk dictionaries with content, embeddings, and metadata
        """
        logger.info(f"Adding {len(chunks)} chunks to vector database")

        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            try:
                # Prepare ID
                chunk_id = chunk.get("chunk_id", f"chunk-{i}")
                ids.append(chunk_id)

                # Prepare embedding
                embedding = chunk.get("embedding")
                if embedding is None:
                    logger.warning(f"Chunk {chunk_id} missing embedding, skipping")
                    continue
                embeddings.append(embedding)

                # Prepare document text
                content = chunk.get("content", "")
                documents.append(content)

                # Prepare metadata (ChromaDB requires string or numeric values)
                metadata = self._prepare_metadata(chunk)
                metadatas.append(metadata)

            except Exception as e:
                logger.error(f"Error preparing chunk {i}: {e}")
                continue

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            try:
                self.collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                )
                logger.debug(f"Added batch {i // batch_size + 1}")
            except Exception as e:
                logger.error(f"Error adding batch {i // batch_size + 1}: {e}")

        logger.info(f"Successfully added chunks to database")

    def _prepare_metadata(self, chunk: Dict) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB (only string and numeric values allowed).

        Args:
            chunk: Chunk dictionary

        Returns:
            Cleaned metadata dictionary
        """
        metadata = {}

        # Source URL
        if "source_url" in chunk:
            metadata["source_url"] = str(chunk["source_url"])

        # Chunk index
        if "chunk_index" in chunk:
            metadata["chunk_index"] = int(chunk["chunk_index"])

        # Content length
        if "content" in chunk:
            metadata["content_length"] = len(chunk["content"])

        # AMC information from nested metadata
        chunk_metadata = chunk.get("metadata", {})
        if "amc_name" in chunk_metadata:
            metadata["amc_name"] = str(chunk_metadata["amc_name"])
        if "amc_id" in chunk_metadata:
            metadata["amc_id"] = str(chunk_metadata["amc_id"])
        if "title" in chunk_metadata:
            metadata["title"] = str(chunk_metadata["title"])

        # Structured info (convert to JSON string)
        if "structured_info" in chunk_metadata:
            structured_info = chunk_metadata["structured_info"]
            if structured_info:
                # Store as JSON string
                metadata["structured_info_json"] = json.dumps(structured_info)

                # Also store individual fields
                for key, value in structured_info.items():
                    metadata[f"info_{key}"] = str(value)

        return metadata

    def query(
        self,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None,
    ) -> Dict:
        """
        Query the vector database.

        Args:
            query_text: Query text (used if query_embedding not provided)
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filters
            where_document: Document content filters

        Returns:
            Query results dictionary
        """
        try:
            if query_embedding:
                # Query with embedding
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where,
                    where_document=where_document,
                )
            else:
                # Query with text (ChromaDB will embed it)
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where,
                    where_document=where_document,
                )

            return results

        except Exception as e:
            logger.error(f"Error querying database: {e}")
            raise

    def get_by_id(self, chunk_ids: List[str]) -> Dict:
        """
        Get chunks by their IDs.

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            Retrieved chunks
        """
        try:
            results = self.collection.get(ids=chunk_ids, include=["documents", "metadatas", "embeddings"])
            return results
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise

    def filter_by_metadata(self, filters: Dict, n_results: int = 10) -> Dict:
        """
        Filter chunks by metadata.

        Args:
            filters: Metadata filters (e.g., {"amc_name": "HDFC"})
            n_results: Maximum number of results

        Returns:
            Filtered chunks
        """
        try:
            results = self.collection.get(
                where=filters,
                limit=n_results,
                include=["documents", "metadatas"],
            )
            return results
        except Exception as e:
            logger.error(f"Error filtering by metadata: {e}")
            raise

    def count(self) -> int:
        """
        Get the number of chunks in the database.

        Returns:
            Number of chunks
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting chunks: {e}")
            return 0

    def delete_collection(self) -> None:
        """
        Delete the entire collection.
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def reset(self) -> None:
        """
        Reset the database (delete and recreate collection).
        """
        try:
            self.delete_collection()
            self.collection = self._get_or_create_collection()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection.

        Returns:
            Collection information
        """
        try:
            count = self.count()
            metadata = self.collection.metadata

            return {
                "name": self.collection_name,
                "count": count,
                "metadata": metadata,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


def main():
    """Main function for testing vector database."""
    import json

    # Initialize vector database
    vectordb = VectorDatabase(
        persist_directory="./data/vectordb",
        collection_name="mutual_funds_faq",
    )

    # Load chunks with embeddings
    try:
        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        logger.error("Chunks with embeddings file not found. Run embedder first.")
        return

    # Add chunks to database
    vectordb.add_chunks(chunks)

    # Get collection info
    info = vectordb.get_collection_info()
    print("\nVector Database Info:")
    print(f"Collection: {info['name']}")
    print(f"Total chunks: {info['count']}")
    print(f"Persist directory: {info['persist_directory']}")

    # Test query
    if info['count'] > 0:
        query_text = "What is the expense ratio?"
        print(f"\nTesting query: '{query_text}'")

        results = vectordb.query(query_text, n_results=3)

        print("\nTop 3 results:")
        for i, (doc, metadata, distance) in enumerate(
            zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ):
            print(f"\n{i+1}. Distance: {distance:.4f}")
            print(f"   AMC: {metadata.get('amc_name', 'Unknown')}")
            print(f"   Source: {metadata.get('source_url', 'Unknown')}")
            print(f"   Content: {doc[:100]}...")

        # Test metadata filtering
        print("\n\nTesting metadata filtering (HDFC funds):")
        filtered = vectordb.filter_by_metadata({"amc_name": "HDFC Mutual Fund"}, n_results=2)

        if filtered["ids"]:
            print(f"Found {len(filtered['ids'])} HDFC chunks")
            for i, (doc, metadata) in enumerate(zip(filtered["documents"], filtered["metadatas"])):
                print(f"\n{i+1}. {metadata.get('title', 'Unknown')}")
                print(f"   Content: {doc[:100]}...")


if __name__ == "__main__":
    main()

